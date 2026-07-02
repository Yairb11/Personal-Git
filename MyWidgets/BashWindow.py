
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QAbstractItemView, 
                             QFileDialog, QListWidget, QListWidgetItem, QInputDialog, QApplication)
from PyQt6.QtCore import QSettings, Qt, QEvent
from PyQt6.QtGui import QIcon, QTextCursor
from MyWidgets.MessageBlock import *
from MyWidgets.GithubBrowserWindow import *
from MyWidgets.MessageListWidgetItem import *
from MyWidgets.SubprocessThread import *
import subprocess
import os
import re

PROGRESS_BAR_REGEX = r'^([a-zA-Z\s]+:)'
GIT_PROGRESS_LIST = ["clone", "fetch", "pull", "push", "bundle", "pack-object"]

class BashWindow(QMainWindow):
    def __init__(self, bash_path, user_name, computer_name):
        super().__init__()
        os.chdir(os.path.expanduser("~"))
        self.path = os.getcwd()
        self.users_home_path = os.getcwd()
        self.bash_path = bash_path
        self.header = f"{user_name}@{computer_name}"
        self.browser_window = None
        self.main_input_widget = None
        self.command_text_lines = None
        self.thread  = None
        self.pointer_index = 0

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
        path_split = self.path.split(self.users_home_path)
        if(len(path_split) == 1):
            path_linux = self.path
        else:
            path_linux = '~' + path_split[-1]
        
        git = self.get_git_status()
        
        message_frame = MessageBlock(self.header, path_linux, git, 
                                    enter_callback=self.on_enter, 
                                    update_callback=self.on_update, 
                                    path_search_callback=self.on_path_search, 
                                    link_search_callback=self.on_link_search,
                                    pointing_callback=self.on_pointing)
        self.main_input_widget = message_frame.user_input_widget
        message_frame.setStyleSheet("background-color: black;")
        list_item = MessageListWidgetItem (self.chat_list, message_frame)
        list_item.resize()
        self.chat_list.setItemWidget(list_item, message_frame)
        self.chat_list.scrollToBottom()
        self.main_input_widget.setFocus()
        self.pointer_index = self.chat_list.count()
    
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
        
    def on_enter(self, user_input):
        if not user_input:
            return " "
        
        parts = user_input.split()
        index = 0
        while(index < len(parts) and not(parts[index])):
            index += 1
        if index == len(parts):
            return " "
        
        if parts[index] == "git":
            second_index = index + 1
            while(second_index < len(parts) and not(parts[second_index])):
                second_index += 1
                
            if second_index == len(parts):
                self.run_commend(user_input)
                return None
            
            if parts[second_index] in GIT_PROGRESS_LIST:
                self.run_commend(user_input + " --progress")
                return None
            
            self.run_commend(user_input)
            return None
        
        if parts[index] != "cd":
            self.run_commend(user_input)
            return None
        
        if len(parts) <= 1:  
            return f"bash: cd: {parts[1]}: No such file or directory"  
        
        try:
            os.chdir(parts[1])
            self.path = os.getcwd()
            return " "
        
        except FileNotFoundError:
            return f"bash: cd: {parts[1]}: No such file or directory"   
        
    def on_update(self):
        last_item = self.chat_list.item(self.chat_list.count() - 1)
        last_item.resize()
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
        
    def on_pointing(self, change):
        if self.pointer_index + change > self.chat_list.count() or self.pointer_index + change <= 0:
            return 
        
        self.pointer_index += change
        pointed_item = self.chat_list.item(self.pointer_index - 1)
        text = pointed_item.get_input_widget().text()
        if self.pointer_index == self.chat_list.count():
            text = ""  
        self.main_input_widget.setText(text)
        

        
    def run_commend(self, user_input):
        self.command_text_lines = [""]
        self.thread = SubprocessThread([self.bash_path, "-c", user_input])
        self.thread.text_update.connect(self.append_text)
        self.thread.finished.connect(self.on_update)
        self.thread.start()
        
    def append_text(self, text, overwrite_last):
        clean_text = text.strip()
        if not clean_text:
            return
        
        last_item = self.chat_list.item(self.chat_list.count() - 1)
        answer_lbl = last_item.get_answer_widget()
        
        if not overwrite_last and len(self.command_text_lines) >= 1:
            progress_cat_new = re.match(PROGRESS_BAR_REGEX, clean_text)
            progress_cat_old = re.match(PROGRESS_BAR_REGEX, self.command_text_lines[-1])
            if progress_cat_new and progress_cat_old:
                overwrite_last = (progress_cat_new.group(1) == progress_cat_old.group(1))
        
        if overwrite_last:
            if self.command_text_lines:
                self.command_text_lines[-1] = clean_text
            else:
                self.command_text_lines.append(clean_text)
        else:
            self.command_text_lines.append(clean_text)

        answer_lbl.setText('\n'.join(self.command_text_lines))
        last_item.resize() 
            
        
    
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

