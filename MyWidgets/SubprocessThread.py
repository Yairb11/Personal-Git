import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QTextCursor

CREATE_NO_WINDOW = 0x08000000
class SubprocessThread(QThread):
    text_update = pyqtSignal(str, bool)
    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1, 
            creationflags=CREATE_NO_WINDOW,
            encoding='utf-8',
            errors='replace'
        )
        
        buffer = ""
        while True:
            char = process.stdout.read(1)
            if not char and process.poll() is not None:
                if buffer:
                    self.text_update.emit(buffer, False)
                break
            if char == '\r':

                self.text_update.emit(buffer, True)
                buffer = ""
            elif char == '\n':
                self.text_update.emit(buffer, False)
                buffer = ""
            else:
                buffer += char
                   
        process.stdout.close()
        process.wait()