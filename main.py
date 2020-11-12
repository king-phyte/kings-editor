from time import sleep
from PyQt5 import QtGui, QtWidgets, QtCore
from typing import List, Callable
from thread import MyThread
from texteditor import TextEditor
from settings import Settings, Formatting


class MainWindow(QtWidgets.QMainWindow):

    current_file = ""

    # A workaround for the encapsulated save function in create_menu_bar
    save: List[Callable] = []

    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self) -> None:
        """
        Sets up the UI and builds the window
        """
        QtCore.QCoreApplication.setOrganizationName("King Inc")
        QtCore.QCoreApplication.setApplicationName("King's Editor")
        QtCore.QCoreApplication.setApplicationVersion("0.1.1")

        self.window_title = "untitled[*] - King's Editor"
        icon = QtGui.QIcon("./svgs/dragon.svg")
        min_width, min_height = 800, 600
        self.setWindowTitle(self.window_title)
        self.setMinimumSize(min_width, min_height)
        self.setWindowIcon(icon)
        self.read_settings()
        self.create_menu_bar()
        self.create_text_editor()
        self.create_status_bar()

        QtGui.QGuiApplication.setFallbackSessionManagementEnabled(False)
        self.setUnifiedTitleAndToolBarOnMac(True)

        self.set_current_file("")

        self.show()

    def create_menu_bar(self) -> None:
        """
        Creates the menu bar
        """

        self.menu_bar = self.menuBar()

        file_menu = self.menu_bar.addMenu("File")

        def new_file():
            if (self.maybe_save()):
                self.text_editor.clear()
                self.set_current_file("")

        new_file_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/file-alt.svg"), "New File", self)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(new_file)

        def new_window():
            MainWindow()

        new_window_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/window-restore.svg"), "New Window", self)
        new_window_action.setShortcut("Ctrl+Shift+N")
        new_window_action.triggered.connect(new_window)

        def open_file():
            if (self.maybe_save()):
                filename = QtWidgets.QFileDialog.getOpenFileName(self)
                if not filename == "":
                    self.load_file(filename)

        open_file_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/file-import.svg"), "Open File", self)
        open_file_action.setShortcut("Ctrl+O")
        open_file_action.triggered.connect(open_file)

        def save() -> bool:
            """
            Saves a pre-exisiting file.
            """
            if self.current_file == "":
                return save_as()
            else:
                return self.save_file(self.current_file)

        self.save.append(save)

        save_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/save.svg"), "Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(save)

        def save_as() -> bool:
            dialog = QtWidgets.QFileDialog(self)
            dialog.setWindowModality(QtCore.Qt.WindowModal)
            dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)

            if (dialog.exec_() != QtWidgets.QDialog.Accepted):
                return False
            return self.save_file(filename=dialog.selectedFiles())

        save_as_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/file-export.svg"), "Save as", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(save_as)

        def autosave():
            if autosave_action.isChecked():
                self.thread = MyThread()
                if not self.thread.isRunning():
                    self.thread.start()
                self.thread.value.connect(lambda num: save())
            else:
                self.thread.autosave_enabled = False

        autosave_action = QtWidgets.QAction("Autosave", self)
        autosave_action.setShortcut("Ctrl+Alt+S")
        autosave_action.setCheckable(True)
        autosave_action.setChecked(False)
        autosave_action.triggered.connect(lambda: autosave())

        settings_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/cogs.svg"), "Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)

        exit_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/times.svg"), "Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)

        file_actions = [new_file_action, new_window_action, "sep",
                        open_file_action, "sep",
                        save_action, save_as_action, autosave_action, "sep",
                        settings_action, "sep",
                        exit_action]

        for action in file_actions:
            if action == "sep":
                file_menu.addSeparator()
                continue
            file_menu.addAction(action)

        edit_menu = self.menu_bar.addMenu("Edit")

        undo_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/undo-alt.svg"), "Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(lambda: self.text_editor.undo())

        redo_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/redo-alt.svg"), "Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(lambda: self.text_editor.redo())

        copy_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/copy.svg"), "Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(lambda: self.text_editor.copy())

        cut_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/cut.svg"), "Cut", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(lambda: self.text_editor.cut())

        paste_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/paste.svg"), "Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(lambda: self.text_editor.paste())

        delete_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/trash-alt.svg"), "Delete", self)
        delete_action.setShortcut("Del")

        search_with_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/question.svg"), "Search with DDG", self)
        search_with_action.setShortcut("Ctrl+?")

        find_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/search.svg"), "Find", self)
        find_action.setShortcut("Ctrl+F")

        replace_action = QtWidgets.QAction("Replace", self)
        replace_action.setShortcut("Ctrl+H")

        goto_action = QtWidgets.QAction("Go to...", self)
        goto_action.setShortcut("Ctrl+G")

        toggle_line_comment = QtWidgets.QAction(
            QtGui.QIcon("./svgs/hashtag.svg"), "Toggle line comment", self)
        toggle_line_comment.setShortcut("Ctrl+/")

        toggle_block_comment = QtWidgets.QAction("Toggle block comment", self)
        toggle_block_comment.setShortcut("Ctrl+Shift+A")

        edit_actions = [undo_action, redo_action, "sep",
                        copy_action, cut_action, paste_action, delete_action, "sep",
                        search_with_action, "sep",
                        find_action, replace_action, goto_action]

        for action in edit_actions:
            if action == "sep":
                edit_menu.addSeparator()
                continue
            edit_menu.addAction(action)

        selection_menu = self.menu_bar.addMenu("Selection")

        select_all_action = QtWidgets.QAction("Select all", self)
        select_all_action.setShortcut("Ctrl+A")

        duplicate_selection = QtWidgets.QAction("Duplicate selection", self)
        duplicate_selection.setShortcut("Ctrl+Alt+D")

        copy_line_up = QtWidgets.QAction("Copy line up", self)
        copy_line_down = QtWidgets.QAction("Copy line down", self)

        move_line_up = QtWidgets.QAction("Move line up", self)
        move_line_down = QtWidgets.QAction("Move line down", self)

        selection_actions = [select_all_action, "sep",
                             duplicate_selection, "sep",
                             copy_line_up, copy_line_down, "sep",
                             move_line_up, move_line_down]

        for action in selection_actions:
            if action == "sep":
                selection_menu.addSeparator()
                continue
            selection_menu.addAction(action)

        view_menu = self.menu_bar.addMenu("View")

        def word_wrap():
            if word_wrap_action.isChecked():
                self.text_editor.setWordWrapMode(
                    QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
                return
            self.text_editor.setWordWrapMode(QtGui.QTextOption.NoWrap)

        word_wrap_action = QtWidgets.QAction("Word wrap", self)
        word_wrap_action.setShortcut("Alt+Z")
        word_wrap_action.setCheckable(True)
        word_wrap_action.triggered.connect(word_wrap)

        def fullscreen_handler():
            availableGeometry = self.screen().availableGeometry()

            if fullscreen_action.isChecked() and (not self.isFullScreen()):
                self.resize(availableGeometry.width(),
                            availableGeometry.height())
                return
            self.resize(800, 600)
            self.move((availableGeometry.width() - self.width()) / 2,
                      (availableGeometry.height() - self.height())/2)

        fullscreen_action = QtWidgets.QAction("Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(fullscreen_handler)

        page_layout_action = QtWidgets.QAction("Page layout", self)

        split_editor_action = QtWidgets.QAction("Split editor", self)

        status_bar_action = QtWidgets.QAction("Status bar", self)
        status_bar_action.setCheckable(True)
        status_bar_action.setChecked(True)
        status_bar_action.triggered.connect(lambda: self.status_bar.setVisible(
            True) if status_bar_action.isChecked() else self.status_bar.setVisible(False))

        view_actions = [word_wrap_action, fullscreen_action, "sep",
                        page_layout_action, split_editor_action, status_bar_action]

        for action in view_actions:
            if action == "sep":
                view_menu.addSeparator()
                continue
            view_menu.addAction(action)

        help_menu = self.menu_bar.addMenu("Help")

        view_help_action = QtWidgets.QAction("View help", self)
        view_help_action.setShortcut("F1")

        documentation_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/table.svg"), "Documentation", self)

        release_notes_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/list.svg"), "Release notes", self)

        keybd_shortcut = QtWidgets.QAction(QtGui.QIcon(
            "./svgs/toolbox.svg"), "Keyboard shortcut reference", self)

        tips_and_tricks_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/info.svg"), "Tips and tricks", self)

        join_us_action = QtWidgets.QAction(QtGui.QIcon(
            "./svgs/twitter.svg"), "Join us on twitter", self)

        feature_request_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/inbox.svg"), "Feature request", self)

        report_issue_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/sad-tear.svg"), "Report issue", self)

        view_license_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/thumbs-up.svg"), "View license", self)

        check_for_updates_action = QtWidgets.QAction("Check for updates", self)

        send_feeback_action = QtWidgets.QAction(
            QtGui.QIcon("./svgs/medal.svg"), "Send feedback", self)

        def about_handler():
            about = self.read_file("about.txt")

            message = QtWidgets.QMessageBox()
            message.about(self, "About King's Editor", about)

        about_action = QtWidgets.QAction(QtGui.QIcon(
            "./svgs/info-circle.svg"), "About King's Editor", self)
        about_action.triggered.connect(about_handler)

        help_actions = [view_help_action, documentation_action, release_notes_action, keybd_shortcut, tips_and_tricks_action, join_us_action,
                        feature_request_action, report_issue_action, view_license_action, check_for_updates_action, send_feeback_action, about_action]

        for action in help_actions:
            help_menu.addAction(action)

        toolbar = self.addToolBar("Toolbar")
        toolbar.addAction(new_file_action)
        toolbar.addAction(save_action)
        toolbar.addAction(copy_action)
        toolbar.addAction(cut_action)
        toolbar.addAction(paste_action)
        toolbar.addAction(undo_action)
        toolbar.addAction(redo_action)

        self.setMenuBar(self.menu_bar)

    def create_text_editor(self):
        self.text_editor = TextEditor()
        self.setCentralWidget(self.text_editor)
        self.text_editor.setTabStopDistance(QtGui.QFontMetricsF.horizontalAdvance(
            QtGui.QFontMetricsF(QtGui.QFont("Arial")), " ") * self.tab_size)
        self.text_editor.cursorPositionChanged.connect(
            self.update_cursor_position)
        self.text_editor.textChanged.connect(self.document_was_modified)
        self.text_editor.setLineWrapMode(self.text_editor.NoWrap)
        self.text_editor.setLineWrapMode(self.text_editor.WidgetWidth)
        self.text_editor.blockCountChanged.connect(
            self.text_editor.update_line_number_area_width)
        self.text_editor.updateRequest.connect(
            self.text_editor.update_line_number_area)
        self.text_editor.update_line_number_area_width(0)

        self.text_editor.setFocus()

    def document_was_modified(self):
        self.setWindowModified(self.text_editor.document().isModified())

    def update_cursor_position(self):
        cursor = self.text_editor.textCursor()

        line_number = cursor.blockNumber() + 1

        column_number = cursor.columnNumber()

        self.status_bar.showMessage(
            f"Line {line_number} | Col {column_number}")

    def create_status_bar(self):
        cursor = self.text_editor.textCursor()

        line_number = cursor.blockNumber() + 1

        column_number = cursor.columnNumber()

        self.tab_size = self.updated_tab_size()

        self.status_bar = self.statusBar()

        def space_handler():
            self.open_settings()
            self.text_editor.setTabStopDistance(QtGui.QFontMetricsF.horizontalAdvance(
                QtGui.QFontMetricsF(QtGui.QFont("Arial")), " ") * self.tab_size)
            spaces.setText(f"Spaces: {self.tab_size}")
            self.text_editor.setFocus()

        spaces = QtWidgets.QPushButton(f"Spaces: {self.tab_size}")
        spaces.setStyleSheet("border: none")
        spaces.clicked.connect(space_handler)
        self.status_bar.addPermanentWidget(spaces)
        self.status_bar.showMessage("Ready")
        self.status_bar.showMessage(
            f"Line {line_number} | Col {column_number}")

    def read_file(self, filename) -> str:
        text_in_file = ""

        with open(filename) as file:
            for line in file:
                text_in_file += line
        return text_in_file

    def load_file(self, filename):
        file = QtCore.QFile(filename[0])

        if not (file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)):
            QtWidgets.QMessageBox.warning(
                self, "Application", f"Cannot read file {QtCore.QDir.toNativeSeparators(filename[0])}:\n{file.errorString()}.")
            return

        input_stream = QtCore.QTextStream(file)

        QtGui.QGuiApplication.restoreOverrideCursor()

        self.text_editor.setPlainText(input_stream.readAll())

        QtGui.QGuiApplication.restoreOverrideCursor()

        self.set_current_file(filename)
        self.status_bar.showMessage("File loaded", 3000)

    def set_current_file(self, filename):
        self.current_file = filename
        self.text_editor.document().setModified(False)
        self.setWindowModified(False)

        shown_name = self.current_file

        if self.current_file == "":
            shown_name = "untitled.txt[*] - King's Editor"
        if type(shown_name) == tuple or type(shown_name) == list:
            shown_name = shown_name[0]
            shown_name = shown_name.split("/")
            shown_name = shown_name[-1] + "[*] - King's Editor"
        self.setWindowFilePath(shown_name)
        self.setWindowTitle(shown_name)

    def save_file(self, filename) -> bool:
        error_message = ""
        QtGui.QGuiApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        file = QtCore.QSaveFile(filename[0])
        if (file.open(QtCore.QIODevice.WriteOnly | QtCore.QIODevice.Text)):
            out = QtCore.QTextStream(file)
            out << self.text_editor.toPlainText()
            self.setWindowTitle(f"{filename[0]}[*] - King's Editor")

            if not (file.commit()):
                error_message = f"Cannot write file {QtCore.QDir.toNativeSeparators(filename[0])}:\n{file.errorString()}"
        else:
            error_message = f"Cannot open file {QtCore.QDir.toNativeSeparators(filename[0])} for writing:\n{file.errorString()}"

        QtGui.QGuiApplication.restoreOverrideCursor()

        if not error_message == "":
            message_box = QtWidgets.QMessageBox()
            message_box.warning(self, "Application", error_message)

            return False

        self.set_current_file(filename)
        self.status_bar.showMessage("File Saved", 2000)
        return True

    def maybe_save(self) -> bool:
        if not self.text_editor.document().isModified():
            return True

        ret = QtWidgets.QMessageBox.warning(self, "Application", "The document has been modified.\nDo you want to save your changes?",
                                            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        if ret == QtWidgets.QMessageBox.Save:

            return self.save[0]()

        elif ret == QtWidgets.QMessageBox.Cancel:
            return False
        return True

    def open_settings(self):
        Settings()
        self.tab_size = self.updated_tab_size()

    def read_settings(self):
        settings = QtCore.QSettings(QtCore.QCoreApplication.organizationName(
        ), QtCore.QCoreApplication.applicationName())
        geometry = settings.value("geometry", QtCore.QByteArray())

        if geometry is None:
            availableGeometry = self.screen().availableGeometry()
            self.resize(availableGeometry.width()/3,
                        availableGeometry.height()/2)
            self.move((availableGeometry.width() - self.width()) / 2,
                      (availableGeometry.height() - self.height())/2)

        else:
            self.restoreGeometry(geometry)

        self.tab_size = self.updated_tab_size()

    def write_settings(self):
        settings = QtCore.QSettings(QtCore.QCoreApplication.organizationName(
        ), QtCore.QCoreApplication.applicationName())
        settings.setValue("geometry", self.saveGeometry())

    def updated_tab_size(self) -> int:
        self.settings = QtCore.QSettings(QtCore.QCoreApplication.organizationName(
        ), QtCore.QCoreApplication.applicationName())
        tab_size = int(self.settings.value("tab-size", 4))
        return tab_size

    def closeEvent(self, event):
        if self.maybe_save():
            self.write_settings()
            event.accept()
        else:
            event.ignore()


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
