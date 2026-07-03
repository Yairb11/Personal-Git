
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QAbstractItemView, 
                             QFileDialog, QListWidget, QApplication)
from PyQt6.QtCore import QSettings, Qt, QEvent
from MyWidgets.MessageBlock import MessageBlock
from MyWidgets.GithubBrowserWindow import GithubBrowserWindow
from MyWidgets.MessageListWidgetItem import MessageListWidgetItem
from MyWidgets.SubprocessThread import SubprocessThread
import subprocess
import os
import re

PROGRESS_BAR_REGEX = r'^([a-zA-Z\s]+:)'
GIT_PROGRESS_LIST = ["clone", "fetch", "pull", "push", "bundle", "pack-object"]

class BashWindow(QMainWindow):
    """Application window with all of the widgets and functions
    """
    def __init__(self, bash_path, user_name, computer_name):
        """Initiates all the widgets and variables, and the main window

        Args:
            bash_path (string): bash.exe path location
            user_name (string): name of the user
            computer_name (string): system name
        """
        super().__init__()
        os.chdir(os.path.expanduser("~"))
        self.path = os.getcwd()
        self.users_home_path = os.getcwd()
        self.bash_path = bash_path
        self.header = f"{user_name}@{computer_name}"
        self.browser_window = None
        self.main_input_widget = None
        self.command_text_lines = None
        self.thread = None
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
        """Addes new MessageBlock to QListWidget to continue the CLI application,
        it gets all the infirmation needed for the new MessageBlock and in the end restarts main view of main application
        """
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
        """Gets git branch name if it exist at all in this folder location, 
        this is for the MessageBlock

        Returns:
            list: bool-> there is branch name, string->branch name
        """
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
        """Checks every event in the main application for some important functionality like
        focus, copying and ending process  
        """
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.main_input_widget.setFocus()
        elif event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if self.thread:
                    self.thread.stop()
                else:
                    selected_widget = None
                    for i in range(self.chat_list.count() - 1):
                        item = self.chat_list.item(i)
                        if item.get_input_widget().hasSelectedText():
                            selected_widget = item.get_input_widget()
                            QApplication.clipboard().setText(selected_widget.selectedText())
                            selected_widget.deselect()
                            break
                        elif item.get_answer_widget().hasSelectedText():
                            selected_widget = item.get_answer_widget()
                            QApplication.clipboard().setText(selected_widget.selectedText())
                            selected_widget.setSelection(0, 0)
                            break
                    if selected_widget is None:
                        return super().eventFilter(obj, event)                    
                    return True
                    
        return super().eventFilter(obj, event)
        
    def on_enter(self, user_input):
        """Gets users input and executes it like it should be in CLI

        Args:
            user_input (string): users input

        Returns:
            bool: is the execution was immediate, and not run thread with subprocess
            string: output of the CLI if exist already
        """
        if not user_input:
            return True, ""
        
        parts = user_input.split()
        index = 0
        while(index < len(parts) and not(parts[index])):
            index += 1
        if index == len(parts):
            return True, ""
        
        if parts[index] == "git":
            second_index = index + 1
            while(second_index < len(parts) and not(parts[second_index])):
                second_index += 1
                
            if second_index == len(parts):
                self.run_commend(user_input)
                return False, ""
            
            if parts[second_index].lower() in GIT_PROGRESS_LIST:
                self.run_commend(user_input + " --progress")
                return False, ""
            
            self.run_commend(user_input)
            return False, ""
        
        if parts[index] != "cd":
            self.run_commend(user_input)
            return False, ""
        
        try:
            os.chdir(parts[1] if len(parts) > 1 else os.path.expanduser("~"))
            self.path = os.getcwd()
            return True, ""
        
        except FileNotFoundError:
            return True, f"bash: cd: {parts[1]}: No such file or directory"   
        
    def on_update(self):
        """Updates the main application widgets after finishing users task,
        in the end creating new message input
        """
        self.thread = None
        last_item = self.chat_list.item(self.chat_list.count() - 1)
        last_item.resize()
        last_item.get_answer_widget().setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.add_message()
        
    def on_path_search(self):
        """Creates QFileDialog for the user to find his targeted folder

        Returns:
            string: folder path
        """
        file_path = QFileDialog.getExistingDirectory(
            self,
            "Select Target Folder",
            f"{self.path}",
        )
        if file_path:
            normalized_path = os.path.normpath(file_path)
            new_path_cut = normalized_path.split(self.path)
            if (new_path_cut[0] and len(new_path_cut) == 1) or (len(new_path_cut) > 2):
                return normalized_path
            return new_path_cut[1]
        return ""
    
    def on_link_search(self):
        """Creates GithubBrowserWindow for the user to find his targeted .git link
        """
        self.main_input_widget.setEnabled(False)
        self.browser_window = GithubBrowserWindow(link_found_callback=self.on_found_link)
        self.browser_window.show()

    def on_found_link(self, link):
        """When targeted .git link is found, it updates the widgets

        Args:
            link (string): targeted .git link
        """
        user_input = self.main_input_widget.text()
        if len(user_input) >= 1 and user_input[-1] != " ":
            self.main_input_widget.setText(f"{user_input} {link}")
        else:
            self.main_input_widget.setText(f"{user_input}{link}")
        self.main_input_widget.setEnabled(True)
        self.main_input_widget.setFocus()
        
    def on_pointing(self, change):
        """Gets user history from the messaging system using keyboard arrows

        Args:
            change (number): jump to history position
        """
        if self.pointer_index + change > self.chat_list.count() or self.pointer_index + change <= 0:
            return 
        
        self.pointer_index += change
        pointed_item = self.chat_list.item(self.pointer_index - 1)
        text = pointed_item.get_input_widget().text()
        if self.pointer_index == self.chat_list.count():
            text = ""  
        self.main_input_widget.setText(text)
        self.chat_list.scrollToBottom()
        
    def run_commend(self, user_input):
        """Creates thread to run users input command

        Args:
            user_input (string): users input command
        """
        self.command_text_lines = [""]
        self.thread = SubprocessThread([self.bash_path, "-c", user_input])
        self.thread.text_update.connect(self.append_text)
        self.thread.finished.connect(self.on_update)
        self.thread.start()
        
    def append_text(self, text, overwrite_last):
        """Runs with created thread to update widgets so it would be fast and stream like for the UX

        Args:
            text (string): line added or changed by the subprocess
            overwrite_last (bool): if the new line is for overwriting last line or not
        """
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
        self.chat_list.scrollToBottom()
            
    def read_settings(self):
        """Read and changes window state and geometry from last use"""
        geometry = self.settings.value("geometry")
        window_state = self.settings.value("windowState")
        if geometry:
            self.restoreGeometry(geometry)
        if window_state:
            self.restoreState(window_state)

    def write_settings(self):
        """Saves window state and geometry of the application"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def closeEvent(self, event):
        """On closing application"""
        self.write_settings()
        super().closeEvent(event)