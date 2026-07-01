
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QAbstractItemView, 
                             QFileDialog, QListWidget, QListWidgetItem, QInputDialog, QApplication)
from PyQt6.QtCore import QSettings, Qt, QEvent
from PyQt6.QtGui import QIcon
from MyWidgets.MessageBlock import *
from MyWidgets.GithubBrowserWindow import *
import subprocess
import os

class BashWindow(QMainWindow):
    def __init__(self, bash_path, user_name, computer_name):
        super().__init__()
        os.chdir(os.path.expanduser("~"))
        self.path = os.getcwd()
        self.users_home_path = os.getcwd()
        self.bash_path = bash_path
        self.user_name = user_name
        self.header = f"{user_name}@{computer_name}"
        self.browser_window = None
        self.main_input_widget = None

        self.setWindowTitle("Personal-Git")
        QApplication.instance().installEventFilter(self)   
        self.settings = QSettings("PersonalGit", "personal-git")
        self.read_settings()    
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
 
        
        self.chat_list =  QListWidget()
        self.chat_list.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.chat_list.verticalScrollBar().setSingleStep(20)
        main_layout.addWidget(self.chat_list)
        self.add_message()
        
    def add_message(self):
        list_item = QListWidgetItem(self.chat_list)
        path_split = self.path.split(self.user_name)
        if(len(path_split) == 1):
            path_linux = self.path
        else:
            path_linux = '~' + path_split[-1]
        
        git = self.get_git_status()
        
        message_frame = MessageBlock(self.header, path_linux, git, 
                                    enter_callback=self.on_enter, 
                                    update_callback=self.on_update, 
                                    path_search_callback=self.on_path_search, 
                                    link_search_callback=self.on_link_search)
        self.main_input_widget = message_frame.user_input_widget
        message_frame.setStyleSheet("background-color: black;")
        list_item.setSizeHint(message_frame.sizeHint())
        self.chat_list.setItemWidget(list_item, message_frame)
        self.chat_list.scrollToBottom()
        self.main_input_widget.setFocus()
    
    def get_git_status(self):
        try:
            subprocess.run(
                ["git", "-C", self.path, "rev-parse", "--is-inside-work-tree"],
                capture_output=True, check=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            branch_result = subprocess.run(
                ["git", "-C", self.path, "branch", "--show-current"],
                capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            branch_name = branch_result.stdout.strip()
            
            if not branch_name:
                commit_result = subprocess.run(
                    ["git", "-C", self.path, "rev-parse", "--short", "HEAD"],
                    capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                branch_name = commit_result.stdout.strip()
                
            return [True, branch_name]
        except subprocess.CalledProcessError:
            return [False, None]
      
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.main_input_widget.setFocus()
        return super().eventFilter(obj, event)
        
    def on_enter(self, user_input, answer_widget, frame):
        if not user_input:
            return ""
        
        parts = user_input.split()
        base_command = parts[0]
        if base_command != "cd":
            return self.run_commend(user_input, answer_widget, frame)
        
        if len(parts) <= 1:  
            return f"bash: cd: {parts[1]}: No such file or directory"  
        
        try:
            os.chdir(parts[1])
            self.path = os.getcwd()
            return ""
        
        except FileNotFoundError:
            return f"bash: cd: {parts[1]}: No such file or directory"   
        
    def on_update(self, frame):
        last_item = self.chat_list.item(self.chat_list.count() - 1)
        last_item.setSizeHint(frame.sizeHint())
        self.add_message()
    def on_path_search(self):
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select Target Folder",
            f"{self.path}",
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            return normalized_path
        return ""
    
    def on_link_search(self):
        self.main_input_widget.setEnabled(False)
        self.browser_window = GithubBrowserWindow(link_found_callback=self.on_found_link)
        self.browser_window.show()

    def on_found_link(self, link):
        user_input = self.main_input_widget.text()
        if len(user_input) >= 1 and user_input[-1] != " ":
            self.main_input_widget.setText(f"{user_input} {link}")
        else:
            self.main_input_widget.setText(f"{user_input}{link}")
        self.main_input_widget.setEnabled(True)
        self.main_input_widget.setFocus()

        
    def run_commend(self, user_input, answer_widget, frame):
        answer = ""
        last_item = self.chat_list.item(self.chat_list.count() - 1)
        process = subprocess.Popen(
            [self.bash_path, "-c", user_input], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True            
        )
        
        for line in process.stdout:
            answer = answer + line
            answer_widget.setText(answer)
            last_item.setSizeHint(frame.sizeHint())
            
        process.wait()
        return answer
    
    def read_settings(self):
        geometry = self.settings.value("geometry")
        window_state = self.settings.value("windowState")
        if geometry:
            self.restoreGeometry(geometry)
        if window_state:
            self.restoreState(window_state)

    def write_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def closeEvent(self, event):
        self.write_settings()
        super().closeEvent(event)

