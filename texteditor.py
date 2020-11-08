from time import sleep
from PyQt5 import QtGui, QtWidgets, QtCore
from typing import List, Callable


class TextEditor(QtWidgets.QPlainTextEdit):

    character_list = {
        "(": ")",
        "[": "]",
        "{": "}",
        "\"": "\"",
        "'": "'"
    }

    def __init__(self):
        super().__init__()
        self.create_text_editor()

    def create_text_editor(self):
        self.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.setLineWrapMode(self.WidgetWidth)

    def keyPressEvent(self, event):
        closing_char = self.character_list.get(event.text())

        if closing_char:
            char_cursor = self.textCursor()
            initial_char_position = char_cursor.position()

            self.insertPlainText(closing_char)
            char_cursor.setPosition(initial_char_position)
            self.setTextCursor(char_cursor)
        super().keyPressEvent(event)
