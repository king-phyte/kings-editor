from time import sleep
from PyQt5 import QtGui, QtWidgets, QtCore
from typing import List, Callable


class LineNumberArea(QtWidgets.QWidget):
    """
    Handles the display of line numbers in the text editor
    """

    def __init__(self, text_editor):
        self.text_editor = text_editor
        super().__init__(self.text_editor)

    def sizeHint(self):
        return QtCore.QSize(self.text_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.text_editor.line_number_area_paint_event(event)


class TextEditor(QtWidgets.QPlainTextEdit):

    character_list = {
        "(": ")",
        "[": "]",
        "{": "}",
        "\"": "\"",
        "'": "'"
    }  # For auto-completion implementation

    def __init__(self):
        super().__init__()
        self.line_number_area = LineNumberArea(self)

    def resizeEvent(self, event):
        cr = self.contentsRect()
        self.line_number_area .setGeometry(QtCore.QRect(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def keyPressEvent(self, event):
        closing_char = self.character_list.get(event.text())

        if closing_char:
            char_cursor = self.textCursor()
            initial_char_position = char_cursor.position()

            self.insertPlainText(closing_char)
            char_cursor.setPosition(initial_char_position)
            self.setTextCursor(char_cursor)
        super().keyPressEvent(event)

    def line_number_area_paint_event(self, event):
        painter = QtGui.QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QtCore.Qt.black)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = QtCore.qRound(self.blockBoundingGeometry(
            block).translated(self.contentOffset()).top())
        bottom = top + QtCore.qRound(self.blockBoundingRect(block).height())

        while block.isValid() and (top <= event.rect().bottom()):
            if (block.isVisible() and bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.setPen(QtCore.Qt.lightGray)
                painter.drawText(0, top, self.line_number_area.width(
                ), self.fontMetrics().height(), QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + \
                QtCore.qRound(self.blockBoundingRect(block).height())
            block_number += 1

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area .scroll(0, dy)
        else:
            self.line_number_area .update(
                0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def line_number_area_width(self) -> int:
        digits = 1
        max_ = max(1, self.blockCount())

        while max_ >= 10:
            max_ /= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance("9" * digits)
        return space

    def update_line_number_area_width(self, new_block_count):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QtWidgets.QTextEdit.ExtraSelection()

            line_color = QtGui.QColor(QtCore.Qt.black).lighter(130)
            selection.format.setBackground(line_color)
            selection.format.setProperty(
                QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)
