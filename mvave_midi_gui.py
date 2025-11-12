import customtkinter as ctk
import mido
import threading
import json
import os
from tkinter import scrolledtext, filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MidiBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mvave MIDI Bridge")
        self.geometry("800x750")

        # Cargar idiomas
        self.load_languages()
        self.current_language = "es"
        
        self.input_port = None
        self.output_port = None
        self.listening = False
        self.learning_mode = False
        self.learning_control_id = None
        self.learning_cc_out = False

        self.toggle_state = {}
        self.buttons = {}
        self.modes = {}
        self.control_vars = {}
        self.cc_out_vars = {}

        # Inicializar los 4 switches por defecto
        self.initialize_default_controls()
        self.build_ui()
        
        # Cargar configuración automáticamente al iniciar
        self.load_configuration_auto()

    def load_languages(self):
        """Carga los idiomas desde el archivo JSON"""
        try:
            with open('languages.json', 'r', encoding='utf-8') as f:
                self.languages = json.load(f)
        except FileNotFoundError:
            # Crear un archivo de idiomas por defecto si no existe
            default_languages = {
                "es": {
                    "app_title": "Mvave MIDI Bridge",
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
            with open('languages.json', 'w', encoding='utf-8') as f:
                json.dump(default_languages, f, ensure_ascii=False, indent=2)
            self.languages = default_languages

    def t(self, key):
        """Traduce una clave al idioma actual"""
        return self.languages.get(self.current_language, {}).get(key, key)

    def rebuild_ui(self):
        """Reconstruye completamente la interfaz con el nuevo idioma"""
        # Destruir todos los widgets existentes
        for widget in self.winfo_children():
            widget.destroy()
        
        # Reconstruir la interfaz completa
        self.build_ui()
        
        # Restaurar el estado de conexión si estaba conectado
        if self.listening:
            self.connect_btn.configure(text=self.t("disconnect"), fg_color="red")
            self.learn_btn.configure(state="normal")

    def truncate_port_name(self, name, max_length=30):
        """Trunca el nombre del puerto MIDI si es muy largo"""
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name

    # ---------------- UI ----------------
    def build_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text=self.t("app_title"), font=("Arial", 20, "bold")).pack(pady=10)

        # ----- Configuración y Puertos -----
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(pady=10, padx=10, fill="x")

        # Fila 1: Idioma
        row1_frame = ctk.CTkFrame(config_frame)
        row1_frame.pack(fill="x", pady=5)

        # Selector de idioma
        ctk.CTkLabel(row1_frame, text=self.t("language")).pack(side="left", padx=5)
        self.language_menu = ctk.CTkOptionMenu(row1_frame, values=["es", "en"], 
                                              command=self.change_language)
        self.language_menu.set(self.current_language)
        self.language_menu.pack(side="left", padx=5)

        # Fila 2: Puertos MIDI
        row2_frame = ctk.CTkFrame(config_frame)
        row2_frame.pack(fill="x", pady=5)

        # Obtener nombres de puertos truncados
        input_ports = [self.truncate_port_name(name) for name in mido.get_input_names()]
        output_ports = [self.truncate_port_name(name) for name in mido.get_output_names()]

        ctk.CTkLabel(row2_frame, text=self.t("input_midi")).pack(side="left", padx=5)
        self.input_menu = ctk.CTkOptionMenu(row2_frame, values=input_ports)
        self.input_menu.pack(side="left", padx=5)

        ctk.CTkLabel(row2_frame, text=self.t("output_midi")).pack(side="left", padx=(20, 5))
        self.output_menu = ctk.CTkOptionMenu(row2_frame, values=output_ports)
        self.output_menu.pack(side="left", padx=5)

        # Fila 3: Botones de conexión y aprendizaje
        row3_frame = ctk.CTkFrame(config_frame)
        row3_frame.pack(fill="x", pady=5)

        self.connect_btn = ctk.CTkButton(row3_frame, text=self.t("connect"), 
                                       command=self.toggle_connection)
        self.connect_btn.pack(side="left", padx=5)

        self.learn_btn = ctk.CTkButton(row3_frame, text=self.t("learn_controls"), 
                                     command=self.toggle_learning_mode,
                                     fg_color="orange", state="disabled")
        self.learn_btn.pack(side="left", padx=5)

        # Fila 4: Botones de configuración
        row4_frame = ctk.CTkFrame(config_frame)
        row4_frame.pack(fill="x", pady=5)

        self.save_btn = ctk.CTkButton(row4_frame, text=self.t("save_config"), 
                                    command=self.save_configuration,
                                    fg_color="green")
        self.save_btn.pack(side="left", padx=5)

        self.load_btn = ctk.CTkButton(row4_frame, text=self.t("load_config"), 
                                    command=self.load_configuration,
                                    fg_color="blue")
        self.load_btn.pack(side="left", padx=5)

        # ----- Controles MIDI -----
        self.controls_frame = ctk.CTkFrame(main_frame)
        self.controls_frame.pack(pady=10, padx=10, fill="x")
        
        # Frame para los controles existentes
        self.existing_controls_frame = ctk.CTkFrame(self.controls_frame)
        self.existing_controls_frame.pack(pady=5, padx=10, fill="x")
        
        # Botón para agregar nuevo switch
        self.add_switch_btn = ctk.CTkButton(self.controls_frame, text=f"+ {self.t('add_switch')}", 
                                           command=self.add_new_switch, fg_color="green")
        self.add_switch_btn.pack(pady=10)

        # Construir los controles iniciales
        self.build_controls()

        # ----- Consola -----
        self.console_frame = ctk.CTkFrame(main_frame)
        self.console_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        ctk.CTkLabel(self.console_frame, text=self.t("debug_console"), anchor="w").pack(pady=(10, 0), padx=10, fill="x")
        self.console = scrolledtext.ScrolledText(self.console_frame, height=10, state="disabled", bg="#111", fg="#0f0")
        self.console.pack(fill="both", expand=True, padx=10, pady=5)

    def change_language(self, language):
        """Cambia el idioma de la aplicación y reconstruye la interfaz"""
        if language != self.current_language:
            self.current_language = language
            self.rebuild_ui()

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.configure(state="disabled")
        self.console.yview("end")

    # ---------------- Configuración ----------------
    def save_configuration(self):
        """Guarda la configuración actual a un archivo JSON"""
        config = {
            "language": self.current_language,
            "input_port": self.input_menu.get(),
            "output_port": self.output_menu.get(),
            "switches": {}
        }
        
        for control_id in self.buttons.keys():
            config["switches"][control_id] = {
                "input_cc": self.control_vars[control_id].get(),
                "output_cc": self.cc_out_vars[control_id].get(),
                "mode": self.modes[control_id].get(),
                "state": self.toggle_state.get(control_id, False)
            }
        
        # Usar config.json como nombre por defecto
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.t("save_config"),
            initialfile="config.json"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                self.log(f"✓ {self.t('config_saved')}: {file_path}")
            except Exception as e:
                self.log(f"❌ Error guardando configuración: {e}")

    def load_configuration(self):
        """Carga la configuración desde un archivo JSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title=self.t("load_config"),
            initialfile="config.json"
        )
        
        if file_path:
            self.load_config_from_file(file_path)

    def load_configuration_auto(self):
        """Intenta cargar la configuración automáticamente al iniciar"""
        auto_config_path = "config.json"
        if os.path.exists(auto_config_path):
            try:
                self.load_config_from_file(auto_config_path)
                self.log(f"✓ Configuración cargada automáticamente")
            except Exception as e:
                self.log(f"❌ Error cargando configuración automática: {e}")

    def load_config_from_file(self, file_path):
        """Carga la configuración desde un archivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Guardar el estado de conexión actual
            was_connected = self.listening
            if was_connected:
                self.disconnect_ports()
            
            # Cargar idioma
            if "language" in config:
                self.current_language = config["language"]
                # Reconstruir la interfaz con el nuevo idioma
                self.rebuild_ui()
            
            # Cargar puertos MIDI (usando nombres reales, no truncados)
            input_ports_real = mido.get_input_names()
            output_ports_real = mido.get_output_names()
            
            if "input_port" in config:
                # Buscar el puerto real que coincida con el nombre guardado (puede estar truncado)
                saved_input = config["input_port"]
                for real_port in input_ports_real:
                    if self.truncate_port_name(real_port) == saved_input or real_port == saved_input:
                        self.input_menu.set(self.truncate_port_name(real_port))
                        break
            
            if "output_port" in config:
                saved_output = config["output_port"]
                for real_port in output_ports_real:
                    if self.truncate_port_name(real_port) == saved_output or real_port == saved_output:
                        self.output_menu.set(self.truncate_port_name(real_port))
                        break
            
            # Limpiar controles existentes
            self.buttons.clear()
            self.control_vars.clear()
            self.cc_out_vars.clear()
            self.toggle_state.clear()
            self.modes.clear()
            
            # Cargar switches
            if "switches" in config:
                for control_id, switch_config in config["switches"].items():
                    self.control_vars[control_id] = ctk.StringVar(value=switch_config.get("input_cc", self.t("not_assigned")))
                    self.cc_out_vars[control_id] = ctk.StringVar(value=switch_config.get("output_cc", "10"))
                    self.toggle_state[control_id] = switch_config.get("state", False)
                    self.modes[control_id] = ctk.StringVar(value=switch_config.get("mode", "toggle"))
            
            # Reconstruir controles
            self.build_controls()
            self.refresh_all_buttons()
            
            self.log(f"✓ {self.t('config_loaded')}: {file_path}")
            
            # Reconectar si estaba conectado antes
            if was_connected:
                self.after(100, self.toggle_connection)
            
        except Exception as e:
            self.log(f"❌ Error cargando configuración: {e}")

    # ---------------- Controles ----------------
    def initialize_default_controls(self):
        """Inicializa los 4 switches por defecto"""
        for i in range(4):
            control_id = f"btn_{i}"
            self.control_vars[control_id] = ctk.StringVar(value=self.t("not_assigned"))
            self.cc_out_vars[control_id] = ctk.StringVar(value=str(10 + i))
            self.toggle_state[control_id] = False
            self.modes[control_id] = ctk.StringVar(value="toggle")

    def build_controls(self):
        """Construye todos los controles en la interfaz"""
        # Limpiar frame existente
        for widget in self.existing_controls_frame.winfo_children():
            widget.destroy()

        # Obtener la lista de control_ids ordenados
        control_ids = sorted(self.control_vars.keys(), key=lambda x: int(x.split('_')[1]))
        
        for control_id in control_ids:
            self.create_control_widget(control_id)

        # Actualizar estado del botón agregar
        self.update_add_button_state()

    def create_control_widget(self, control_id):
        """Crea un widget de control individual"""
        frame = ctk.CTkFrame(self.existing_controls_frame)
        frame.pack(pady=5, padx=10, fill="x")

        # Extraer el número del control_id
        control_num = int(control_id.split('_')[1]) + 1

        # Botón principal con función de aprendizaje
        btn = ctk.CTkButton(frame, text=f"{self.t('switch')} {control_num}", fg_color="gray",
                            command=lambda cid=control_id: self.start_learning_for_control(cid))
        btn.pack(side="left", padx=5, pady=5)
        self.buttons[control_id] = btn

        # Selector de modo
        mode_var = self.modes.get(control_id, ctk.StringVar(value="toggle"))
        mode_menu = ctk.CTkOptionMenu(frame, values=[self.t("toggle"), self.t("momentary")], 
                                     variable=mode_var)
        mode_menu.pack(side="right", padx=5)
        self.modes[control_id] = mode_var

        # Campo para CC de entrada (lectura durante aprendizaje)
        ctk.CTkLabel(frame, text=self.t("input_cc")).pack(side="left", padx=(10, 2))
        entry_cc = ctk.CTkEntry(frame, width=80, textvariable=self.control_vars[control_id], state="readonly")
        entry_cc.pack(side="left", padx=5)

        # Campo para CC de salida (editable)
        ctk.CTkLabel(frame, text=self.t("output_cc")).pack(side="left", padx=(10, 2))
        entry_cc_out = ctk.CTkEntry(frame, width=80, textvariable=self.cc_out_vars[control_id])
        entry_cc_out.pack(side="left", padx=5)

        # Botón para eliminar switch (solo para switches adicionales)
        if int(control_id.split('_')[1]) >= 4:  # Los primeros 4 (0-3) son fijos
            delete_btn = ctk.CTkButton(frame, text=self.t("delete"), width=60, fg_color="red",
                                     command=lambda cid=control_id: self.delete_switch(cid))
            delete_btn.pack(side="left", padx=5)

    def add_new_switch(self):
        """Agrega un nuevo switch dinámicamente"""
        # Verificar límite máximo (10 switches)
        if len(self.buttons) >= 10:
            self.log(f"❌ {self.t('limit_reached')}: 10 {self.t('switch').lower()}s")
            return
            
        # Encontrar el próximo ID disponible
        existing_ids = [int(ctrl_id.split('_')[1]) for ctrl_id in self.buttons.keys()]
        next_id = max(existing_ids) + 1 if existing_ids else 4
        
        control_id = f"btn_{next_id}"
        
        # Inicializar variables para el nuevo control
        self.control_vars[control_id] = ctk.StringVar(value=self.t("not_assigned"))
        self.cc_out_vars[control_id] = ctk.StringVar(value=str(10 + next_id))
        self.toggle_state[control_id] = False
        self.modes[control_id] = ctk.StringVar(value="toggle")
        
        # Reconstruir todos los controles
        self.build_controls()
        
        self.log(f"✓ {self.t('switch')} {next_id + 1} {self.t('add_switch').lower()}")
        self.update_add_button_state()

    def delete_switch(self, control_id):
        """Elimina un switch dinámicamente"""
        # No permitir eliminar los primeros 4 switches
        control_num = int(control_id.split('_')[1])
        if control_num < 4:
            self.log(f"❌ No se pueden eliminar los primeros 4 {self.t('switch').lower()}s")
            return
            
        # Remover el control
        if control_id in self.buttons:
            del self.buttons[control_id]
        if control_id in self.control_vars:
            del self.control_vars[control_id]
        if control_id in self.cc_out_vars:
            del self.cc_out_vars[control_id]
        if control_id in self.toggle_state:
            del self.toggle_state[control_id]
        if control_id in self.modes:
            del self.modes[control_id]
            
        # Reconstruir todos los controles
        self.build_controls()
        
        self.log(f"✓ {self.t('switch')} {control_num + 1} {self.t('delete').lower()}")
        self.update_add_button_state()

    def update_add_button_state(self):
        """Actualiza el estado del botón agregar según el límite"""
        if len(self.buttons) >= 10:
            self.add_switch_btn.configure(state="disabled", text=f"{self.t('limit_reached')} (10)")
        else:
            self.add_switch_btn.configure(state="normal", text=f"+ {self.t('add_switch')} ({len(self.buttons)}/10)")

    def toggle_learning_mode(self):
        """Activa/desactiva el modo de aprendizaje global"""
        if not self.learning_mode:
            self.learning_mode = True
            self.learning_cc_out = False
            self.learn_btn.configure(text=self.t("cancel_learn"), fg_color="red")
            self.log(self.t("learn_mode_active"))
            self.log(self.t("learn_instructions"))
            
            # Cambiar todos los botones a modo aprendizaje
            for control_id, btn in self.buttons.items():
                btn.configure(text=f"Aprender...", fg_color="orange")
        else:
            self.cancel_learning_mode()

    def cancel_learning_mode(self):
        """Cancela el modo de aprendizaje"""
        self.learning_mode = False
        self.learning_cc_out = False
        self.learning_control_id = None
        self.learn_btn.configure(text=self.t("learn_controls"), fg_color="orange")
        self.refresh_all_buttons()
        self.log("Modo aprendizaje cancelado")

    def start_learning_for_control(self, control_id):
        """Inicia el aprendizaje para un control específico (CC entrada)"""
        if not self.learning_mode or self.learning_cc_out:
            return
            
        self.learning_control_id = control_id
        self.buttons[control_id].configure(text="¡Presiona control físico!", fg_color="yellow")
        self.log(f"Esperando input MIDI para CC ENTRADA de {control_id}...")

    def refresh_all_buttons(self):
        """Actualiza todos los botones con su estado actual"""
        for control_id, btn in self.buttons.items():
            cc_value = self.control_vars[control_id].get()
            cc_out_value = self.cc_out_vars[control_id].get()
            state = self.toggle_state.get(control_id, False)
            
            if cc_value == self.t("not_assigned"):
                control_num = int(control_id.split('_')[1]) + 1
                btn_text = f"{self.t('switch')} {control_num}"
                btn.configure(text=btn_text, fg_color="gray")
            else:
                color = "green" if state else "red"
                # Mostrar ambos CCs
                btn_text = f"CC{cc_value}→CC{cc_out_value}: {'ON' if state else 'OFF'}"
                btn.configure(text=btn_text, fg_color=color)

    def refresh_button_label(self, control_id):
        """Actualiza el texto de un botón específico"""
        btn = self.buttons.get(control_id)
        if not btn:
            return
        cc_number = self.control_vars[control_id].get()
        cc_out_number = self.cc_out_vars[control_id].get()
        state = self.toggle_state.get(control_id, False)
        
        if cc_number == self.t("not_assigned"):
            control_num = int(control_id.split('_')[1]) + 1
            btn.configure(text=f"{self.t('switch')} {control_num}")
        else:
            color = "green" if state else "red"
            # Mostrar ambos CCs
            btn_text = f"CC{cc_number}→CC{cc_out_number}: {'ON' if state else 'OFF'}"
            btn.configure(text=btn_text, fg_color=color)

    def toggle_connection(self):
        if not self.listening:
            try:
                # Obtener nombres reales de los puertos (no truncados)
                input_ports_real = mido.get_input_names()
                output_ports_real = mido.get_output_names()
                
                selected_input = self.input_menu.get()
                selected_output = self.output_menu.get()
                
                # Buscar el puerto real que coincida con el nombre truncado
                real_input = None
                for port in input_ports_real:
                    if self.truncate_port_name(port) == selected_input:
                        real_input = port
                        break
                
                real_output = None
                for port in output_ports_real:
                    if self.truncate_port_name(port) == selected_output:
                        real_output = port
                        break
                
                if real_input is None or real_output is None:
                    self.log("Error: No se pudo encontrar el puerto MIDI real")
                    return
                
                self.input_port = mido.open_input(real_input)
                self.output_port = mido.open_output(real_output)
                self.connect_btn.configure(text=self.t("disconnect"), fg_color="red")
                self.learn_btn.configure(state="normal")
                self.listening = True
                threading.Thread(target=self.listen_midi, daemon=True).start()
                self.log(f"Conectado a {real_input} → {real_output}")
                self.log("Presiona 'Aprender Controles' para mapear tus botones físicos")
                
                # Mostrar los valores por defecto en la consola
                self.log("Valores por defecto CC Salida:")
                for control_id in sorted(self.buttons.keys(), key=lambda x: int(x.split('_')[1])):
                    cc_out = self.cc_out_vars[control_id].get()
                    control_num = int(control_id.split('_')[1]) + 1
                    self.log(f"  {self.t('switch')} {control_num}: CC{cc_out}")
                
            except Exception as e:
                self.log(f"Error al conectar: {e}")
        else:
            self.disconnect_ports()

    def disconnect_ports(self):
        self.listening = False
        self.cancel_learning_mode()
        try:
            if self.input_port:
                self.input_port.close()
            if self.output_port:
                self.output_port.close()
            self.log("Puertos MIDI desconectados.")
        except Exception as e:
            self.log(f"Error al desconectar: {e}")
        self.connect_btn.configure(text=self.t("connect"), fg_color="green")
        self.learn_btn.configure(state="disabled")

    def listen_midi(self):
        while self.listening:
            try:
                for msg in self.input_port.iter_pending():
                    if msg.type == "control_change":
                        self.handle_cc(msg)
            except Exception as e:
                self.log(f"Error en listen_midi: {e}")
                break
        self.log("Hilo MIDI detenido.")

    def handle_cc(self, msg):
        """Maneja mensajes CC entrantes del controlador MIDI"""
        control = msg.control
        value = msg.value
        
        self.log(f"MIDI IN: CC{control} = {value}")
        
        # Si estamos en modo aprendizaje
        if self.learning_mode and self.learning_control_id:
            control_id = self.learning_control_id
            
            if self.learning_cc_out:
                # Aprendiendo CC de salida
                self.cc_out_vars[control_id].set(str(control))
                self.log(f"✓ CC SALIDA para {control_id} asignado a CC{control}")
            else:
                # Aprendiendo CC de entrada
                self.control_vars[control_id].set(str(control))
                self.log(f"✓ CC ENTRADA para {control_id} asignado a CC{control}")
            
            self.learning_control_id = None
            self.learning_cc_out = False
            self.refresh_button_label(control_id)
            
            # Si no estamos aprendiendo CC de salida, verificar si todos los controles están asignados
            if not self.learning_cc_out and all(cc.get() != self.t("not_assigned") for cc in self.control_vars.values()):
                self.log("✓ Todos los controles de ENTRADA han sido asignados!")
                self.cancel_learning_mode()
            return
        
        # Buscar qué botón está mapeado a este número CC de entrada
        matching_control_id = None
        for control_id, cc_var in self.control_vars.items():
            try:
                if cc_var.get() != self.t("not_assigned") and int(cc_var.get()) == control:
                    matching_control_id = control_id
                    break
            except ValueError:
                continue
        
        if not matching_control_id:
            self.log(f"CC{control} no está mapeado a ningún botón")
            return

        mode = self.modes[matching_control_id].get()
        
        if mode == self.t("toggle"):
            # En modo toggle, alterna el estado cuando recibe cualquier valor > 0
            current_state = self.toggle_state.get(matching_control_id, False)
            state = not current_state if value > 0 else current_state
        else:
            # En modo momentary, el estado sigue el valor del mensaje
            state = value > 0

        self.toggle_state[matching_control_id] = state
        self.refresh_button_label(matching_control_id)
        
        # Obtener el CC de salida (siempre habrá uno por defecto)
        cc_out_value = self.cc_out_vars[matching_control_id].get()
        try:
            cc_to_send = int(cc_out_value)
            control_num = int(matching_control_id.split('_')[1]) + 1
            self.log(f"{self.t('switch')} {control_num} (CC{control}→CC{cc_to_send}) → {'ON' if state else 'OFF'}")
            # Enviar el mensaje MIDI
            self.send_cc(cc_to_send, 127 if state else 0)
        except ValueError:
            self.log(f"Error: CC de salida inválido para {matching_control_id}: {cc_out_value}")

    def send_cc(self, control, value):
        if self.output_port:
            try:
                control_int = int(control)
                if 0 <= control_int <= 127 and 0 <= value <= 127:
                    msg = mido.Message("control_change", control=control_int, value=value)
                    self.output_port.send(msg)
                    self.log(f"MIDI OUT: CC{control_int} = {value}")
                else:
                    self.log(f"Valor CC inválido: {control_int}={value}")
            except ValueError:
                self.log(f"CC inválido: {control}")


if __name__ == "__main__":
    app = MidiBridgeApp()
    app.mainloop()