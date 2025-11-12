import customtkinter as ctk
import mido

class MidiPortsPanel(ctk.CTkFrame):
    def __init__(self, parent, localization):
        super().__init__(parent)
        self.localization = localization
        self.build_ui()
    
    def build_ui(self):
        # Implementar interfaz de puertos MIDI
        pass
    
    def truncate_port_name(self, name, max_length=30):
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name