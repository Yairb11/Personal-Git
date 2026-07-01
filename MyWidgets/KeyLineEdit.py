from PyQt6.QtWidgets  import  (QLineEdit)
from PyQt6.QtCore import Qt

class KeyLineEdit(QLineEdit):
    def __init__(self, enter_callback = None, path_search_callback = None, link_search_callback = None):
        super().__init__()
        self.enter_callback = enter_callback
        self.path_search_callback = path_search_callback
        self.link_search_callback = link_search_callback
        
    def keyPressEvent(self, event):
        key = event.key()
        is_ctrl_pressed = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        
        if (key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter) and self.enter_callback:
            self.enter_callback()
        elif is_ctrl_pressed and key == Qt.Key.Key_F and self.path_search_callback:
            self.path_search_callback()
        elif is_ctrl_pressed and key == Qt.Key.Key_I and self.link_search_callback:
            self.link_search_callback()
        
        if not is_ctrl_pressed:
            super().keyPressEvent(event)
        
