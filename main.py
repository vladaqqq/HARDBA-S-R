import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidget
from main_window import MainWindow


if __name__ =="__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("SAPR-BAR")
    window.resize(1280,720)
    window.show()
    sys.exit(app.exec_())