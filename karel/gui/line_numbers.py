from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QSize


class LineNumbers(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_numbers_width(), 0)

    def paintEvent(self, event):
        self.editor.line_numbers_paint_event(event)