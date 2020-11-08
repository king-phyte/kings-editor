from PyQt5 import QtCore
from time import sleep


class MyThread(QtCore.QThread):

    value = QtCore.pyqtSignal(int)
    autosave_time = 8
    autosave_enabled = True

    def run(self):
        while self.autosave_enabled:
            sleep(self.autosave_time)
            self.value.emit(1)
        else:
            self.quit()
