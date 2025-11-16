from PyQt5.QtWidgets import QMessageBox, QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import tempfile
import os
from datetime import datetime


class PDFReportGenerator:
    def __init__(self, main_window):
        self.main_window = main_window
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
            self.font_name = 'DejaVuSans'
        except:
            try:
                pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
                self.font_name = 'Arial'
            except:
                self.font_name = 'Helvetica'

    def generate_report(self):
        try:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "Сохранить отчет в PDF",
                f"Расчет_системы_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf",
                "PDF Files (*.pdf)",
                options=options
            )

            if not file_name:
                return

            doc = SimpleDocTemplate(file_name, pagesize=A4)
            story = []

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.font_name,
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=self.font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=self.font_name,
                fontSize=10
            )
            story.append(Paragraph("РАСЧЕТ СТЕРЖНЕВОЙ СИСТЕМЫ", title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Результаты расчета методом перемещений", heading_style))
            story.append(Paragraph(f"Дата расчета: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
            story.append(Spacer(1, 30))
            story.append(Paragraph("1. ИСХОДНЫЕ ДАННЫЕ", heading_style))
            system_data = self.main_window.collect_info()
            bars_count = len(system_data.get("Стержни", []))
            concentrated_loads_count = len(system_data.get("Сосредоточенные нагрузки", []))
            distributed_loads_count = len(system_data.get("Распределенные нагрузки", []))
            info_data = [
                ["Параметр", "Значение"],
                ["Количество стержней", str(bars_count)],
                ["Количество сосредоточенных нагрузок", str(concentrated_loads_count)],
                ["Количество распределенных нагрузок", str(distributed_loads_count)]
            ]
            info_table = Table(info_data, colWidths=[8 * cm, 8 * cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 15))
            left_fixed = self.main_window.viewer.checkbox.left_checkbox.isChecked()
            right_fixed = self.main_window.viewer.checkbox.right_checkbox.isChecked()
            fixed_data = [
                ["Заделка", "Состояние"],
                ["Левая заделка", "Установлена" if left_fixed else "Отсутствует"],
                ["Правая заделка", "Установлена" if right_fixed else "Отсутствует"]
            ]
            fixed_table = Table(fixed_data, colWidths=[8 * cm, 8 * cm])
            fixed_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
            ]))

            story.append(fixed_table)
            story.append(Spacer(1, 20))
            if bars_count > 0:
                story.append(Paragraph("Таблица стержней:", heading_style))
                bars_data = [["№", "Длина (м)", "Площадь (м²)", "Модуль упругости (Па)", "Допускаемое напряжение (Па)"]]
                for i, bar in enumerate(system_data["Стержни"]):
                    bars_data.append([
                        str(i + 1),
                        f"{bar[0]:.3f}" if len(bar) > 0 else "0",
                        f"{bar[1]:.3e}" if len(bar) > 1 else "0",
                        f"{bar[2]:.3e}" if len(bar) > 2 else "0",
                        f"{bar[3]:.3e}" if len(bar) > 3 else "250e6"
                    ])
                bars_table = Table(bars_data, colWidths=[1.5 * cm, 3 * cm, 3 * cm, 4 * cm, 4 * cm])
                bars_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
                ]))

                story.append(bars_table)
                story.append(Spacer(1, 20))
            if concentrated_loads_count > 0:
                story.append(Paragraph("Сосредоточенные нагрузки:", heading_style))
                conc_data = [["№ узла", "Сила (Н)"]]

                for load in system_data["Сосредоточенные нагрузки"]:
                    conc_data.append([str(load[0]), f"{load[1]:.3e}"])

                conc_table = Table(conc_data, colWidths=[4 * cm, 4 * cm])
                conc_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
                ]))

                story.append(conc_table)
                story.append(Spacer(1, 20))
            if distributed_loads_count > 0:
                story.append(Paragraph("Распределенные нагрузки:", heading_style))
                dist_data = [["№ стержня", "Интенсивность (Н/м)"]]
                for load in system_data["Распределенные нагрузки"]:
                    dist_data.append([str(load[0]), f"{load[1]:.3e}"])

                dist_table = Table(dist_data, colWidths=[4 * cm, 4 * cm])
                dist_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
                ]))

                story.append(dist_table)
                story.append(Spacer(1, 20))
            story.append(Paragraph("2. РЕЗУЛЬТАТЫ РАСЧЕТА", heading_style))

            if hasattr(self.main_window.process_tab, 'results') and self.main_window.process_tab.results:
                results = self.main_window.process_tab.results
                story.append(Paragraph("Перемещения узлов:", heading_style))
                displacements_data = [["№ узла", "Перемещение u (м)"]]
                for i, u in enumerate(results['displacements']):
                    displacements_data.append([str(i + 1), f"{u:.3e}"])
                disp_table = Table(displacements_data, colWidths=[4 * cm, 6 * cm])
                disp_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
                ]))
                story.append(disp_table)
                story.append(Spacer(1, 20))
                story.append(Paragraph("Результаты расчета по точкам:", heading_style))
                calc_data = [["Стержень", "x (м)", "N (Н)", "u (м)", "σ (Па)"]]
                table_widget = self.main_window.process_tab.results_table
                for row in range(table_widget.rowCount()):
                    row_data = []
                    for col in range(table_widget.columnCount()):
                        item = table_widget.item(row, col)
                        row_data.append(item.text() if item else "")
                    calc_data.append(row_data)

                calc_table = Table(calc_data, colWidths=[2 * cm, 2.5 * cm, 3.5 * cm, 3.5 * cm, 4.5 * cm])
                calc_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name),
                    ('FONTSIZE', (0, 0), (-1, -1), 7),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 0.7, colors.black),
                ]))
                story.append(calc_table)
                story.append(Spacer(1, 20))

            story.append(Paragraph("3. ГРАФИКИ И ЭПЮРЫ", heading_style))
            temp_files = []

            try:
                construction_file = self.save_construction_to_image()
                if construction_file:
                    temp_files.append(construction_file)
                    story.append(Paragraph("Расчетная схема конструкции:", heading_style))
                    story.append(Image(construction_file, width=15 * cm, height=8 * cm))
                    story.append(Spacer(1, 15))

                # График N(x)
                if hasattr(self.main_window.postprocess_tab, 'n_canvas'):
                    n_file = self.save_figure_to_temp(self.main_window.postprocess_tab.n_canvas.figure, "N_x")
                    temp_files.append(n_file)
                    story.append(Paragraph("График продольных сил N(x):", heading_style))
                    story.append(Image(n_file, width=14 * cm, height=7 * cm))
                    story.append(Spacer(1, 10))

                # График σ(x)
                if hasattr(self.main_window.postprocess_tab, 'sigma_canvas'):
                    sigma_file = self.save_figure_to_temp(self.main_window.postprocess_tab.sigma_canvas.figure,
                                                          "sigma_x")
                    temp_files.append(sigma_file)
                    story.append(Paragraph("График напряжений σ(x):", heading_style))
                    story.append(Image(sigma_file, width=14 * cm, height=7 * cm))
                    story.append(Spacer(1, 10))

                # График u(x)
                if hasattr(self.main_window.postprocess_tab, 'u_canvas'):
                    u_file = self.save_figure_to_temp(self.main_window.postprocess_tab.u_canvas.figure, "u_x")
                    temp_files.append(u_file)
                    story.append(Paragraph("График перемещений u(x):", heading_style))
                    story.append(Image(u_file, width=14 * cm, height=7 * cm))
                    story.append(Spacer(1, 10))

                # Эпюра N(x)
                if hasattr(self.main_window.postprocess_tab, 'epure_n_canvas'):
                    epure_n_file = self.save_figure_to_temp(self.main_window.postprocess_tab.epure_n_canvas.figure,
                                                            "epure_N_x")
                    temp_files.append(epure_n_file)
                    story.append(Paragraph("Эпюра продольных сил N(x):", heading_style))
                    story.append(Image(epure_n_file, width=14 * cm, height=7 * cm))
                    story.append(Spacer(1, 10))

                # Эпюра σ(x)
                if hasattr(self.main_window.postprocess_tab, 'epure_sigma_canvas'):
                    epure_sigma_file = self.save_figure_to_temp(
                        self.main_window.postprocess_tab.epure_sigma_canvas.figure, "epure_sigma_x")
                    temp_files.append(epure_sigma_file)
                    story.append(Paragraph("Эпюра напряжений σ(x):", heading_style))
                    story.append(Image(epure_sigma_file, width=14 * cm, height=7 * cm))
                    story.append(Spacer(1, 10))

                # Эпюра u(x)
                if hasattr(self.main_window.postprocess_tab, 'epure_u_canvas'):
                    epure_u_file = self.save_figure_to_temp(self.main_window.postprocess_tab.epure_u_canvas.figure,
                                                            "epure_u_x")
                    temp_files.append(epure_u_file)
                    story.append(Paragraph("Эпюра перемещений u(x):", heading_style))
                    story.append(Image(epure_u_file, width=14 * cm, height=7 * cm))

            except Exception as e:
                story.append(Paragraph(f"Ошибка при добавлении графиков: {str(e)}", normal_style))
            doc.build(story)
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except:
                    pass

            QMessageBox.information(self.main_window, "Успех", f"Отчет успешно сохранен в:\n{file_name}")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Ошибка", f"Не удалось создать отчет:\n{str(e)}")

    def save_figure_to_temp(self, figure, prefix):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', prefix=prefix)
        figure.savefig(temp_file.name, dpi=150, bbox_inches='tight', format='png')
        return temp_file.name

    def save_construction_to_image(self):
        try:
            # Простой способ - делаем скриншот виджета
            viewer = self.main_window.viewer
            pixmap = viewer.grab()

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', prefix='construction')
            pixmap.save(temp_file.name, 'PNG')
            return temp_file.name

        except Exception as e:
            print(f"Ошибка сохранения конструкции: {e}")
            return None