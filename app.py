import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QDialog
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal
from ui.main_window import Ui_MainWindow
from ui.advanced_options import Ui_AdvancedOptions
from data_types import AdvancedOptions
from app_logging import logger, LogLevel
import cv2
import vision


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
        self.baseFrame: cv2.typing.MatLike
        self.previewedFrame: cv2.typing.MatLike

        # ----- Advanced Options -----
        self.advancedOptionsWindow: QDialog
        self.advancedOptions = AdvancedOptions()

        # ----- Creating UI connections ------
        logger.logSignal.connect(self.log)

        # ----- Connecting UI to functions ------
        self.fileBrowseButton.clicked.connect(self.browseFiles)
        self.advancedOptionsButton.clicked.connect(self.openAdvancedOptions)
        self.previewKeysButton.clicked.connect(self.previewKeyDetection)

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
        self.getFrame()
        self.displayCurrentFrame()
        self.previewKeysButton.setEnabled(True)

        logger.sendLog(f"Opened video file: {fileName}.", LogLevel.INFO)
        logger.sendLog(f"Frames per second: {fps}.", LogLevel.INFO)

    def getFrame(self):
        if not self.videoCapture:
            return

        ret, frame = self.videoCapture.read()
        self.baseFrame = frame
        self.previewedFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def displayCurrentFrame(self):
        if self.previewedFrame is None:
            return

        height, width, channels = self.previewedFrame.shape
        bytesPerLine = channels * width
        qImg = QImage(
            self.previewedFrame.data, width, height, bytesPerLine, QImage.Format_RGB888
        )
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

    def previewKeyDetection(self):
        self.previewedFrame = self.baseFrame.copy()
        self.previewedFrame = cv2.cvtColor(self.previewedFrame, cv2.COLOR_BGR2RGB)
        keyLocations = vision.determineKeyLocations(
            self.baseFrame, self.advancedOptions
        )
        for x, y in keyLocations:
            cv2.circle(self.previewedFrame, (x, y), 1, (0, 255, 0), -1)
        self.displayCurrentFrame()
        self.transcribeVideoButton.setEnabled(True)

        logger.sendLog(f"Detected {len(keyLocations)} keys.", LogLevel.INFO)

        fullPianoKeyLocations = 88
        if len(keyLocations) < fullPianoKeyLocations:
            logger.sendLog(
                f"Detected fewer than {fullPianoKeyLocations} keys. Consider adjusting detection parameters or starting key's note.",
                LogLevel.WARNING,
            )

    def log(self, message: str):
        self.logOutput.appendPlainText(message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
