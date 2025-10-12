import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.burger_btn = None
        self.table_menu = None
        self.table_menu1 = None
        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self.burger_btn = QtWidgets.QPushButton("☰")
        self.burger_btn.setFixedSize(40, 40)
        self.burger_btn.clicked.connect(self.show_menu)
        self.table_menu = MainTables()
        self.table_menu1 = MainTables()

    def setup_layout(self):
        main_layout = QtWidgets.QHBoxLayout()
        main_layout1 = QtWidgets.QVBoxLayout()
        main_layout1.addWidget(self.burger_btn)
        main_layout1.addStretch(1)

        group_box1 = QtWidgets.QGroupBox("Узловые силы")
        table_layout1 = QtWidgets.QVBoxLayout()
        table_layout1.addWidget(self.table_menu)
        group_box1.setLayout(table_layout1)

        group_box2 = QtWidgets.QGroupBox("Распределенные нагрузки")
        table_layout2 = QtWidgets.QVBoxLayout()
        table_layout2.addWidget(self.table_menu1)
        group_box2.setLayout(table_layout2)

        tables_container = QtWidgets.QVBoxLayout()
        tables_container.addWidget(group_box1)
        tables_container.addWidget(group_box2)
        tables_container.addStretch(1)

        main_layout.addLayout(main_layout1)
        main_layout.addLayout(tables_container)
        self.setLayout(main_layout)

    #высвечивание меню
    def show_menu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction("Показать таблицы")
        menu.addAction("Скрыть таблицы")
        menu.addAction("Сохранить файл")
        menu.exec_(self.burger_btn.mapToGlobal(self.burger_btn.rect().bottomLeft()))


class MainTables(QTableWidget):
    def __init__(self):
        super().__init__()
        self.create()

    def create(self):
        self.setRowCount(3)
        self.setColumnCount(3)


if __name__ =="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("SAPR-BAR")
    window.resize(800,800)
    window.show()
    sys.exit(app.exec_())