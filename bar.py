from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import QRectF


class Bar(QGraphicsRectItem):
    def __init__(self, x, y, real_width, real_height, scaled_width, scaled_height):
        super().__init__()
        self.x = x
        self.y = y
        self.real_width = real_width
        self.real_height = real_height
        self.scaled_width = scaled_width
        self.scaled_height = scaled_height
        self.setPos(self.x, self.y)
        self.setZValue(3)

    def boundingRect(self):
        return QRectF(0, 0, self.scaled_width, self.scaled_height)

    def paint(self, painter, option, widget=None):
        painter.drawRect(QRectF(0, 0, self.scaled_width, self.scaled_height))

