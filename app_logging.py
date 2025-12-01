from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class LogEmitter(QObject):
    logSignal = pyqtSignal(str)

    def __init__(self, logLevel: LogLevel, parent=None):
        super().__init__(parent)
        self.logLevel = logLevel

    def sendLog(self, message: str, logLevel: LogLevel):
        if logLevel.value < self.logLevel.value:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log = f"[{timestamp}] {logLevel.name} | {message}"
        if logLevel == LogLevel.DEBUG:
            print(log)
        self.logSignal.emit(log)


logger = LogEmitter(logLevel=LogLevel.DEBUG)
