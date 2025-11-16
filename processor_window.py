from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QTextEdit, QGroupBox, QFrame, QFileDialog, QMessageBox,
    QLineEdit
)
from PyQt5.QtCore import Qt
from proc_calcu import SystemCalculator
import json

class ProcessorWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.calculator = SystemCalculator()
        self.results = None  # результат расчёта

        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self.title = QLabel("РАСЧЕТ СИСТЕМЫ МЕТОДОМ ПЕРЕМЕЩЕНИЙ")
        self.title.setAlignment(Qt.AlignCenter)

        self.calc_btn = QPushButton("ВЫПОЛНИТЬ РАСЧЕТ")
        self.calc_btn.clicked.connect(self.calculate_system)
        self.calc_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1f8e4d;
            }
        """)

        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.horizontalHeader().setStretchLastSection(True)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)

        self.query_group = QGroupBox("Получить значения в заданной точке")
        q_layout = QHBoxLayout()

        self.bar_input = QLineEdit()
        self.bar_input.setPlaceholderText("№ стержня")
        self.bar_input.setFixedWidth(60)
        q_layout.addWidget(QLabel("Стержень:"))
        q_layout.addWidget(self.bar_input)

        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("x (м)")
        self.x_input.setFixedWidth(100)
        q_layout.addWidget(QLabel("x:"))
        q_layout.addWidget(self.x_input)

        self.query_btn = QPushButton("Показать значения")
        self.query_btn.clicked.connect(self.query_point)
        self.query_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
        """)
        q_layout.addWidget(self.query_btn)

        self.query_result = QLabel("")
        self.query_result.setWordWrap(True)
        self.query_result.setStyleSheet("""
            QLabel {
                background-color: #f0f3f7;
                border: 1px solid #dcdde1;
                padding: 6px;
                border-radius: 4px;
            }
        """)

        v_layout = QVBoxLayout()
        v_layout.addLayout(q_layout)
        v_layout.addWidget(self.query_result)
        self.query_group.setLayout(v_layout)

    def setup_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)

        header = QHBoxLayout()
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.calc_btn)

        work_layout = QHBoxLayout()
        work_layout.setContentsMargins(0, 10, 0, 0)

        self.results_table.setMinimumWidth(900)
        self.results_table.setMinimumHeight(600)
        self.results_table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        self.results_table.horizontalHeader().setMinimumHeight(30)
        self.results_table.verticalHeader().setDefaultSectionSize(28)

        table_layout = QVBoxLayout()
        table_layout.addWidget(self.results_table)
        table_layout.addWidget(self.query_group)
        table_layout.setStretchFactor(self.results_table, 1)

        self.toggle_btn = QPushButton("◀ Параметры")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.clicked.connect(self.toggle_side_panel)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                writing-mode: vertical-rl;
                padding: 6px;
                font-size: 13px;
                background-color: #2ecc71;
                color: white;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:checked {
                background-color: #27ae60;
            }
        """)

        self.side_panel = QFrame()
        self.side_panel.setMinimumWidth(300)
        self.side_panel.setMaximumWidth(350)
        self.side_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Параметры системы"))
        right_layout.addWidget(self.report_text)
        self.side_panel.setLayout(right_layout)
        self.side_panel.setStyleSheet("""
            QFrame {
                background: #f5f7fa;
                border-left: 2px solid #b2bec3;
            }
        """)

        work_layout.addLayout(table_layout, stretch=10)
        work_layout.addWidget(self.toggle_btn)
        work_layout.addWidget(self.side_panel, stretch=1)

        main_layout.addLayout(header)
        main_layout.addLayout(work_layout)
        self.setLayout(main_layout)

        self.title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2d3436;
        """)

    def toggle_side_panel(self):
        if self.toggle_btn.isChecked():
            self.side_panel.hide()
            self.toggle_btn.setText("▶ Параметры")
        else:
            self.side_panel.show()
            self.toggle_btn.setText("◀ Параметры")

    def calculate_system(self):
        try:
            system_data = self.main_window.collect_info()
            success = self.calculator.calculate_system(system_data, self.main_window)

            if success:
                results = self.calculator.get_results()
                self.results = results
                sigma_allow_list = []
                for bar in system_data.get("Стержни", []):
                    try:
                        sigma_allow_list.append(float(bar[3]))
                    except Exception:
                        sigma_allow_list.append(250e6)

                self.display_results_table(results)
                self.display_report(results, system_data, sigma_allow_list)

                try:
                    self.main_window.update_postprocessor()
                except Exception:
                    pass
            else:
                QMessageBox.warning(self, "Ошибка", "Сначала выполните расчёт!")
                return

        except Exception as e:
            self.report_text.setText(f"Ошибка: {str(e)}")

    def display_report(self, results, system_data, sigma_allow_list):
        report = "РАСЧЁТ СТЕРЖНЕВОЙ СИСТЕМЫ\n" + "="*29 + "\n\n"
        report += f"Количество стержней: {len(system_data['Стержни'])}\n"
        report += f"Количество узлов: {results['n_nodes']}\n"
        report += f"Заделки: {[x + 1 for x in results['fixed_nodes']]}\n\n"
        report += "- Перемещения узлов:\n"
        for i, u in enumerate(results['displacements']):
            report += f"u[{i + 1}] = {u:.6e} м\n"

        report += "\n- Проверка прочности стержней:\n"
        max_sigmas, status_list = SystemCalculator.check_strength(results, sigma_allow_list)
        for i, (sigma_max, status) in enumerate(zip(max_sigmas, status_list)):
            report += f"Cтержень {i + 1}: max |σ| = {sigma_max:.6e} Па → {status}\n"

        self.report_text.setText(report)

    def display_results_table(self, results):
        system_data = self.main_window.collect_info()
        bars_data = system_data["Стержни"]

        n_rows = len(bars_data) * 3
        self.results_table.setRowCount(n_rows)
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Стержень", "x (м)", "Усилие N (Н)", "Перемещение u (м)", "Напряжение σ (Па)"
        ])

        row = 0
        for i, (force_func, stress_func) in enumerate(zip(results['bar_forces'], results['bar_stresses'])):
            L = bars_data[i][0]
            points = [0, L / 2, L]
            for x in points:
                try:
                    N_val = force_func(x)
                except Exception:
                    N_val = 0.0
                try:
                    sigma_val = stress_func(x)
                except Exception:
                    sigma_val = 0.0
                if i < len(results['displacements']) - 1:
                    u_i = results['displacements'][i]
                    u_j = results['displacements'][i + 1]
                    u_val = u_i + (u_j - u_i) * (x / L)
                else:
                    u_val = results['displacements'][i]

                self.results_table.setItem(row, 0, QTableWidgetItem(f"{i + 1}"))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"{x:.3f}"))
                self.results_table.setItem(row, 2, QTableWidgetItem(f"{N_val:.6e}"))
                self.results_table.setItem(row, 3, QTableWidgetItem(f"{u_val:.6e}"))
                self.results_table.setItem(row, 4, QTableWidgetItem(f"{sigma_val:.6e}"))
                row += 1

        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.resizeColumnsToContents()
        self.results_table.resizeRowsToContents()

    def query_point(self):
        if not self.results:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните расчёт!")
            return
        system_data = self.main_window.collect_info()
        bars = system_data.get("Стержни", [])
        distributed_loads = system_data.get("Распределенные нагрузки", [])
        # Номер стержня
        s_bar = self.bar_input.text().strip()
        if not s_bar:
            QMessageBox.warning(self, "Ошибка", "Введите номер стержня!")
            return
        try:
            bar_id = int(s_bar)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Номер стержня должен быть целым числом!")
            return
        if bar_id < 1 or bar_id > len(bars):
            QMessageBox.warning(self, "Ошибка", "Такого стержня не существует!")
            return
        i = bar_id - 1
        # Координата x
        s_x = self.x_input.text().strip()
        if not s_x:
            QMessageBox.warning(self, "Ошибка", "Введите координату x!")
            return
        try:
            x = float(s_x)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Координата x должна быть числом!")
            return
        L = float(bars[i][0])
        if x < 0 or x > L:
            QMessageBox.warning(self, "Ошибка", f"Координата x должна быть в пределах [0; {L}]")
            return
        try:
            force_func = self.results['bar_forces'][i]
            stress_func = self.results['bar_stresses'][i]
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Данные функций для стержня отсутствуют.")
            return
        try:
            N_x = force_func(x)
        except Exception:
            N_x = float('nan')
        try:
            sigma_x = stress_func(x)
        except Exception:
            sigma_x = float('nan')
        try:
            L_bar = float(bars[i][0])
            A = float(bars[i][1])
            E = float(bars[i][2])
        except Exception:
            A = None
            E = None
            L_bar = L

        U0 = float(self.results['displacements'][i])
        UL = float(self.results['displacements'][i + 1]) if i + 1 < len(self.results['displacements']) else U0
        q = 0.0
        for ld in distributed_loads:
            try:
                if int(ld[0]) - 1 == i:
                    q = float(ld[1])
                    break
            except Exception:
                continue
        try:
            if A is None or E is None or A == 0 or E == 0:
                u_x = U0 + (UL - U0) * (x / L_bar)
            else:
                u_x = U0 + (UL - U0) * (x / L_bar) + (q / (2.0 * E * A)) * (x * L_bar - x ** 2)
        except Exception:
            u_x = float('nan')
        out = (
            f"<b>Стержень {bar_id}</b><br>"
            f"x = {x:.6f} м<br><br>"
            f"N(x) = {N_x:.6e} Н<br>"
            f"σ(x) = {sigma_x:.6e} Па<br>"
            f"u(x) = {u_x:.6e} м"
        )
        self.query_result.setText(out)

    def save_results_to_json(self, results):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить результаты расчёта",
            "",
            "JSON Files (*.json)",
            options=options
        )
        if not file_name:
            return

        system_data = self.main_window.collect_info()
        bars_data = system_data["Стержни"]

        json_data = {
            "CalculationResult": {
                "Bars": [],
                "Nodes": []
            }
        }
        # Сохраняем все точки для каждого стержня
        for i, bar_points in enumerate(results["bar_forces_points"]):
            xs, Ns = zip(*bar_points)
            _, sigmas = zip(*results["bar_stresses_points"][i])
            _, us = zip(*results["bar_displacements_points"][i])

            bar_entry = {
                "bar_id": i + 1,
                "length": bars_data[i][0],
                "cross_section": bars_data[i][1],
                "modulus_of_elasticity": bars_data[i][2],
                "points": []
            }

            for x, N_val, sigma_val, u_val in zip(xs, Ns, sigmas, us):
                bar_entry["points"].append({
                    "x": x,
                    "N": N_val,
                    "sigma": sigma_val,
                    "u": u_val
                })

            json_data["CalculationResult"]["Bars"].append(bar_entry)
        for i, u in enumerate(results["displacements"]):
            json_data["CalculationResult"]["Nodes"].append({
                "node_id": i + 1,
                "u": u
            })

        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        QMessageBox.information(self, "Сохранено", "Результаты успешно сохранены!")


