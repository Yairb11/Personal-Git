from PyQt6.QtWidgets import QListWidgetItem

class MessageListWidgetItem(QListWidgetItem):
    """Object for storing MessageBlock objects as QListWidgetItem widget and gaining more easily access to them
    """
    def __init__(self, list_widget, message_block):
        """Initiates basic QListWidgetItem with a pointer to MessageBlock object

        Args:
            list_widget (parent): QListWidget object
            message_block (MessageBlock): MessageBlock object pointer
        """
        super().__init__(list_widget)
        self.message_block = message_block
    
    def get_answer_widget(self):
        """Returns answer_lbl widget from pointer who stores MessageBlock 

        Returns:
            QLabel: answer_lbl widget
        """
        return self.message_block.answer_lbl
    
    def get_input_widget(self):
        """Returns user_input_widget widget from pointer who stores MessageBlock 

        Returns:
            QLineEdit: user_input_widget widget
        """
        return self.message_block.user_input_widget
    
    def resize(self):
        """Resizes QListWidgetItem to match MessageBlock size that is stores inside of it
        """
        self.setSizeHint(self.message_block.sizeHint())