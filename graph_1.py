from PyQt5.QtWidgets import QGraphicsView
from graphic_scene import GraphicsScene
from chekbox_group import CheckboxBTN

class GraphicsViewer(QGraphicsView):
    def __init__(self, parent = None):
        super().__init__()
        self.scene = GraphicsScene(self)
        self.setStyleSheet("background-color: white;")
        self.setScene(self.scene)
        self.setMinimumHeight(900)
        self.parent = parent
        self.checkbox = CheckboxBTN(self)

