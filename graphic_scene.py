from PyQt5.QtWidgets import QGraphicsScene, QMessageBox
from bar import Bar
from loads import Сoncentrated_loads, Distributed_loads
from bar_info import BarInfo, BarNum
from chekbox_group import BarCheckBox


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars = []
        self.current_x = 0
        self.max_width = 1000
        self.max_height = 150
        self.parent = parent
        self.left_checkbox = BarCheckBox()
        self.right_checkbox = BarCheckBox(direction="Right")
        self.loading_from_file = False

    def update_scene(self, info):
        if not info:
            return
        self.clear()
        self.current_x = 0
        self.bars.clear()
        self.update_bar(info["Стержни"])
        if len(self.bars) <= 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Предупреждение")
            msg.setText(f"Стержни отсутсвуют")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return
        else:
            self.update_сoncentrated_loads(info["Сосредоточенные нагрузки"])
            self.update_distributed_loads(info["Распределенные нагрузки"])
        self.update_checkbox("Left")
        self.update_checkbox("Right")


    def update_checkbox(self, side):
        if not self.bars:
            return
        if side == "Left":
            first_bar = self.bars[0]
            left_x = first_bar.x - 30
            left_y = first_bar.y
            self.left_checkbox = BarCheckBox(left_x, left_y, first_bar.scaled_height)
            self.addItem(self.left_checkbox)
            if not self.parent.checkbox.left_checkbox.isChecked():
                self.left_checkbox.hide()
        elif side == "Right":
            last_bar = self.bars[-1]
            right_x = last_bar.x + last_bar.scaled_width
            right_y = last_bar.y
            self.right_checkbox = BarCheckBox(right_x, right_y, last_bar.scaled_height, direction="Right")
            self.addItem(self.right_checkbox)
            if not self.parent.checkbox.right_checkbox.isChecked():
                self.right_checkbox.hide()


    def update_bar(self, bar_info):
        if not bar_info:
            return
        scaled_bar = self.bar_scaling(bar_info)
        for i, (scaled_width, scaled_height) in enumerate(scaled_bar):
            real_width = bar_info[i][0]
            real_height = bar_info[i][1]
            x = self.current_x
            y = -scaled_height / 2
            draw_bar = Bar(x, y, real_width, real_height, scaled_width, scaled_height)
            self.bars.append(draw_bar)
            self.addItem(draw_bar)
            self.current_x += scaled_width
            info = BarInfo(x - 10, y + scaled_height, real_width, scaled_width, i + 1,
                           (self.max_height - scaled_height) // 2)
            self.addItem(info)
            bar_number = BarNum(i + 1, x + scaled_width // 2, y - 60)
            self.addItem(bar_number)

    def update_сoncentrated_loads(self, loads_info): # noqa
        if not loads_info or not self.bars:
            return
        busy_nodes = []
        for loads in loads_info:
            force = loads[1]
            node_number = loads[0] - 1
            if node_number in busy_nodes:
                if not self.loading_from_file:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText(f"На узел {node_number + 1} уже наложена сила!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    break
            if 0 <= node_number <= len(self.bars):
                if node_number == len(self.bars):
                    x = self.bars[-1].x + self.bars[-1].scaled_width
                else:
                    x = self.bars[node_number].x
                y = 0
                draw_load = Сoncentrated_loads(x, y, force)
                self.addItem(draw_load)
                busy_nodes.append(node_number)
            else:
                if not self.loading_from_file:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText(f"Такого узла не существует!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    break

    def update_distributed_loads(self, loads_info):
        if not loads_info or not self.bars:
            return
        busy_bar = []
        for loads in loads_info:
            force = loads[1]
            bar_number = loads[0] - 1
            if bar_number in busy_bar:
                if not self.loading_from_file:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText(f"На стержень {bar_number + 1} уже наложена сила!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    break
            if 0 <= bar_number < len(self.bars):
                x = self.bars[bar_number].x
                width = self.bars[bar_number].scaled_width
                y = 0
                draw_load = Distributed_loads(x, y, width, force)
                self.addItem(draw_load)
                busy_bar.append(bar_number)
            else:
                if not self.loading_from_file:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Предупреждение")
                    msg.setText(f"Такого стержня не существует!")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    break

    def bar_scaling(self, bar_info):
        self.max_width = self.parent.viewport().width() - 200
        all_width = [bar[0] for bar in bar_info]
        all_height = [bar[1] for bar in bar_info]
        sum_width = sum(all_width)
        scale_for_width = self.max_width / sum_width
        scaled_width = [width * scale_for_width for width in all_width]
        max_height = max(all_height)
        scale_for_height = self.max_height / max_height
        scaled_height = [height * scale_for_height for height in all_height]
        min_height = 16
        min_width = 60
        scaled_width = [max(min_width, width) for width in scaled_width]
        scaled_height = [max(min_height, height) for height in scaled_height]
        sum_scaled_width = sum(scaled_width)
        if sum_scaled_width > self.max_width:
            scale_scaled_width = self.max_width / sum_scaled_width
            scaled_width = [width * scale_scaled_width for width in scaled_width]
        scaled_width_gain = self.difference_between_bars(scaled_width, True)
        scaled_height_gain = self.difference_between_bars(scaled_height, False)
        if sum(scaled_width_gain) != self.max_width:
            final_scaled_width = self.normalization_of_amounts(scaled_width_gain, self.max_width)
        else:
            final_scaled_width = scaled_width_gain
        return list(zip(final_scaled_width, scaled_height_gain))

    def difference_between_bars(self, bar_values, is_width):
        if len(bar_values) < 2:
            return bar_values
        min_value = min(bar_values)
        max_value = max(bar_values)
        if max_value - min_value < 0.02 * max_value:
            scale_difference = 3 if is_width else 2
            mean_difference = sum(bar_values) / len(bar_values)
            scaled_difference_values = []
            for value in bar_values:
                if value > mean_difference:
                    scaled_difference_values.append(value * (1 + scale_difference * (value - mean_difference)
                                                             / mean_difference))
                else:
                    scaled_difference_values.append(value * (1 - scale_difference * (mean_difference - value)
                                                             / mean_difference))
            if is_width:
                return self.normalization_of_amounts(scaled_difference_values, sum(bar_values))
            else:
                max_scaled_difference_values = max(scaled_difference_values)
                scale_scaling = max_value / max_scaled_difference_values if max_scaled_difference_values > 0 else 1
                return [value * scale_scaling for value in scaled_difference_values]
        return bar_values

    @staticmethod
    def normalization_of_amounts(scaled_difference_values, sum_bar_values):
        scale_difference_values = sum(scaled_difference_values)
        if scale_difference_values == 0:
            return [sum_bar_values / len(scaled_difference_values)] * len(scaled_difference_values)
        scale_scaling = sum_bar_values / scale_difference_values
        return [value * scale_scaling for value in scaled_difference_values]

    def check_box_visible(self, direction, is_visible):
        if direction == "Left":
            self.left_checkbox.setVisible(is_visible)
        else:
            self.right_checkbox.setVisible(is_visible)