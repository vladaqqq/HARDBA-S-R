from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtWidgets import QGraphicsItem


class Сoncentrated_loads(QGraphicsItem):
    width = 30
    height = 30

    def __init__(self, x, y, force):
        super().__init__()
        self.x = x
        self.y = y
        self.force = force
        self.setPos(self.x, self.y - self.height // 2)
        self.setZValue(2)

    def boundingRect(self):
        return QRectF(0, 0, self.width + 3, self.height)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(3)
        painter.setPen(pen)
        painter.drawLine(QLineF(1.5, self.height // 2, self.width, self.height // 2))
        if self.force < 0:
            painter.drawLine(QLineF(1.5, self.height // 2, 10, self.height // 2 - 5))
            painter.drawLine(QLineF(1.5, self.height // 2, 10, self.height // 2 + 5))
        else:
            painter.drawLine(QLineF(1.5 + self.width, self.height // 2, 1.5 + self.width - 10, self.height // 2 - 5))
            painter.drawLine(QLineF(1.5 + self.width, self.height // 2, 1.5 + self.width - 10, self.height // 2 + 5))


class Distributed_loads(QGraphicsItem):
    height = 30

    def __init__(self, x, y, width, force):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.force = force
        self.setPos(self.x, self.y - self.height // 2)
        self.setZValue(1)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(0, 255, 0))
        pen.setWidth(2)
        painter.setPen(pen)
        current_x = 1
        width_indent = 10
        length_arrow = 15
        arrow_count = (self.width + width_indent) // (length_arrow + width_indent)
        for i in range(int(arrow_count)):
            painter.drawLine(QLineF(current_x, self.height // 2, current_x + length_arrow, self.height // 2))
            if self.force < 0:
                painter.drawLine(QLineF(current_x, self.height // 2, current_x + 5, self.height // 2 - 5))
                painter.drawLine(QLineF(current_x, self.height // 2, current_x + 5, self.height // 2 + 5))
            else:
                painter.drawLine(QLineF(current_x + length_arrow, self.height // 2, current_x + length_arrow - 5,
                                        self.height // 2 - 5))
                painter.drawLine(QLineF(current_x + length_arrow, self.height // 2, current_x + length_arrow - 5,
                                        self.height // 2 + 5))
            current_x += length_arrow + width_indent