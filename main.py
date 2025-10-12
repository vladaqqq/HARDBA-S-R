import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.burger_btn = None
        self.table_menu = None
        self.table_menu1 = None
        self.tables_visible = True
        self.group_box1 = None  # Добавляем как атрибуты
        self.group_box2 = None  # Добавляем как атрибуты
        self.create_widgets()
        self.setup_layout()

    #создание виджетов
    def create_widgets(self):
        self.burger_btn = QtWidgets.QPushButton("☰")  #бургир
        self.burger_btn.setFixedSize(40, 40)
        self.burger_btn.clicked.connect(self.show_menu)
        self.table_menu = MainTables("Узловые силы")  #первая таблица
        self.table_menu1 = MainTables("Распределенные нагрузки")  #вторая таблица

    #создание лэйаутов
    def setup_layout(self):
        main_layout = QtWidgets.QHBoxLayout()   #основной лэйаут
        main_layout1 = QtWidgets.QVBoxLayout()  #лэйаут для бургира
        main_layout1.addWidget(self.burger_btn)
        main_layout1.addStretch()

        self.group_box1 = QtWidgets.QGroupBox("Узловые силы")
        table_layout1 = QtWidgets.QVBoxLayout()   #лэйаут для певрой таблицы
        table_layout1.addWidget(self.table_menu)
        self.group_box1.setLayout(table_layout1)

        self.group_box2 = QtWidgets.QGroupBox("Распределенные нагрузки")
        table_layout2 = QtWidgets.QVBoxLayout()   #лэйаут для второй таблицы
        table_layout2.addWidget(self.table_menu1)
        self.group_box2.setLayout(table_layout2)

        tables_container = QtWidgets.QVBoxLayout()   #лэйаут для обеих таблиц
        tables_container.addWidget(self.group_box1)
        tables_container.addWidget(self.group_box2)
        tables_container.addStretch(1)

        main_layout.addLayout(main_layout1)   #добавление в основой лэйаут
        main_layout.addLayout(tables_container)
        self.setLayout(main_layout)

    #высвечивание меню
    def show_menu(self):
        menu = QtWidgets.QMenu(self)
        show_action = menu.addAction("Показать таблицы")
        hide_action = menu.addAction("Скрыть таблицы")
        save_action = menu.addAction("Сохранить файл")

        action = menu.exec_(self.burger_btn.mapToGlobal(self.burger_btn.rect().bottomLeft()))

        if action == show_action:
            self.show_tables()
        elif action == hide_action:
            self.hide_tables()
        elif action == save_action:
            self.save_file()

    #показать таблицы
    def show_tables(self):
        self.group_box1.show()
        self.group_box2.show()

    #скрыть таблицы
    def hide_tables(self):
        self.group_box1.hide()
        self.group_box2.hide()


class MainTables(QTableWidget):
    def __init__(self, table_name=""):
        super().__init__()
        self.table_name = table_name
        self.create()

    #создание таблиц
    def create(self):
        self.setRowCount(3)
        self.setColumnCount(3)
        if self.table_name == "Узловые силы":
            self.setHorizontalHeaderLabels(["F","Q","D"])
        else:
            self.setHorizontalHeaderLabels(["A","A","A"])


if __name__ =="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("SAPR-BAR")
    window.resize(800,800)
    window.show()
    sys.exit(app.exec_())