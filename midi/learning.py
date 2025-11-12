class LearningManager:
    def __init__(self):
        self.learning_mode = False
        self.learning_control_id = None
        self.learning_cc_out = False
    
    def start_learning_input(self, control_id):
        self.learning_mode = True
        self.learning_cc_out = False
        self.learning_control_id = control_id
    
    def start_learning_output(self, control_id):
        self.learning_mode = True
        self.learning_cc_out = True
        self.learning_control_id = control_id
    
    def cancel_learning(self):
        self.learning_mode = False
        self.learning_control_id = None
        self.learning_cc_out = False