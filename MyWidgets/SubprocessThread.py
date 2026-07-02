import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

CREATE_NO_WINDOW = 0x08000000

class SubprocessThread(QThread):
    """Object for runnig commands on the background and streaming outputs
    """
    text_update = pyqtSignal(str, bool)
    def __init__(self, command):
        """Initializes basic needs for this thread

        Args:
            command (list): users command for the subprocess to work
        """
        super().__init__()
        self.command = command
        self.process = None
        self.is_stoped = False

    def run(self):
        """Runs subprocess while updating the mainloop of the application using self.text_update that was defind with this object
        can be stoped by the mainloop
        """
        self.process = subprocess.Popen(
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
        while not self.is_stoped:
            char = self.process.stdout.read(1)
            if not char and self.process.poll() is not None:
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
                   
        self.process.stdout.close()
        self.process.wait()
        
    def stop(self):
        """Stops this thread process by getting input from the mainloop of the application
        """
        self.is_stoped = True
        if self.process:
            self.process.terminate()