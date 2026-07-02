from PyQt6.QtWidgets  import  (QLabel, QFrame, QHBoxLayout, QVBoxLayout)
from PyQt6.QtCore import Qt
from MyWidgets.KeyLineEdit import KeyLineEdit

class MessageBlock(QFrame):
    """Object for giving space for users input command and then shows the output
    """
    def __init__(self, header, path, git, enter_callback = None, update_callback = None, path_search_callback = None, link_search_callback = None, pointing_callback = None):
        """Initializes message block with all of its widgets and all callback functions

        Args:
            header (string): user and system name to show
            path (string): folder path to show
            git (string): git branch name, if it is inside git repo
            enter_callback (function, optional): function for when ending the command. Defaults to None.
            update_callback (function, optional): function to update view of widgets in the main app. Defaults to None.
            path_search_callback (function, optional): function for path searching. Defaults to None.
            link_search_callback (function, optional): function for link searching. Defaults to None.
            pointing_callback (function, optional): function for using arrows. Defaults to None.
        """
        super().__init__()
        self.enter_callback = enter_callback
        self.update_callback = update_callback
        self.path_search_callback = path_search_callback
        self.link_search_callback = link_search_callback
        self.pointing_callback = pointing_callback
        self.u_input = ""
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        self.setLayout(layout)
        
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_lbl = QLabel(header + " ")
        header_lbl.setStyleSheet("color: #7FFF00;")
        header_path_lbl = QLabel(path)
        header_path_lbl.setStyleSheet("color: #FFD700;")
        
        header_layout.addWidget(header_lbl)
        header_layout.addWidget(header_path_lbl)
        if git[0]:
            git_lbl = QLabel(f"({git[1]})")
            git_lbl.setStyleSheet("color: #1E90FF;")
            header_layout.addWidget(git_lbl)

        
        user_input_layout = QHBoxLayout()
        start_lbl = QLabel(">")
        start_lbl.setStyleSheet("color: #FFFFFF;")
        self.user_input_widget = KeyLineEdit(enter_callback=self.finish_input, 
                                            path_search_callback=self.writing_path, 
                                            link_search_callback=self.link_search_callback,
                                            pointing_callback=self.pointing_callback)
        self.user_input_widget.setStyleSheet("color: #FFFFFF;")
        self.user_input_widget.setFrame(False)
        user_input_layout.addWidget(start_lbl)
        user_input_layout.addWidget(self.user_input_widget)
        
        self.answer_lbl = QLabel()
        self.answer_lbl.setStyleSheet("color: #FFFFFF;")
        
        layout.addLayout(header_layout)
        layout.addLayout(user_input_layout)
        layout.addWidget(self.answer_lbl)
        
    
    def finish_input(self):
        """On finishing the command and sending it to the CLI, and its changes to the widgets
        """
        self.user_input_widget.setReadOnly(False)
        user_input = self.user_input_widget.text()
        answer_text = None
        if self.enter_callback:
            immediate_response, answer_text = self.enter_callback(user_input)  
        if immediate_response:
            self.answer_lbl.setText(answer_text)
            if self.update_callback:
                self.update_callback()

    
    def writing_path(self):
        """On path searching and its changes to the widgets
        """
        self.user_input_widget.setEnabled(False)
        user_input = self.user_input_widget.text()
        path = ""
        if self.path_search_callback:
            path = self.path_search_callback()
            if len(user_input) >= 1 and user_input[-1] != " ":
                path = " " + path
        self.user_input_widget.setText(f"{user_input}{path}")
        self.user_input_widget.setEnabled(True)
        self.user_input_widget.setFocus()


    def mousePressEvent(self, event):
        """Focusing on the main user input widget"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.user_input_widget.setFocus()
        super().mousePressEvent(event)
        
        

        
