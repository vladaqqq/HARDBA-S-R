from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator

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
        else:
            row_validator = QDoubleValidator()
            if self.is_positive:
                row_validator.setBottom(0.0)
        row_editor.setValidator(row_validator)
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
            self.setRowCount(3)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0,TablesDelegate(self, is_int = True, is_positive = True))
            self.setItemDelegateForColumn(1, TablesDelegate(self, is_int = False, is_positive = False))
        elif self.table_name == "Распределенные нагрузки":
            self.setRowCount(3)
            self.setColumnCount(2)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0, TablesDelegate(self, is_int = True, is_positive = True))
            self.setItemDelegateForColumn(1, TablesDelegate(self, is_int = False, is_positive = False))
        else:
            self.setRowCount(3)
            self.setColumnCount(4)
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            self.setItemDelegateForColumn(0, TablesDelegate(self, is_int = True, is_positive = True))
            self.setItemDelegateForColumn(1, TablesDelegate(self, is_int = False, is_positive = True))
            self.setItemDelegateForColumn(2, TablesDelegate(self, is_int = False, is_positive = True))
            self.setItemDelegateForColumn(3, TablesDelegate(self, is_int = False, is_positive = True))

        self.plus_btn.clicked.connect(self.add_row)
        self.minus_btn.clicked.connect(self.remove_row)



        if self.table_name == "Сосредтотченные нагрузки":
            self.setHorizontalHeaderLabels(["№Узла","F"])
        elif self.table_name == "Распределенные нагрузки":
            self.setHorizontalHeaderLabels(["№Стержня","q"])
        else:
            self.setHorizontalHeaderLabels(["Длина(L)","Поперечное сечение(A)","Модуль упрогсти(E)", "Напряжение(σ)"])

    def add_row(self):
        current_rows = self.rowCount()
        self.setRowCount(current_rows + 1)

    def remove_row(self):
        current_rows = self.rowCount()
        if current_rows !=1:
            self.setRowCount(current_rows - 1)