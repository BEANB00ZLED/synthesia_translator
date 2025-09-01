import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal
from ui.main_window import Ui_MainWindow
from ui.advanced_options import Ui_AdvancedOptions
from dataclasses import dataclass
import cv2


@dataclass
class AdvancedOptions:
    keyOffset: int


class AdvancedOptionsWindow(QDialog, Ui_AdvancedOptions):
    advancedOptions = pyqtSignal(AdvancedOptions)

    def __init__(self, advancedOptions: AdvancedOptions):
        super().__init__()
        self.setupUi(self)

        # Set values to stored inputs
        self.keyOffsetSpinBox.setValue(advancedOptions.keyOffset)

        # ----- Creating UI connections -----
        self.buttonBox.accepted.connect(self.emitValues)

    def emitValues(self):
        updatedOptions = AdvancedOptions(keyOffset=self.keyOffsetSpinBox.value())
        self.advancedOptions.emit(updatedOptions)
        self.accept()


class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.videoCapture: cv2.VideoCapture

        # ----- Advanced Options -----
        self.advancedOptionsWindow: QDialog
        self.advancedOptions = AdvancedOptions(keyOffset=90)

        # ----- Creating UI connections ------

        # ----- Connecting UI to functions ------
        self.fileBrowseButton.clicked.connect(self.browseFiles)
        self.advancedOptionsButton.clicked.connect(self.openAdvancedOptions)

    def browseFiles(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setNameFilter("Video Files (*.mp4)")
        # On filebrowser open
        if dlg.exec_():
            selectedFile = dlg.selectedFiles()[0]
            self.filePathLine.setText(selectedFile)
            self.openFile(selectedFile)

    def openFile(self, fileName):
        self.videoCapture = cv2.VideoCapture(fileName)
        fps = round(self.videoCapture.get(cv2.CAP_PROP_FPS), 0)
        numFrames = self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.videoCapture.set(
            cv2.CAP_PROP_POS_FRAMES, 1000
        )  # temp for now so not starting on black frame
        self.displayNextFrame()

        print(f"Video FPS: {fps}")
        print(f"Number of frames: {numFrames}")

    def displayNextFrame(self):
        if not self.videoCapture:
            return

        ret, frame = self.videoCapture.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame.shape
        bytesPerLine = channels * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qImg)
        self.videoLabel.setPixmap(pixmap)

    def openAdvancedOptions(self):
        # Create window with current values
        self.advancedOptionsWindow = AdvancedOptionsWindow(self.advancedOptions)
        # Connect local variable to signal
        self.advancedOptionsWindow.advancedOptions.connect(self.updatedAdvancedOptions)
        self.advancedOptionsWindow.show()
        self.advancedOptionsWindow.raise_()
        self.advancedOptionsWindow.activateWindow()

    def updatedAdvancedOptions(self, upadtedOptions: AdvancedOptions):
        self.advancedOptions = upadtedOptions


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
