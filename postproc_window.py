from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QTabWidget, QTextEdit
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class PostProcessorWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.results = None
        self.create_widgets()
        self.setup_layout()

    def create_widgets(self):
        self.tabs = QTabWidget()
        self.calc_tab = QWidget()
        self.graph_tab = QTabWidget()
        self.epure_tab = QTabWidget()
        self.results_table = QTableWidget()
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)

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
        calc_layout.addWidget(self.results_table)
        calc_layout.addWidget(self.report_text)
        self.calc_tab.setLayout(calc_layout)
        self.tabs.addTab(self.calc_tab, "Расчёты")
        self.tabs.addTab(self.graph_tab, "Графики")
        self.tabs.addTab(self.epure_tab, "Эпюры")

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

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

    def draw_graphs(self, system_data, results):
        bars_data = system_data["Стержни"]
        # N(x)
        self.n_canvas.figure.clear()
        ax = self.n_canvas.figure.add_subplot(111)
        for i, points in enumerate(results['bar_forces_points']):
            xs, ys = zip(*points)
            ax.plot(xs, ys, label=f"Стержень {i+1}")
        ax.set_title("N(x)")
        ax.set_xlabel("x (м)")
        ax.set_ylabel("N (Н)")
        ax.grid(True)
        ax.legend()
        self.n_canvas.draw()
        # σ(x)
        self.sigma_canvas.figure.clear()
        ax = self.sigma_canvas.figure.add_subplot(111)
        for i, points in enumerate(results['bar_stresses_points']):
            xs, ys = zip(*points)
            ax.plot(xs, ys, label=f"Стержень {i+1}")
        ax.set_title("σ(x)")
        ax.set_xlabel("x (м)")
        ax.set_ylabel("σ (Па)")
        ax.grid(True)
        ax.legend()
        self.sigma_canvas.draw()
        # u(x)
        self.u_canvas.figure.clear()
        ax = self.u_canvas.figure.add_subplot(111)
        for i, points in enumerate(results['bar_displacements_points']):
            xs, ys = zip(*points)
            ax.plot(xs, ys, label=f"Стержень {i+1}")
        ax.set_title("u(x)")
        ax.set_xlabel("x (м)")
        ax.set_ylabel("u (м)")
        ax.grid(True)
        ax.legend()
        self.u_canvas.draw()

    def annotate_key_points(self, ax, xs, ys, xs_global):
        key_points = []
        key_points.append((xs_global[0], ys[0]))
        mid_index = len(xs) // 2
        key_points.append((xs_global[mid_index], ys[mid_index]))
        key_points.append((xs_global[-1], ys[-1]))
        max_index = ys.index(max(ys))
        min_index = ys.index(min(ys))
        key_points.append((xs_global[max_index], ys[max_index]))
        key_points.append((xs_global[min_index], ys[min_index]))
        for i in range(len(xs) - 1):
            y1 = ys[i]
            y2 = ys[i + 1]
            if y1 == 0:
                key_points.append((xs_global[i], 0))
            if y1 * y2 < 0:
                x1g = xs_global[i]
                x2g = xs_global[i + 1]
                x_zero = x1g + (0 - y1) * (x2g - x1g) / (y2 - y1)
                key_points.append((x_zero, 0))
        unique = []
        for p in key_points:
            if p not in unique:
                unique.append(p)
        for x, y in unique:
            ax.plot(x, y, "o", color="red", markersize=4)
            ax.annotate(f"{y:.2e}", xy=(x, y), xytext=(0, 5),
                        textcoords="offset points", ha="center", fontsize=8)

    def draw_epures(self, system_data, results, scale=1.0):
        bars_data = system_data["Стержни"]
        colors = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple",
                  "tab:brown", "tab:pink", "tab:olive", "tab:cyan"]

        # N(x)
        self.epure_n_canvas.figure.clear()
        ax_n = self.epure_n_canvas.figure.add_subplot(111)
        total_x = 0.0
        for i, points in enumerate(results['bar_forces_points']):
            xs, ys = zip(*points)
            xs_global = [x + total_x for x in xs]
            ax_n.plot(xs_global, ys, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_n.fill_between(xs_global, ys, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_n, xs, ys, xs_global)
            total_x += bars_data[i][0]
        ax_n.set_title("Эпюра N(x)")
        ax_n.set_xlabel("x (м)")
        ax_n.set_ylabel("N (Н)")
        ax_n.grid(True, linestyle='--', alpha=0.5)
        ax_n.legend(fontsize=8)
        self.epure_n_canvas.draw()

        # σ(x)
        self.epure_sigma_canvas.figure.clear()
        ax_s = self.epure_sigma_canvas.figure.add_subplot(111)
        total_x = 0.0
        for i, points in enumerate(results['bar_stresses_points']):
            xs, ys = zip(*points)
            xs_global = [x + total_x for x in xs]
            ax_s.plot(xs_global, ys, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_s.fill_between(xs_global, ys, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_s, xs, ys, xs_global)
            total_x += bars_data[i][0]
        ax_s.set_title("Эпюра σ(x)")
        ax_s.set_xlabel("x (м)")
        ax_s.set_ylabel("σ (Па)")
        ax_s.grid(True, linestyle='--', alpha=0.5)
        ax_s.legend(fontsize=8)
        self.epure_sigma_canvas.draw()

        # u(x)
        self.epure_u_canvas.figure.clear()
        ax_u = self.epure_u_canvas.figure.add_subplot(111)
        total_x = 0.0
        for i, points in enumerate(results['bar_displacements_points']):
            xs, ys = zip(*points)
            xs_global = [x + total_x for x in xs]
            ys_scaled = [y * scale for y in ys]
            ax_u.plot(xs_global, ys_scaled, color=colors[i % len(colors)], label=f"Стержень {i + 1}")
            ax_u.fill_between(xs_global, ys_scaled, 0, color=colors[i % len(colors)], alpha=0.2)
            self.annotate_key_points(ax_u, xs, ys_scaled, xs_global)
            total_x += bars_data[i][0]
        ax_u.set_title("Эпюра u(x)")
        ax_u.set_xlabel("x (м)")
        ax_u.set_ylabel("u (м)")
        ax_u.grid(True, linestyle='--', alpha=0.5)
        ax_u.legend(fontsize=8)
        self.epure_u_canvas.draw()
