from PyQt6.QtWidgets  import  (QLabel, QFrame, QHBoxLayout, QVBoxLayout, QLineEdit)
from PyQt6.QtCore import Qt
from MyWidgets.KeyLineEdit import *

class MessageBlock(QFrame):
    def __init__(self, header, path, git, enter_callback = None, update_callback = None, path_search_callback = None, link_search_callback = None):
        super().__init__()
        self.enter_callback = enter_callback
        self.update_callback = update_callback
        self.path_search_callback = path_search_callback
        self.link_search_callback = link_search_callback
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
        self.user_input_widget = KeyLineEdit(enter_callback=self.finish_input, 
                                            path_search_callback=self.writing_path, 
                                            link_search_callback=self.link_search_callback)
        self.user_input_widget.setFrame(False)
        user_input_layout.addWidget(start_lbl)
        user_input_layout.addWidget(self.user_input_widget)
        
        self.answer_lbl = QLabel()
        
        layout.addLayout(header_layout)
        layout.addLayout(user_input_layout)
        layout.addWidget(self.answer_lbl)
        
    
    def finish_input(self):
        self.user_input_widget.setEnabled(False)
        user_input = self.user_input_widget.text()
        if self.enter_callback:
            answer_text = self.enter_callback(user_input, self.answer_lbl, self)
            self.answer_lbl.setText(answer_text)
        if self.update_callback:
            self.update_callback(self)

    
    def writing_path(self):
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
        if event.button() == Qt.MouseButton.LeftButton:
            self.user_input_widget.setFocus()
        super().mousePressEvent(event)
        
        

        
