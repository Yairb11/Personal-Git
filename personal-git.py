import shutil
import sys
from PyQt6 import QtWidgets 
from MyWidgets.BashWindow import *
import getpass
import os

BASH_PATH = r"X:\gitlab\Git\usr\bin\bash.EXE"

if __name__ == "__main__":
    user_name = getpass.getuser()
    computer_name = os.environ.get('COMPUTERNAME')
    desktop_app = QtWidgets.QApplication(sys.argv)
    window = BashWindow(BASH_PATH, user_name, computer_name)
 
    window.show()
    sys.exit(desktop_app.exec())
 