from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtCore import Qt, QRegExp


class TableDelegate(QStyledItemDelegate):
    def __init__(self, column_type: dict, parent=None):
        super().__init__(parent)
        self.column_type = column_type

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setAlignment(Qt.AlignHCenter)
        validator = None
        if self.column_type["type"] == "int":
            if self.column_type["plus"]:
                validator = QIntValidator(1, 1000000, parent)
            else:
                regex = QRegExp(r"^-?(0*[1-9]\d*)$")
                validator = QRegExpValidator(regex, parent)
        elif self.column_type["type"] == "float":
            if self.column_type["plus"]:
                regex = QRegExp(r"^(\d+\.?\d*|\.\d+)$")
            else:
                regex = QRegExp(r"^-?(\d*\.?\d*|\d+\.\d*)$")
            validator = QRegExpValidator(regex, parent)

        editor.setValidator(validator)
        return editor

    def setEditorData(self, editor, index):
        text = index.data(Qt.DisplayRole) or ""
        editor.setText(str(text))

    def setModelData(self, editor, model, index):
        text = editor.text().strip()

        if not text:
            text = self._get_default_value()
        else:
            text = self._validate_and_correct(text)

        model.setData(index, text, Qt.EditRole)

    def _get_default_value(self):
        if self.column_type["type"] == "int":
            return "1"
        else:
            return "1.0"

    def _validate_and_correct(self, text):
        if text in ["", ".", "-", "-."]:
            return self._get_default_value()

        try:
            if self.column_type["type"] == "int":
                value = int(text)
                if value == 0:
                    return self._get_default_value()
                if self.column_type["plus"] and value < 0:
                    return str(abs(value))
                return str(value)
            else:
                value = float(text)
                if value == 0:
                    return self._get_default_value()
                if self.column_type["plus"] and value < 0:
                    value = abs(value)
                if value == int(value):
                    return f"{int(value)}.0"
                else:
                    text = f"{value:.10f}".rstrip('0').rstrip('.')
                    if '.' not in text:
                        text += ".0"
                    if text == "0.0":
                        return self._get_default_value()
                    return text

        except ValueError:
            return self._get_default_value()


class MainTables(QTableWidget):
    def __init__(self, table_name="", parent=None):
        super().__init__()
        self.parent = parent
        self.table_name = table_name
        self.create_tables()
        self.itemChanged.connect(self.itemChangedEvent)

    # создание таблиц
    def create_tables(self):
        self.plus_btn = QtWidgets.QPushButton("+")  # noqa
        self.minus_btn = QtWidgets.QPushButton("-")  # noqa

        if self.table_name == "Сосредтотченные нагрузки":
            self.setRowCount(0)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0, TableDelegate({"type": "int", "plus": True}, parent=self))
            self.setItemDelegateForColumn(1, TableDelegate({"type": "float", "plus": False}, parent=self))
            self.add_row()
        elif self.table_name == "Распределенные нагрузки":
            self.setRowCount(0)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0, TableDelegate({"type": "int", "plus": True}, parent=self))
            self.setItemDelegateForColumn(1, TableDelegate({"type": "float", "plus": False}, parent=self))
            self.add_row()
        else:
            self.setRowCount(0)
            self.setColumnCount(4)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegate(TableDelegate({"type": "float", "plus": True}, parent=self))
            self.add_row()

        self.plus_btn.clicked.connect(self.add_row)
        self.minus_btn.clicked.connect(self.remove_row)

        if self.table_name == "Сосредтотченные нагрузки":
            self.setHorizontalHeaderLabels(["№Узла", "F"])
        elif self.table_name == "Распределенные нагрузки":
            self.setHorizontalHeaderLabels(["№Стержня", "q"])
        else:
            self.setHorizontalHeaderLabels(["Длина(L)", "Поперечное сечение(A)", "Модуль упрогсти(E)", "Напряжение(σ)"])

    # подстраиваем формат для json
    def tables_json(self):
        tables_data = {
            "Стержни": ["lenght", "cross_section", "modulus_of_elasticity", "pressure"],
            "Сосредтотченные нагрузки": ["node_number", "force"],
            "Распределенные нагрузки": ["bar_number", "distributed_load"]
        }

        tables_data_name = tables_data.get(self.table_name)

        tables_json_data = {
            "Object": self.table_name,
            "Count": self.rowCount(),
            "List values": [],
            "Правая заделка": self.parent.viewer.checkbox.right_checkbox.isChecked(),
            "Левая заделка": self.parent.viewer.checkbox.left_checkbox.isChecked(),
        }

        for row in range(self.rowCount()):
            if self.table_name == "Стержни":
                row_values = {"barNumber": row + 1}
                for col, field_name in enumerate(tables_data_name):
                    item = self.item(row, col)
                    if item is None or item.text().strip() == "":
                        row_values[field_name] = "0"
                    else:
                        row_values[field_name] = item.text()
                tables_json_data["List values"].append(row_values)
            else:
                row_values = {}
                for col, field_name in enumerate(tables_data_name):
                    item = self.item(row, col)
                    if item is None or item.text().strip() == "":
                        row_values[field_name] = "0"
                    else:
                        row_values[field_name] = item.text()
                tables_json_data["List values"].append(row_values)

        return tables_json_data

    def load_from_json(self, table_data):
        tables_data = {
            "Стержни": ["lenght", "cross_section", "modulus_of_elasticity", "pressure"],
            "Сосредтотченные нагрузки": ["node_number", "force"],
            "Распределенные нагрузки": ["bar_number", "distributed_load"]
        }

        fields = tables_data.get(self.table_name, [])
        list_values = table_data.get("List values", [])

        self.setRowCount(0)
        for i in range(len(list_values)):
            self.add_row()

        for row, row_data in enumerate(list_values):
            for col, field_name in enumerate(fields):
                value = str(row_data.get(field_name, ""))
                item = QtWidgets.QTableWidgetItem(value)
                self.setItem(row, col, item)

        self.parent.viewer.checkbox.left_checkbox.setChecked(table_data["Левая заделка"])
        self.parent.viewer.checkbox.right_checkbox.setChecked(table_data["Правая заделка"])
        return True

    def collect_info_bar(self):
        res = []
        rows = self.rowCount()
        columns = self.columnCount()
        for row in range(rows):
            bar = []
            for column in range(columns):
                item = self.item(row, column)
                if item.text():
                    if float(item.text())<=0:
                        break
                    bar.append(float(item.text()))
            else:
                res.append(bar)
        return res

    def collect_info_loads(self):
        res = []
        rows = self.rowCount()
        columns = self.columnCount()
        for row in range(rows):
            load = []
            for column in range(columns):
                item = self.item(row, column)
                if column == 0:
                    if int(item.text()) <= 0:
                        break
                    load.append(int(item.text()))
                else:
                    load.append(float(item.text()))
            else:
                res.append(load)
        return res

    def add_row(self):
        current_rows = self.currentRow()
        self.insertRow(current_rows + 1)
        for column in range(0, self.columnCount()):
            row = current_rows + 1
            item = QTableWidgetItem("0")
            self.setItem(row, column, item)
        self.clearSelection()

    def remove_row(self):
        current_rows = self.currentRow()
        self.removeRow(current_rows)
        self.clearSelection()
        self.parent.viewer.scene.update_scene(self.parent.collect_info())

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Equal:
                self.add_row()
            elif event.key() == Qt.Key_Minus:
                self.remove_row()
            else:
                super().keyPressEvent(event)

    def itemChangedEvent(self, item):
        row = item.row()
        if self.table_name == "Стержни":
            for column in range(0, 4):
                item = self.item(row, column)
                if item.text():
                    if float(item.text()) <= 0:
                        break
                else:
                    break
            else:
                self.parent.viewer.scene.update_scene(self.parent.collect_info())
        else:
            for column in range(0, 2):
                item = self.item(row, column)
                if item.text():
                    if column == 0:
                        if float(item.text()) <= 0:
                            break
                    else:
                        if float(item.text()) == 0:
                            break
                else:
                    break
            else:
                self.parent.viewer.scene.update_scene(self.parent.collect_info())