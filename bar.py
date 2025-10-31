from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import QRectF


class Bar(QGraphicsRectItem):
    def __init__(self, x, y, length, width):
        super().__init__(x, y, length, width)
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.resize_bar(x, y, length, width)

    def resize_bar(self, x, y, length, width):
        if length:
            self.length = length
        if width:
            self.width = width
        if x:
            self.x = x
        if y:
            self.y = y
        self.setRect(QRectF(self.x, self.y, self.length, self.width))
