from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QTextCursor, QPainter, QColor
from PySide6.QtCore import Qt, QRect

from karel.gui.line_numbers import LineNumbers

class CodeEditor(QPlainTextEdit):
    OPENING_TO_CLOSING = {"(": ")"}

    def __init__(self):
        super().__init__()
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self.line_numbers = LineNumbers(self)
        self.blockCountChanged.connect(self._update_line_numbers_width)
        self.updateRequest.connect(self._update_line_numbers)
        self._update_line_numbers_width(0)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._handle_enter(event)
            return

        if event.text() in self.OPENING_TO_CLOSING:
            if self.textCursor().hasSelection():
                self._wrap_selection(event.text(), self.OPENING_TO_CLOSING[event.text()])
            else:
                self._handle_opening_bracket(event.text())
            return

        if event.text() in self.OPENING_TO_CLOSING.values():
            if self._handle_closing_bracket(event.text()):
                return

        if event.key() == Qt.Key_Tab:
            self._indent_lines(add=True)
            return

        if event.key() == Qt.Key_Backtab:
            self._indent_lines(add=False)
            return

        if event.key() == Qt.Key_Slash and event.modifiers() & Qt.ControlModifier:
            self._toggle_comment()
            return

        super().keyPressEvent(event)

    def _selected_block_range(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            start = cursor.selectionStart()
            end = cursor.selectionEnd()
        else:
            start = end = cursor.position()

        doc = self.document()
        start_block = doc.findBlock(start).blockNumber()
        end_block = doc.findBlock(end).blockNumber()
        return start_block, end_block

    def _toggle_comment(self):
        start_block, end_block = self._selected_block_range()
        doc = self.document()

        uncomment = False
        for block_number in range(start_block, end_block + 1):
            text = doc.findBlockByNumber(block_number).text()
            stripped = text.lstrip()
            if stripped:
                uncomment = stripped.startswith("#")
                break

        edit_cursor = self.textCursor()
        edit_cursor.beginEditBlock()

        for block_number in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_number)
            text = block.text()
            leading = len(text) - len(text.lstrip())
            line_cursor = QTextCursor(doc)
            line_cursor.setPosition(block.position() + leading)

            if uncomment:
                if text[leading:leading + 1] == "#":
                    remove_count = 2 if text[leading + 1:leading + 2] == " " else 1
                    line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, remove_count)
                    line_cursor.removeSelectedText()
            else:
                line_cursor.insertText("# ")

        edit_cursor.endEditBlock()

    def _wrap_selection(self, opening, closing):
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        selected_text = cursor.selectedText()

        cursor.beginEditBlock()
        cursor.insertText(opening + selected_text + closing)
        cursor.endEditBlock()

        new_cursor = self.textCursor()
        new_cursor.setPosition(start + len(opening))
        new_cursor.setPosition(end + len(opening), QTextCursor.KeepAnchor)
        self.setTextCursor(new_cursor)

    def _indent_lines(self, add):
        start_block, end_block = self._selected_block_range()
        doc = self.document()

        edit_cursor = self.textCursor()
        edit_cursor.beginEditBlock()

        for block_number in range(start_block, end_block + 1):
            block = doc.findBlockByNumber(block_number)
            line_cursor = QTextCursor(doc)
            line_cursor.setPosition(block.position())

            if add:
                line_cursor.insertText("    ")
            else:
                text = block.text()
                leading_spaces = len(text) - len(text.lstrip(" "))
                remove_count = min(4, leading_spaces)
                if remove_count > 0:
                    line_cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, remove_count)
                    line_cursor.removeSelectedText()

        edit_cursor.endEditBlock()

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

    def line_numbers_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 10 + self.fontMetrics().horizontalAdvance("9") * digits

    def _update_line_numbers_width(self, _):
        self.setViewportMargins(self.line_numbers_width(), 0, 0, 0)

    def _update_line_numbers(self, rect, dy):
        if dy:
            self.line_numbers.scroll(0, dy)
        else:
            self.line_numbers.update(0, rect.y(), self.line_numbers.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self._update_line_numbers_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_numbers.setGeometry(QRect(cr.left(), cr.top(), self.line_numbers_width(), cr.height()))

    def line_numbers_paint_event(self, event):
        painter = QPainter(self.line_numbers)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#777777"))
                painter.drawText(
                    0, int(top), self.line_numbers.width() - 5, self.fontMetrics().height(),
                    Qt.AlignRight, number,
                )
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1