from PyQt5.QtWidgets import QGraphicsScene
from bar import Bar


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bars = []
        self.current_x = 0
        self.add_bar(2, 1)
        self.add_bar(1, 3)
        self.add_bar(2, 2)
        self.remove_bar(1)

    def add_bar(self, length, width):
        bar = Bar(self.current_x, (-width * 100 / 2), length * 100, width * 100)
        self.addItem(bar)
        self.bars.append(bar)
        self.current_x += length * 100

    def resize_bar(self, bar_id, new_length, new_width):
        bar_id -= 1
        bar = self.bars[bar_id]
        if new_length or new_width:
            if new_width:
                new_width *= 100
                difference_width = bar.width - new_width
                y = bar.y + difference_width / 2
            else:
                y = None
            if new_length:
                new_length *= 100
                difference_length = bar.length - new_length
                for i in range(bar_id + 1, len(self.bars)):
                    x = self.bars[i].x - difference_length
                    self.bars[i].resize_bar(x, None, None, None)
            bar.resize_bar(None, y, new_length, new_width)

    def remove_bar(self, bar_id):
        bar_id -= 1
        bar = self.bars[bar_id]
        new_length = bar.length
        self.bars.pop(bar_id)
        for i in range(bar_id, len(self.bars)):
            x = self.bars[i].x - new_length
            self.bars[i].resize_bar(x, None, None, None)


