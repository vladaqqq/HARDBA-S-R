from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtGui import QColor, QPen, QFont
from PyQt5.QtWidgets import QGraphicsItem


class BarInfo(QGraphicsItem):
    def __init__(self, x, y, real_width, scaled_width, bar_id, difference_height):
        super().__init__()
        self.x = x
        self.y = y
        self.real_width = real_width
        self.scaled_width = scaled_width
        self.difference_height = difference_height
        self.bar_id = bar_id
        self.setPos(self.x, self.y)

    def boundingRect(self):
        return QRectF(0, 0, self.scaled_width + 50, self.difference_height + 125)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(0, 0, 0))
        font = QFont()
        font.setPixelSize(16)
        painter.setFont(font)
        pen.setWidth(1)
        painter.setPen(pen)
        if self.bar_id == 1:
            painter.drawLine(QLineF(10, 0, 10, self.difference_height + 20))
            pen.setColor(QColor(0, 255, 0))
            painter.setPen(pen)
            painter.drawRect(QRectF(0,  self.difference_height + 20, 20, 30))
            painter.drawText(QRectF(6, self.difference_height + 25, 20, 20), '1')
            pen.setColor(QColor(0, 0, 0))
            painter.setPen(pen)
            painter.drawLine(QLineF(10, self.difference_height + 50, 10, self.difference_height + 119))
        painter.drawLine(QLineF(self.scaled_width + 10, 0, self.scaled_width + 10, self.difference_height + 20))
        pen.setColor(QColor(0, 255, 0))
        painter.setPen(pen)
        painter.drawRect(QRectF(self.scaled_width, self.difference_height + 20, 20, 30))
        painter.drawText(QRectF(self.scaled_width + 6, self.difference_height + 25, 20, 20), str(self.bar_id + 1))
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawLine(QLineF(self.scaled_width + 10, self.difference_height + 50, self.scaled_width + 10,
                                self.difference_height + 119))
        painter.drawLine(QLineF(10, self.difference_height + 119, self.scaled_width + 10, self.difference_height + 119))
        painter.drawLine(QLineF(10, self.difference_height + 119, 15, self.difference_height + 114))
        painter.drawLine(QLineF(10, self.difference_height + 119, 15, self.difference_height + 124))
        painter.drawLine(QLineF(self.scaled_width + 10, self.difference_height + 119, self.scaled_width + 5,
                                self.difference_height + 114))
        painter.drawLine(QLineF(self.scaled_width + 10, self.difference_height + 119, self.scaled_width + 5,
                                self.difference_height + 124))
        painter.drawText(QRectF((self.scaled_width + 10) // 2, self.difference_height + 100, 20, 20), str(int(self.real_width)))

class BarNum(QGraphicsItem):
    def __init__(self, bar_id, x, y):
        super().__init__()
        self.bar_id = bar_id
        self.x = x
        self.y = y
        self.setPos(self.x - 20, self.y)

    def boundingRect(self):
        return QRectF(0, 0, 40, 40)

    def paint(self, painter, option, widget=None):
        pen = QPen(QColor(255, 0, 0))
        font = QFont()
        font.setPixelSize(16)
        font.setWeight(QFont.DemiBold)
        painter.setPen(pen)
        painter.setFont(font)
        painter.drawEllipse(QRectF(0, 0, 40, 40))
        painter.drawText(QRectF(15, 10, 20, 20), str(self.bar_id)) #


