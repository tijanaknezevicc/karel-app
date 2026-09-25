import sys
import ctypes

if sys.platform == "win32":
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("karel.diplomski.app")

from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from karel.gui.main_window import MainWindow

app = QApplication(sys.argv)
app.setWindowIcon(QIcon(str(Path(__file__).parent / "karel" / "gui" / "assets" / "lefrog.png")))

window = MainWindow()
window.show()
sys.exit(app.exec())