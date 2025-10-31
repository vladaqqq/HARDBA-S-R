from PyQt5 import QtWidgets
from PyQt5.QtGui import QKeySequence

from graph_1 import GraphicsViewer
from tables import MainTables
from validator import validate_tables_data, validate_tables_data_on_open
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import json

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.setup_layout()

    #создание виджетов
    def create_widgets(self):
        self.burger_btn = QtWidgets.QPushButton("☰")  # noqa
        self.burger_btn.setFixedSize(40, 40)
        self.burger_btn.clicked.connect(self.show_menu)
        self.viewer = GraphicsViewer()
        self.table_menu = MainTables("Стержни")# noqa первая таблица
        self.table_menu1 = MainTables("Распределенные нагрузки") # noqa вторая таблица
        self.table_menu2 = MainTables("Сосредтотченные нагрузки") # noqa третья таблица

    #создание лэйаутов
    def setup_layout(self):
        main_layout = QtWidgets.QHBoxLayout()   #основной лэйаут
        main_layout1 = QtWidgets.QVBoxLayout()  #лэйаут для бургира
        main_layout1.addWidget(self.burger_btn)


        self.group_box1 = QtWidgets.QGroupBox("Стержни") # noqa
        table_layout1 = QtWidgets.QVBoxLayout()   #лэйаут для певрой таблицы
        table_layout1.addWidget(self.table_menu)
        table_layout1.addWidget(self.table_menu.plus_btn)
        table_layout1.addWidget(self.table_menu.minus_btn)
        self.group_box1.setLayout(table_layout1)

        self.group_box2 = QtWidgets.QGroupBox("Распределенные нагрузки") # noqa
        table_layout2 = QtWidgets.QVBoxLayout()   #лэйаут для второй таблицы
        table_layout2.addWidget(self.table_menu1)
        table_layout2.addWidget(self.table_menu1.plus_btn)
        table_layout2.addWidget(self.table_menu1.minus_btn)
        self.group_box2.setLayout(table_layout2)

        self.group_box3 = QtWidgets.QGroupBox("Сосредтотченные нагрузки") # noqa
        table_layout3 = QtWidgets.QVBoxLayout()
        table_layout3.addWidget(self.table_menu2)
        table_layout3.addWidget(self.table_menu2.plus_btn)
        table_layout3.addWidget(self.table_menu2.minus_btn)
        self.group_box3.setLayout(table_layout3)

        tables_widget = QWidget()
        tables_widget.setMaximumWidth(780)
        tables_container = QtWidgets.QVBoxLayout()   #лэйаут для всех таблиц
        tables_container.addWidget(self.group_box1)
        tables_container.addWidget(self.group_box2)
        tables_container.addWidget(self.group_box3)
        tables_container.addStretch(1)
        tables_widget.setLayout(tables_container)

        main_layout1.addWidget(self.viewer)
        main_layout.addLayout(main_layout1)   #добавление в основой лэйаут
        main_layout.addWidget(tables_widget)
        self.setLayout(main_layout)

    #высвечивание меню
    def show_menu(self):
        menu = QtWidgets.QMenu(self)

        submenu = QtWidgets.QMenu("Таблицы",self)
        action1 = submenu.addAction("Стержни", submenu)
        action1.setShortcut(QKeySequence(Qt.ALT + Qt.Key_O))
        action1.triggered.connect(tables_work(self.group_box1))
        action2 = submenu.addAction("Распределенные нагрузки")
        action3 = submenu.addAction("Сосредтотченные нагрузки")
        menu.addMenu(submenu)

        open_action = menu.addAction("Открыть файл")
        save_action = menu.addAction("Сохранить файл")
        action = menu.exec_(self.burger_btn.mapToGlobal(self.burger_btn.rect().bottomLeft()))

        if action == action1:
            tables_work(self.group_box1)
        elif action == action2:
            tables_work(self.group_box2)
        elif action == action3:
            tables_work(self.group_box3)
        elif action == save_action:
            self.save_all_tables()
        elif action == open_action:
            self.open_file()

    #сохранение файлов
    def save_all_tables(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить все таблицы", "", "JSON Files (*.json)", options=options) #окно для сохранения
        if not file_name:
            return

        errors = validate_tables_data(self.table_menu.tables_json(), self.table_menu1.tables_json(),
                                      self.table_menu2.tables_json())
        if errors:
            error_text = "\n".join(errors)
            QMessageBox.warning(self, "Ошибки валидации", f"Обнаружены ошибки:\n\n{error_text}")
            return

        all_tables_json = dict()
        data = list()
        data.append(self.table_menu.tables_json())
        data.append(self.table_menu1.tables_json())
        data.append(self.table_menu2.tables_json()) #все таблицы в словари
        all_tables_json["Objects"] = data
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(all_tables_json, f, ensure_ascii=False, indent=4) #сохранение в файл

        QMessageBox.information(self, "Сохранение", f"Таблицы сохранены в:\n{file_name}")

    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл таблиц", "", "JSON Files (*.json)", options=options
        )
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "Objects" not in data:
                QMessageBox.warning(self, "Ошибка", "Неверный формат файла")
                return

            table1_data = None
            table2_data = None
            table3_data = None

            # Собираем данные таблиц
            for table_data in data["Objects"]:
                if table_data["Object"] == "Стержни":
                    table1_data = table_data
                elif table_data["Object"] == "Распределенные нагрузки":
                    table2_data = table_data
                elif table_data["Object"] == "Сосредтотченные нагрузки":
                    table3_data = table_data

            # Валидация при открытии (уже включает проверку наличия всех таблиц)
            errors = validate_tables_data_on_open(table1_data, table2_data, table3_data)
            if errors:
                error_text = "\n".join(errors)
                QMessageBox.warning(self, "Ошибки валидации", f"Обнаружены ошибки:\n\n{error_text}")
                return

            # Загружаем данные (валидация уже прошла)
            for table_data in data["Objects"]:
                table_name = table_data["Object"]
                if table_name == "Стержни":
                    self.table_menu.load_from_json(table_data)
                elif table_name == "Распределенные нагрузки":
                    self.table_menu1.load_from_json(table_data)
                elif table_name == "Сосредтотченные нагрузки":
                    self.table_menu2.load_from_json(table_data)

            QMessageBox.information(self, "Успех", "Все таблицы загружены")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

#работа с показом и скрытием таблиц
def tables_work(table_group_box):
    if table_group_box.isVisible():
        table_group_box.hide()
    else:
        table_group_box.show()