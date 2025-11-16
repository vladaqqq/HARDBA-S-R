from PyQt5.QtCore import QRectF, QLineF, Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsItem, QGroupBox, QHBoxLayout,  QCheckBox


class BarCheckBox(QGraphicsItem):
    def __init__(self, x = 0, y = 0, scaled_height = 0, direction = "Left"):
        super().__init__()
        self.x = x
        self.y = y
        self.scaled_height = scaled_height
        self.direction = direction
        self.setPos(self.x, self.y)

    def boundingRect(self):
        return QRectF(0, -7, 40, self.scaled_height + 20)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(1)
        painter.setPen(pen)
        indent = 5
        line_count = int(self.scaled_height // indent)
        if self.direction == "Left":
            painter.drawLine(QLineF(30, 0, 30, self.scaled_height))
            for i in range(line_count + 1):
                painter.drawLine(QLineF(30, i * indent, 15, i * indent + 7))
        else:
            painter.drawLine(QLineF(0, 0, 0, self.scaled_height))
            for i in range(line_count + 1):
                painter.drawLine(QLineF(0, i * indent, 15, i * indent - 7))


class CheckboxBTN(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Заделки", parent=parent)
        self.setAlignment(Qt.AlignCenter)
        self.checkbox_layout = QHBoxLayout()
        self.left_checkbox = QCheckBox("Левая")
        self.right_checkbox = QCheckBox("Правая")
        self.left_checkbox.stateChanged.connect(lambda x: parent.scene.check_box_visible("Left", x)) # noqa
        self.right_checkbox.stateChanged.connect(lambda x: parent.scene.check_box_visible("Right", x)) # noqa
        self.checkbox_layout.addWidget(self.left_checkbox)
        self.checkbox_layout.addWidget(self.right_checkbox)
        self.setLayout(self.checkbox_layout)