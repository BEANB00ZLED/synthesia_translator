import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from ui import Ui_MainWindow


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ----- Connecting UI to functions ------
        self.fileBrowseButton.clicked.connect(self.browseFiles)

    def browseFiles(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Video Files (*.mp4)")
        if dlg.exec_():
            fname = dlg.selectedFiles()
            self.filePathLine.setText(fname[0])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
