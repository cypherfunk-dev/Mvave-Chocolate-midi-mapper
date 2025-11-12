import customtkinter as ctk

class MidiSwitch:
    def __init__(self, control_id, switch_number):
        self.control_id = control_id
        self.switch_number = switch_number
        self.input_cc_var = ctk.StringVar(value="No asignado")
        self.output_cc_var = ctk.StringVar(value=str(10 + switch_number - 1))
        self.mode_var = ctk.StringVar(value="toggle")
        self.state = False
        self.is_default = switch_number <= 4