from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit, QMessageBox, QPushButton, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from export_pdf import PDFReportGenerator


class PostProcessorWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.results = None

        # визуальные параметры (можно настраивать)
        self.max_height = 250  # пиксели-условная высота для визуализации поперечных сечений
        self.max_width = None  # будет вычисляться динамически в bar_scaling
        self.min_height_visual = 16
        self.min_width_visual = 60

        self.create_widgets()
        self.setup_layout()

    # ------------------------------
    # UI setup (ваш код почти без изменений)
    # ------------------------------
    def create_widgets(self):
        self.tabs = QTabWidget()
        self.calc_tab = QWidget()
        self.graph_tab = QTabWidget()
        self.epure_tab = QTabWidget()
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)

        self.save_pdf_btn = QPushButton("Сохранить отчет в PDF")
        self.save_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.save_pdf_btn.clicked.connect(self.save_to_pdf)

        self.n_canvas = FigureCanvas(plt.Figure())
        self.sigma_canvas = FigureCanvas(plt.Figure())
        self.u_canvas = FigureCanvas(plt.Figure())

        self.graph_tab.addTab(self.n_canvas, "N(x)")
        self.graph_tab.addTab(self.sigma_canvas, "σ(x)")
        self.graph_tab.addTab(self.u_canvas, "u(x)")

        self.epure_n_canvas = FigureCanvas(plt.Figure())
        self.epure_sigma_canvas = FigureCanvas(plt.Figure())
        self.epure_u_canvas = FigureCanvas(plt.Figure())

        self.epure_tab.addTab(self.epure_n_canvas, "N(x)")
        self.epure_tab.addTab(self.epure_sigma_canvas, "σ(x)")
        self.epure_tab.addTab(self.epure_u_canvas, "u(x)")

    def setup_layout(self):
        calc_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.save_pdf_btn)
        button_layout.addStretch()

        calc_layout.addLayout(button_layout)
        calc_layout.addWidget(self.results_table)
        calc_layout.addWidget(self.report_text)

        self.calc_tab.setLayout(calc_layout)
        self.tabs.addTab(self.calc_tab, "Расчёты")
        self.tabs.addTab(self.graph_tab, "Графики")
        self.tabs.addTab(self.epure_tab, "Эпюры")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def save_to_pdf(self):
        """Сохранение отчета в PDF"""
        if not hasattr(self.main_window.process_tab, 'results') or not self.main_window.process_tab.results:
            QMessageBox.warning(self, "Ошибка", "Сначала выполните расчет в процессоре!")
            return

        try:
            pdf_generator = PDFReportGenerator(self.main_window)
            pdf_generator.generate_report()
        except ImportError as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модуль PDF: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании PDF: {str(e)}")

    # ------------------------------
    # Обновление данных / таблицы / отчета
    # ------------------------------
    def update_results(self):
        self.results = self.main_window.process_tab.calculator.get_results()
        system_data = self.main_window.collect_info()

        self.fill_table(system_data, self.results)
        self.fill_report(system_data, self.results)
        self.draw_graphs(system_data, self.results)
        self.draw_epures(system_data, self.results)

    def fill_table(self, system_data, results):
        graph_table = results.get("graph_table", [])
        self.results_table.setRowCount(len(graph_table))
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Стержень", "x (м)", "N (Н)", "u (м)", "σ (Па)"])

        for row_idx, row in enumerate(graph_table):
            self.results_table.setItem(row_idx, 0, QTableWidgetItem(str(row["bar"])))
            self.results_table.setItem(row_idx, 1, QTableWidgetItem(f"{row['x']:.5f}"))
            self.results_table.setItem(row_idx, 2, QTableWidgetItem(f"{row['N']:.6e}"))
            self.results_table.setItem(row_idx, 3, QTableWidgetItem(f"{row['u']:.6e}"))
            self.results_table.setItem(row_idx, 4, QTableWidgetItem(f"{row['sigma']:.6e}"))

    def fill_report(self, system_data, results):
        report = "САПР - Расчет стержневой системы\n\n"
        report += f"Количество стержней: {len(system_data['Стержни'])}\n"
        report += f"Количество узлов: {results['n_nodes']}\n"
        report += f"Заделки: {[x+1 for x in results['fixed_nodes']]}\n"
        self.report_text.setText(report)

    # ------------------------------
    # Масштабирование стержней (ваша логика с небольшими изменениями)
    # bar_info: список элементов [length, cross_section, ...]
    # возвращает: [(width_px, height_px), ...]
    # ------------------------------
    def bar_scaling(self, bar_info):
        # определяем доступную ширину (если None — вычисляем от виджета)
        if self.max_width is None:
            try:
                self.max_width = max(300, self.parent().viewport().width() - 200)
            except Exception:
                self.max_width = 800

        all_width = [bar[0] for bar in bar_info]  # реальные длины
        all_height = [bar[1] if len(bar) > 1 else 1.0 for bar in bar_info]  # поперечные сечения или высота

        sum_width = sum(all_width) if sum(all_width) > 0 else 1.0
        scale_for_width = self.max_width / sum_width
        scaled_width = [width * scale_for_width for width in all_width]

        max_height = max(all_height) if all_height else 1.0
        scale_for_height = (self.max_height / max_height) if max_height > 0 else 1.0
        scaled_height = [height * scale_for_height for height in all_height]

        # минимальные значения для визуализации
        min_height = self.min_height_visual
        min_width = self.min_width_visual
        scaled_width = [max(min_width, width) for width in scaled_width]
        scaled_height = [max(min_height, height) for height in scaled_height]

        # если суммарная ширина превысила, нормируем
        sum_scaled_width = sum(scaled_width)
        if sum_scaled_width > self.max_width:
            scale_scaled_width = self.max_width / sum_scaled_width
            scaled_width = [width * scale_scaled_width for width in scaled_width]

        # делаем небольшое усиление различий, как у вас
        scaled_width_gain = self.difference_between_bars(scaled_width, True)
        scaled_height_gain = self.difference_between_bars(scaled_height, False)

        # нормализация суммарной ширины в точность до max_width
        if abs(sum(scaled_width_gain) - self.max_width) > 1e-6:
            final_scaled_width = self.normalization_of_amounts(scaled_width_gain, self.max_width)
        else:
            final_scaled_width = scaled_width_gain

        return list(zip(final_scaled_width, scaled_height_gain))

    def difference_between_bars(self, bar_values, is_width):
        if len(bar_values) < 2:
            return bar_values
        min_value = min(bar_values)
        max_value = max(bar_values)
        if max_value == 0:
            return bar_values
        # если разброс маленький — усиливаем различия
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
                max_scaled = max(scaled_difference_values) if scaled_difference_values else 1.0
                scale_scaling = max_value / max_scaled if max_scaled > 0 else 1.0
                return [value * scale_scaling for value in scaled_difference_values]
        return bar_values

    @staticmethod
    def normalization_of_amounts(scaled_difference_values, sum_bar_values):
        scale_difference_values = sum(scaled_difference_values)
        if scale_difference_values == 0:
            n = len(scaled_difference_values)
            return [sum_bar_values / n] * n
        scale_scaling = sum_bar_values / scale_difference_values
        return [value * scale_scaling for value in scaled_difference_values]

    # ------------------------------
    # Вспомогательные: маппинг локальных x -> глобальные отображаемые x
    # scaled_layout: результат bar_scaling()
    # ------------------------------
    def compute_scaled_layout(self, system_data):
        """
        Возвращает:
          scaled_layout: [(width_px, height_px), ...]
          cum_x: [0, w0, w0+w1, ...] - кумулятивные координаты начала каждого стержня
          total_visual_width: float
        """
        bars = system_data["Стержни"]
        scaled_layout = self.bar_scaling(bars)
        widths = [w for w, h in scaled_layout]
        cum_x = [0.0]
        s = 0.0
        for w in widths:
            s += w
            cum_x.append(s)
        total_visual_width = sum(widths)
        return scaled_layout, cum_x, total_visual_width

    def map_local_xs_to_global(self, xs, bar_index, system_data, scaled_layout, cum_x):
        """
        Переводит локальные координаты xs (от 0 до длины стержня) в глобальные отображаемые X,
        соответствующие визуальным ширинам из scaled_layout.
        """
        real_length = system_data["Стержни"][bar_index][0]
        visual_width = scaled_layout[bar_index][0]
        start = cum_x[bar_index]
        if real_length == 0:
            return [start + visual_width * 0.5 for _ in xs]
        return [start + (x / real_length) * visual_width for x in xs]

    def compute_y_limits(self, values_list, min_visual_ratio=0.05, absolute_min=1e-9):
        # склеиваем все значения
        flat = []
        for arr in values_list:
            flat.extend(arr)
        if not flat:
            return -1.0, 1.0  # запас

        max_val = max(flat)
        min_val = min(flat)
        max_abs = max(abs(min_val), abs(max_val))

        # если все нули или очень маленькие значения — делаем визуальное "усиление"
        if max_abs < absolute_min:
            # используем относительную величину, чтобы показать "форму"
            delta = 1.0
            return -delta, delta

        # если диапазон слишком мал по сравнению с максимумом -> увеличим его
        spread = max_val - min_val
        if spread / max_abs < min_visual_ratio:
            # расширим spread до min_visual_ratio * max_abs вокруг центра
            center = 0.5 * (max_val + min_val)
            half = max_abs * min_visual_ratio * 0.5 if max_abs > 0 else min_visual_ratio
            return center - half * 2, center + half * 2  # немного увеличиваем
        # обычный случай
        return -max_abs * 1.1, max_abs * 1.1

    def draw_graphs(self, system_data, results, displ_scale=1.0):
        # Получаем масштаб для X (визуальная раскладка стержней)
        scaled_layout, cum_x, total_visual_width = self.compute_scaled_layout(system_data)

        # Подготовка данных для вычисления общих Y-лимитов
        forces_vals = [ [y for _, y in pts] for pts in results.get('bar_forces_points', []) ]
        stresses_vals = [ [y for _, y in pts] for pts in results.get('bar_stresses_points', []) ]
        disp_vals = [ [y * displ_scale for _, y in pts] for pts in results.get('bar_displacements_points', []) ]

        # Вычисляем лимиты для каждого типа графика
        n_ylim = self.compute_y_limits(forces_vals)
        s_ylim = self.compute_y_limits(stresses_vals)
        u_ylim = self.compute_y_limits(disp_vals)

        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
                  "tab:brown", "tab:pink", "tab:olive", "tab:cyan"]

        self.n_canvas.figure.clear()
        ax_n = self.n_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_forces_points', [])):
            xs, ys = zip(*pts)
            xs_mapped = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_n.plot(xs_mapped, ys, label=f"Стержень {i+1}", color=colors[i % len(colors)])

        ax_n.set_title("N(x)")
        ax_n.set_xlabel("x (пикс.ед.)")
        ax_n.set_ylabel("N (Н)")
        ax_n.grid(True)
        ax_n.legend()
        ax_n.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_n.set_ylim(n_ylim)
        self.n_canvas.draw()

        self.sigma_canvas.figure.clear()
        ax_s = self.sigma_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_stresses_points', [])):
            xs, ys = zip(*pts)
            xs_mapped = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_s.plot(xs_mapped, ys, label=f"Стержень {i+1}", color=colors[i % len(colors)])

        ax_s.set_title("σ(x)")
        ax_s.set_xlabel("x (пикс.ед.)")
        ax_s.set_ylabel("σ (Па)")
        ax_s.grid(True)
        ax_s.legend()
        ax_s.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_s.set_ylim(s_ylim)
        self.sigma_canvas.draw()

        self.u_canvas.figure.clear()
        ax_u = self.u_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_displacements_points', [])):
            xs, ys = zip(*pts)
            ys_scaled = [y * displ_scale for y in ys]
            xs_mapped = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_u.plot(xs_mapped, ys_scaled, label=f"Стержень {i+1}", color=colors[i % len(colors)])

        ax_u.set_title("u(x) (масштаб смещений: {:.1f}x)".format(displ_scale))
        ax_u.set_xlabel("x (пикс.ед.)")
        ax_u.set_ylabel("u (м)")
        ax_u.grid(True)
        ax_u.legend()
        ax_u.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_u.set_ylim(u_ylim)
        self.u_canvas.draw()

    def annotate_key_points(self, ax, xs, ys, xs_global):
        key_points = []
        # Начало и конец стержня
        if xs_global:
            key_points.append((xs_global[0], ys[0]))
            key_points.append((xs_global[-1], ys[-1]))
        # Экстремумы
        try:
            max_index = ys.index(max(ys))
            min_index = ys.index(min(ys))
            key_points.append((xs_global[max_index], ys[max_index]))
            key_points.append((xs_global[min_index], ys[min_index]))
        except Exception:
            pass
        # уникальные точки
        unique = []
        tol = 1e-6
        for p in key_points:
            if not any(abs(p[0] - u[0]) < tol and abs(p[1] - u[1]) < tol for u in unique):
                unique.append(p)
        # Отображаем точки
        for x, y in unique:
            ax.plot(x, y, "o", color="red", markersize=4)
            # форматирование надписи
            if abs(y) < 0.01 or abs(y) > 1000:
                label = f"{y:.2e}"
            else:
                label = f"{y:.2f}"
            ax.annotate(
                label,
                xy=(x, y),
                xytext=(5, 5),
                textcoords="offset points",
                ha='left',
                va='bottom',
                fontsize=6,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.7)
            )

    def draw_epures(self, system_data, results, displ_scale=1.0):
        scaled_layout, cum_x, total_visual_width = self.compute_scaled_layout(system_data)
        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
                  "tab:brown", "tab:pink", "tab:olive", "tab:cyan"]

        # Подготовим значения для вычисления лимитов по Y
        forces_vals = [ [y for _, y in pts] for pts in results.get('bar_forces_points', []) ]
        stresses_vals = [ [y for _, y in pts] for pts in results.get('bar_stresses_points', []) ]
        disp_vals = [ [y * displ_scale for _, y in pts] for pts in results.get('bar_displacements_points', []) ]

        n_ylim = self.compute_y_limits(forces_vals)
        s_ylim = self.compute_y_limits(stresses_vals)
        u_ylim = self.compute_y_limits(disp_vals)

        self.epure_n_canvas.figure.clear()
        ax_n = self.epure_n_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_forces_points', [])):
            xs, ys = zip(*pts)
            xs_global = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_n.plot(xs_global, ys, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_n.fill_between(xs_global, ys, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_n, xs, ys, xs_global)

        ax_n.set_title("Эпюра N(x)")
        ax_n.set_xlabel("x (пикс.ед.)")
        ax_n.set_ylabel("N (Н)")
        ax_n.grid(True, linestyle='--', alpha=0.5)
        ax_n.legend(fontsize=8)
        ax_n.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_n.set_ylim(n_ylim)
        self.epure_n_canvas.draw()

        self.epure_sigma_canvas.figure.clear()
        ax_s = self.epure_sigma_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_stresses_points', [])):
            xs, ys = zip(*pts)
            xs_global = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_s.plot(xs_global, ys, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_s.fill_between(xs_global, ys, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_s, xs, ys, xs_global)

        ax_s.set_title("Эпюра σ(x)")
        ax_s.set_xlabel("x (пикс.ед.)")
        ax_s.set_ylabel("σ (Па)")
        ax_s.grid(True, linestyle='--', alpha=0.5)
        ax_s.legend(fontsize=8)
        ax_s.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_s.set_ylim(s_ylim)
        self.epure_sigma_canvas.draw()

        self.epure_u_canvas.figure.clear()
        ax_u = self.epure_u_canvas.figure.add_subplot(111)

        for i, pts in enumerate(results.get('bar_displacements_points', [])):
            xs, ys = zip(*pts)
            ys_scaled = [y * displ_scale for y in ys]
            xs_global = self.map_local_xs_to_global(xs, i, system_data, scaled_layout, cum_x)
            ax_u.plot(xs_global, ys_scaled, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_u.fill_between(xs_global, ys_scaled, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_u, xs, ys_scaled, xs_global)

        ax_u.set_title("Эпюра u(x) (масштаб смещений: {:.1f}x)".format(displ_scale))
        ax_u.set_xlabel("x (пикс.ед.)")
        ax_u.set_ylabel("u (м)")
        ax_u.grid(True, linestyle='--', alpha=0.5)
        ax_u.legend(fontsize=8)
        ax_u.set_xlim(0, total_visual_width if total_visual_width > 0 else 1.0)
        ax_u.set_ylim(u_ylim)
        self.epure_u_canvas.draw()

    def load_calculation(self, calc_data):
        try:
            self.calc_data = calc_data  # сохраняем для дальнейшей работы
            system_data = {
                "Стержни": [
                    [bar["length"], bar.get("cross_section", 1.0), bar.get("modulus_of_elasticity", 1e9)]
                    for bar in calc_data["Bars"]
                ]
            }
            results = {
                "bar_forces_points": [],
                "bar_stresses_points": [],
                "bar_displacements_points": [],
                "displacements": [],
                "graph_table": [],
                "n_nodes": len(calc_data["Nodes"]),
                "fixed_nodes": [0, len(calc_data["Nodes"]) - 1]  # пример, можно уточнить
            }
            total_x = 0.0
            for bar in calc_data["Bars"]:
                xs = [pt["x"] for pt in bar["points"]]
                Ns = [pt["N"] for pt in bar["points"]]
                sigmas = [pt["sigma"] for pt in bar["points"]]
                us = [pt["u"] for pt in bar["points"]]

                results["bar_forces_points"].append(list(zip(xs, Ns)))
                results["bar_stresses_points"].append(list(zip(xs, sigmas)))
                results["bar_displacements_points"].append(list(zip(xs, us)))

                for x, N, u, sigma in zip(xs, Ns, us, sigmas):
                    results["graph_table"].append({
                        "bar": bar["bar_id"],
                        "x": total_x + x,
                        "N": N,
                        "u": u,
                        "sigma": sigma
                    })
                total_x += bar["length"]

            results["displacements"] = [node["u"] for node in calc_data["Nodes"]]
            self.results = results
            self.fill_table(system_data, results)
            self.fill_report(system_data, results)
            self.draw_graphs(system_data, results)
            self.draw_epures(system_data, results)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить расчёт:\n{str(e)}")