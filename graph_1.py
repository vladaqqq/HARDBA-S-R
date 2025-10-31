from PyQt5.QtWidgets import QGraphicsView
from graphic_scene import GraphicsScene


class GraphicsViewer(QGraphicsView):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.scene = GraphicsScene(self)
        self.setStyleSheet("background-color: white;")
        self.setScene(self.scene)
        self.setMinimumHeight(900)
