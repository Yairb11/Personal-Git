from PyQt6.QtWidgets import QListWidgetItem

class MessageListWidgetItem(QListWidgetItem):
    
    def __init__(self, list_widget, message_block):
        super().__init__(list_widget)
        self.message_block = message_block
    
    def get_answer_widget(self):
        return self.message_block.answer_lbl
    
    def get_input_widget(self):
        return self.message_block.user_input_widget
    
    def resize(self):
        self.setSizeHint(self.message_block.sizeHint())