from PyQt5 import QtWidgets
from graph_1 import GraphicsViewer
from tables import MainTables
from validator import validate_tables_data, validate_tables_data_on_open
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QAction, QPushButton, QTableWidget, QTabWidget
import json
from processor_window import ProcessorWindow
from postproc_window import PostProcessorWindow

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

        self.table_menu = MainTables("Стержни", parent=self)# noqa первая таблица
        self.table_menu1 = MainTables("Распределенные нагрузки", parent=self) # noqa вторая таблица
        self.table_menu2 = MainTables("Сосредтотченные нагрузки", parent=self) # noqa третья таблица
        self.viewer = GraphicsViewer(self) # noqa

        self.mode_tabs = QTabWidget()
        self.mode_tabs.setTabPosition(QTabWidget.North)
        self.mode_tabs.setMovable(False)

        # Создаем виджеты для вкладок
        self.preprocess_tab = QWidget()
        self.process_tab = ProcessorWindow(self)  # Используем готовый класс процессора
        self.postprocess_tab = PostProcessorWindow(self)

        self.mode_tabs.addTab(self.preprocess_tab, "Препроцессор")
        self.mode_tabs.addTab(self.process_tab, "Процессор")
        self.mode_tabs.addTab(self.postprocess_tab, "Постпроцессор")

        # создание лэйаутов
    def setup_layout(self):
        main_layout = QtWidgets.QVBoxLayout()  # основной лэйаут
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Верхняя панель с бургер-меню и вкладками на одном уровне
        top_bar = QtWidgets.QVBoxLayout()
        top_bar.setContentsMargins(5, 5, 5, 5)
        top_bar.addWidget(self.burger_btn)
        top_bar.addWidget(self.mode_tabs, stretch=1)

        main_layout.addLayout(top_bar)

        preprocess_main_layout = QtWidgets.QHBoxLayout()
        preprocess_main_layout.setContentsMargins(0, 0, 0, 0)

        # Левая часть - график
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.viewer)

        # Правая часть - таблицы
        self.group_box1 = QtWidgets.QGroupBox("Стержни")
        table_layout1 = QtWidgets.QVBoxLayout()
        table_layout1.addWidget(self.table_menu)
        table_layout1.addWidget(self.table_menu.plus_btn)
        table_layout1.addWidget(self.table_menu.minus_btn)
        self.group_box1.setLayout(table_layout1)

        self.group_box2 = QtWidgets.QGroupBox("Распределенные нагрузки")
        table_layout2 = QtWidgets.QVBoxLayout()
        table_layout2.addWidget(self.table_menu1)
        table_layout2.addWidget(self.table_menu1.plus_btn)
        table_layout2.addWidget(self.table_menu1.minus_btn)
        self.group_box2.setLayout(table_layout2)

        self.group_box3 = QtWidgets.QGroupBox("Сосредтотченные нагрузки")
        table_layout3 = QtWidgets.QVBoxLayout()
        table_layout3.addWidget(self.table_menu2)
        table_layout3.addWidget(self.table_menu2.plus_btn)
        table_layout3.addWidget(self.table_menu2.minus_btn)
        self.group_box3.setLayout(table_layout3)

        tables_widget = QWidget()
        tables_widget.setMaximumWidth(780)
        tables_container = QtWidgets.QVBoxLayout()
        tables_container.addWidget(self.group_box1)
        tables_container.addWidget(self.group_box2)
        tables_container.addWidget(self.group_box3)
        tables_container.addStretch(1)
        tables_widget.setLayout(tables_container)

        # Собираем layout препроцессора
        preprocess_main_layout.addLayout(left_layout)
        preprocess_main_layout.addWidget(tables_widget)
        self.preprocess_tab.setLayout(preprocess_main_layout)

        # Для постпроцессора пока пустой layout
        postprocess_layout = QtWidgets.QVBoxLayout()
        postprocess_layout.addWidget(QtWidgets.QLabel("Постпроцессор - здесь будут результаты расчетов"))
        self.postprocess_tab.setLayout(postprocess_layout)

        self.setLayout(main_layout)

    #высвечивание меню
    def show_menu(self):
        menu = QtWidgets.QMenu(self)
        submenu = QtWidgets.QMenu("Таблицы",self)
        action1 = QAction("Стержни", submenu)
        submenu.addAction(action1)
        action2 = QAction("Распределенные нагрузки")
        submenu.addAction(action2)
        action3 = QAction("Сосредтотченные нагрузки")
        submenu.addAction(action3)
        menu.addMenu(submenu)
        open_action = menu.addAction("Открыть файл")
        save_action = menu.addAction("Сохранить файл")
        save_calc_action = menu.addAction("Сохранить файл расчёта")
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
        elif action == save_calc_action:
            self.save_calculation()

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

            # Валидация
            errors = validate_tables_data_on_open(table1_data, table2_data, table3_data)
            if errors:
                error_text = "\n".join(errors)
                QMessageBox.warning(self, "Ошибки валидации", f"Обнаружены ошибки:\n\n{error_text}")
                return

            # Загружаем данные
            for table_data in data["Objects"]:
                table_name = table_data["Object"]
                if table_name == "Стержни":
                    self.table_menu.load_from_json(table_data)
                elif table_name == "Распределенные нагрузки":
                    self.table_menu1.load_from_json(table_data)
                elif table_name == "Сосредтотченные нагрузки":
                    self.table_menu2.load_from_json(table_data)

            info = self.collect_info()
            self.scene = self.viewer.scene
            self.scene.loading_from_file = True
            self.scene.update_scene(info)


            QMessageBox.information(self, "Успех", "Все таблицы загружены")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def save_calculation(self):
        try:
            results = self.process_tab.results
        except AttributeError:
            QMessageBox.warning(self, "Нет данных", "Сначала выполните расчёт!")
            return
        try:
            self.process_tab.save_results_to_json(results)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении расчёта:\n{str(e)}")

    def collect_info(self):
        res = dict()
        res["Стержни"] = self.table_menu.collect_info_bar()
        res["Распределенные нагрузки"] = self.table_menu1.collect_info_loads()
        res["Сосредоточенные нагрузки"] = self.table_menu2.collect_info_loads()
        return res

    def update_postprocessor(self):
        try:
            self.postprocess_tab.update_results()
        except AttributeError:
            QMessageBox.warning(self, "Ошибка", "Метод обновления постпроцессора недоступен")

#работа с показом и скрытием таблиц
def tables_work(table_group_box):
    if table_group_box.isVisible():
        table_group_box.hide()
    else:
        table_group_box.show()