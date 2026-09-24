from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt


class CodeEditor(QPlainTextEdit):
    OPENING_TO_CLOSING = {"(": ")"}

    def __init__(self):
        super().__init__()
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._handle_enter(event)
            return

        if event.text() in self.OPENING_TO_CLOSING:
            self._handle_opening_bracket(event.text())
            return

        if event.text() in self.OPENING_TO_CLOSING.values():
            if self._handle_closing_bracket(event.text()):
                return

        super().keyPressEvent(event)

    def _handle_enter(self, event):
        current_line = self.textCursor().block().text()
        indent = len(current_line) - len(current_line.lstrip())
        if current_line.strip().endswith(":"):
            indent += 4
        super().keyPressEvent(event)  # enter
        self.insertPlainText(indent * " ")  # ident

    def _handle_opening_bracket(self, opening):
        closing = self.OPENING_TO_CLOSING[opening]
        cursor = self.textCursor()
        cursor.insertText(opening + closing)
        cursor.movePosition(QTextCursor.Left)
        self.setTextCursor(cursor)

    def _handle_closing_bracket(self, closing):
        cursor = self.textCursor()
        pos_in_block = cursor.positionInBlock()
        block_text = cursor.block().text()

        if pos_in_block < len(block_text) and block_text[pos_in_block] == closing:
            cursor.movePosition(QTextCursor.Right)
            self.setTextCursor(cursor)
            return True
        return False