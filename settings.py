from PyQt5 import QtCore, QtWidgets


class Settings(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()
        self.setup_UI()

    def setup_UI(self):
        self.setWindowTitle("Settings - King's Editor")

        list_widget = QtWidgets.QListWidget(self)

        def mapper(item):
            if item == "Saving":
                saving_setting()
            elif item == "Formatting":
                formatting_settings()

        def saving_setting():
            stacked_widget.setCurrentWidget(saving_frame)

        def formatting_settings():
            stacked_widget.setCurrentWidget(formatting_frame)

        QtWidgets.QListWidgetItem("Saving", list_widget)
        QtWidgets.QListWidgetItem("Formatting", list_widget)
        QtWidgets.QListWidgetItem("Status bar", list_widget)

        list_widget.currentItemChanged.connect(
            lambda: mapper(list_widget.currentItem().text()))

        saving_frame = QtWidgets.QFrame(self)
        saving_layout = QtWidgets.QGridLayout()
        autosave_label = QtWidgets.QLabel(
            "Autosave time interval (s): ", parent=saving_frame)
        autosave_time = QtWidgets.QSpinBox(parent=saving_frame)
        autosave_time.setMinimum(5)
        saving_layout.addWidget(autosave_label, 1, 1)
        saving_layout.addWidget(autosave_time, 1, 2)
        saving_frame.setLayout(saving_layout)

        formatting_frame = QtWidgets.QFrame(self)
        formatting_layout = QtWidgets.QGridLayout()
        font_label = QtWidgets.QLabel("Font: ", parent=formatting_frame)
        font = QtWidgets.QFontComboBox(parent=formatting_frame)
        font_size_label = QtWidgets.QLabel(
            "Font Size: ", parent=formatting_frame)
        font_size = QtWidgets.QSpinBox(parent=formatting_frame)
        font_size.setMinimum(8)
        font_size.setMaximum(150)
        text_color_label = QtWidgets.QLabel(
            "Text Color: ", parent=formatting_frame)
        text_color = QtWidgets.QPushButton(
            "Pick a color", parent=formatting_frame)
        text_color.clicked.connect(self.change_color)
        tab_size_label = QtWidgets.QLabel(
            "Tab Size: ", parent=formatting_frame)
        tab_size = QtWidgets.QSpinBox(parent=formatting_frame)
        tab_size.setRange(2, 8)

        formatting_layout.addWidget(font_label, 1, 1)
        formatting_layout.addWidget(font, 1, 2)
        formatting_layout.addWidget(font_size_label, 2, 1)
        formatting_layout.addWidget(font_size, 2, 2)
        formatting_layout.addWidget(text_color_label, 3, 1)
        formatting_layout.addWidget(text_color, 3, 2)
        formatting_layout.addWidget(tab_size_label, 4, 1)
        formatting_layout.addWidget(tab_size, 4, 2)
        formatting_frame.setLayout(formatting_layout)

        status_bar_frame = QtWidgets.QFrame(self)
        status_bar_layout = QtWidgets.QVBoxLayout()

        status_bar_frame.setLayout(status_bar_layout)

        stacked_widget = QtWidgets.QStackedWidget(self)
        stacked_widget.setFixedSize(QtCore.QSize(400, 400))
        stacked_widget.addWidget(saving_frame)
        stacked_widget.addWidget(formatting_frame)
        stacked_widget.addWidget(status_bar_frame)

        self.settings_layout = QtWidgets.QHBoxLayout()
        self.settings_layout.addWidget(list_widget)
        self.settings_layout.addWidget(stacked_widget)

        self.setLayout(self.settings_layout)
        self.exec_()

    def change_color(self):
        color_dialog = QtWidgets.QColorDialog()
        self.settings_layout.addWidget(color_dialog)
