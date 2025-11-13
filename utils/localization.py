import json

class Localization:
    def __init__(self):
        self.languages = {}
        self.current_language = "en"
        self.load_languages()
    
    def load_languages(self):
        """Carga los idiomas desde el archivo JSON"""
        try:
            with open('config/languages.json', 'r', encoding='utf-8') as f:
                self.languages = json.load(f)
        except FileNotFoundError:
            # Cargar idiomas por defecto si el archivo no existe
            self.languages = {
                "es": {
                    "app_title": "Bluetooth MIDI Bridge",
                    "input_midi": "Entrada MIDI:",
                    "output_midi": "Salida MIDI:",
                    "connect": "Conectar",
                    "disconnect": "Desconectar",
                    "learn_controls": "Aprender Controles",
                    "cancel_learn": "Cancelar Aprendizaje",
                    "add_switch": "Agregar Nuevo Switch",
                    "delete": "Eliminar",
                    "input_cc": "CC Entrada:",
                    "output_cc": "CC Salida:",
                    "mode": "Modo:",
                    "toggle": "Toggle",
                    "momentary": "Momentary",
                    "debug_console": "Consola de depuración:",
                    "learn_mode_active": "MODO APRENDIZAJE ACTIVADO - CC ENTRADA",
                    "learn_instructions": "Haz clic en un botón de la interfaz y luego presiona el control físico que quieres asignar",
                    "switch": "Switch",
                    "not_assigned": "No asignado",
                    "limit_reached": "Límite alcanzado",
                    "save_config": "Guardar Config",
                    "load_config": "Cargar Config",
                    "config_saved": "Configuración guardada",
                    "config_loaded": "Configuración cargada",
                    "language": "Idioma:"
                },
                "en": {
                    "app_title": "Mvave MIDI Bridge",
                    "input_midi": "MIDI Input:",
                    "output_midi": "MIDI Output:",
                    "connect": "Connect",
                    "disconnect": "Disconnect",
                    "learn_controls": "Learn Controls",
                    "cancel_learn": "Cancel Learning",
                    "add_switch": "Add New Switch",
                    "delete": "Delete",
                    "input_cc": "Input CC:",
                    "output_cc": "Output CC:",
                    "mode": "Mode:",
                    "toggle": "Toggle",
                    "momentary": "Momentary",
                    "debug_console": "Debug Console:",
                    "learn_mode_active": "LEARNING MODE ACTIVE - INPUT CC",
                    "learn_instructions": "Click on an interface button and then press the physical control you want to assign",
                    "switch": "Switch",
                    "not_assigned": "Not assigned",
                    "limit_reached": "Limit reached",
                    "save_config": "Save Config",
                    "load_config": "Load Config",
                    "config_saved": "Configuration saved",
                    "config_loaded": "Configuration loaded",
                    "language": "Language:"
                }
            }
    
    def t(self, key):
        """Traduce una clave al idioma actual"""
        return self.languages.get(self.current_language, {}).get(key, key)