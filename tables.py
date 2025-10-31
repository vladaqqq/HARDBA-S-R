from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QValidator



class EmptyAllowedValidator(QValidator):
    def __init__(self, base_validator, parent=None):
        super().__init__(parent)
        self.base_validator = base_validator

    def validate(self, text, pos):
        if text.strip() == "":
            return QValidator.Acceptable, text, pos
        return self.base_validator.validate(text, pos)


class TablesDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent = None, is_int = False, is_positive = False):
        super().__init__(parent)
        self.is_int = is_int
        self.is_positive = is_positive

    def createEditor(self, parent, option, index):
        row_editor = QtWidgets.QLineEdit(parent)

        if self.is_int:
            row_validator = QIntValidator()
            if self.is_positive:
                row_validator.setBottom(0)
            row_editor.setValidator(EmptyAllowedValidator(row_validator))
        else:
            row_validator = QDoubleValidator()
            if self.is_positive:
                row_validator.setBottom(0.0)
            row_validator.setNotation(QDoubleValidator.StandardNotation)

        row_validator.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        row_editor.setValidator(EmptyAllowedValidator(row_validator))
        return row_editor


class MainTables(QTableWidget):
    def __init__(self, table_name=""):
        super().__init__()
        self.table_name = table_name
        self.create_tables()

    #создание таблиц
    def create_tables(self):
        self.plus_btn = QtWidgets.QPushButton("+") # noqa
        self.minus_btn = QtWidgets.QPushButton("-") # noqa

        if self.table_name == "Сосредтотченные нагрузки":
            self.setRowCount(1)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0,TablesDelegate(self, is_int = True, is_positive = True))
            self.setItemDelegateForColumn(1, TablesDelegate(self, is_int = False, is_positive = False))
        elif self.table_name == "Распределенные нагрузки":
            self.setRowCount(1)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0, TablesDelegate(self, is_int = True, is_positive = True))
            self.setItemDelegateForColumn(1, TablesDelegate(self, is_int = False, is_positive = False))
        else:
            self.setRowCount(1)
            self.setColumnCount(4)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegate(TablesDelegate(self, is_int = False, is_positive = True))

        self.plus_btn.clicked.connect(self.add_row)
        self.minus_btn.clicked.connect(self.remove_row)

        if self.table_name == "Сосредтотченные нагрузки":
            self.setHorizontalHeaderLabels(["№Узла","F"])
        elif self.table_name == "Распределенные нагрузки":
            self.setHorizontalHeaderLabels(["№Стержня","q"])
        else:
            self.setHorizontalHeaderLabels(["Длина(L)","Поперечное сечение(A)","Модуль упрогсти(E)", "Напряжение(σ)"])

    #подстраиваем формат для json
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
            "List values": []
        }

        for row in range(self.rowCount()):
            if self.table_name == "Стержни":
                row_values = {"barNumber": row + 1}
                for col, field_name in enumerate(tables_data_name):
                    item = self.item(row, col)
                    row_values[field_name] = item.text() if item else "0"
                tables_json_data["List values"].append(row_values)
            else:
                row_values = {}
                for col, field_name in enumerate(tables_data_name):
                    item = self.item(row, col)
                    row_values[field_name] = item.text() if item else "0"
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

        self.setRowCount(len(list_values))

        for row, row_data in enumerate(list_values):
            for col, field_name in enumerate(fields):
                #if valid_values() == True:
                    value = str(row_data.get(field_name, ""))
                    item = QtWidgets.QTableWidgetItem(value)
                    self.setItem(row, col, item)
        return True


    def add_row(self):
        current_rows = self.currentRow()
        self.insertRow(current_rows + 1)
        self.clearSelection()

    def remove_row(self):
        current_rows = self.currentRow()
        self. removeRow(current_rows)
        self.clearSelection()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Equal:
                self.add_row()
            elif event.key() == Qt.Key_Minus:
                self.remove_row()
            else:
                super().keyPressEvent(event)