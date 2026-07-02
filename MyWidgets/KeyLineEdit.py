from PyQt6.QtWidgets  import  (QLineEdit)
from PyQt6.QtCore import Qt

class KeyLineEdit(QLineEdit):
    """Object for custom QLineEdit that recording key presses for some unique that would match wanted functionality
    """
    def __init__(self, enter_callback = None, path_search_callback = None, link_search_callback = None, pointing_callback = None):
        """Initiates with storing usefull callback functions

        Args:
            enter_callback (function, optional): function for pressing enter and finishing the command. Defaults to None.
            path_search_callback (function, optional): function for path searching. Defaults to None.
            link_search_callback (function, optional): function for .git link searching. Defaults to None.
            pointing_callback (function, optional): function for arrow usage on the keyboard. Defaults to None.
        """
        super().__init__()
        self.enter_callback = enter_callback
        self.path_search_callback = path_search_callback
        self.link_search_callback = link_search_callback
        self.pointing_callback = pointing_callback
        
    def keyPressEvent(self, event):
        """Recording key presses for the ability to use some callback function
        """
        key = event.key()
        is_ctrl_pressed = event.modifiers() == Qt.KeyboardModifier.ControlModifier
        
        if (key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter) and self.enter_callback:
            self.enter_callback()
        elif is_ctrl_pressed and key == Qt.Key.Key_F and self.path_search_callback:
            self.path_search_callback()
        elif is_ctrl_pressed and key == Qt.Key.Key_I and self.link_search_callback:
            self.link_search_callback()
        elif key == Qt.Key.Key_Up:
            self.pointing_callback(-1)
        elif key == Qt.Key.Key_Down:
            self.pointing_callback(1)
        super().keyPressEvent(event)
        
