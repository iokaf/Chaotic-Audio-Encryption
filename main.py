import sys

from PyQt6.QtWidgets import QApplication

from src.main_app import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())