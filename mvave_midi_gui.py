import customtkinter as ctk
import mido
import threading
from tkinter import scrolledtext

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MidiBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mvave MIDI Bridge")
        self.geometry("650x600")

        self.input_port = None
        self.output_port = None
        self.listening = False

        self.toggle_state = {}
        self.buttons = {}
        self.modes = {}
        self.control_vars = {}

        self.build_ui()

    # ---------------- UI ----------------
    def build_ui(self):
        ctk.CTkLabel(self, text="Mvave MIDI Bridge", font=("Arial", 20, "bold")).pack(pady=10)

        # ----- Puertos -----
        ports_frame = ctk.CTkFrame(self)
        ports_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(ports_frame, text="Entrada MIDI:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.input_menu = ctk.CTkOptionMenu(ports_frame, values=mido.get_input_names())
        self.input_menu.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(ports_frame, text="Salida MIDI:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.output_menu = ctk.CTkOptionMenu(ports_frame, values=mido.get_output_names())
        self.output_menu.grid(row=1, column=1, padx=5, pady=5)

        self.connect_btn = ctk.CTkButton(ports_frame, text="Conectar", command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # ----- Controles MIDI -----
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(pady=10, padx=10, fill="x")
        self.control_list = [20, 21, 22, 23]
        self.build_controls()

        # ----- Consola -----
        ctk.CTkLabel(self, text="Consola de depuración:", anchor="w").pack(pady=(10, 0), padx=10, fill="x")
        self.console = scrolledtext.ScrolledText(self, height=10, state="disabled", bg="#111", fg="#0f0")
        self.console.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.configure(state="disabled")
        self.console.yview("end")

    # ---------------- Controles ----------------
    def build_controls(self):
        for widget in self.controls_frame.winfo_children():
            widget.destroy()

        for i, control in enumerate(self.control_list):
            frame = ctk.CTkFrame(self.controls_frame)
            frame.pack(pady=5, padx=10, fill="x")

            btn = ctk.CTkButton(frame, text=f"CC {control}: OFF", fg_color="gray",
                                command=lambda c=control: self.on_button_click(c))
            btn.pack(side="left", padx=5, pady=5)
            self.buttons[control] = btn
            self.toggle_state[control] = False

            # Selector de modo
            mode_var = ctk.StringVar(value="toggle")
            mode_menu = ctk.CTkOptionMenu(frame, values=["toggle", "momentary"],
                                          variable=mode_var)
            mode_menu.pack(side="right", padx=5)
            self.modes[control] = mode_var

            # Campo para editar el número CC
            ctk.CTkLabel(frame, text="CC#:").pack(side="left", padx=(10, 2))
            var_cc = ctk.StringVar(value=str(control))
            entry_cc = ctk.CTkEntry(frame, width=50, textvariable=var_cc)
            entry_cc.pack(side="left", padx=5)
            self.control_vars[control] = var_cc

    # ---------------- MIDI ----------------
    def toggle_connection(self):
        if not self.listening:
            try:
                in_name = self.input_menu.get()
                out_name = self.output_menu.get()
                self.input_port = mido.open_input(in_name)
                self.output_port = mido.open_output(out_name)
                self.connect_btn.configure(text="Desconectar", fg_color="red")
                self.listening = True
                threading.Thread(target=self.listen_midi, daemon=True).start()
                self.log(f"Conectado a {in_name} → {out_name}")
            except Exception as e:
                self.log(f"Error al conectar: {e}")
        else:
            self.disconnect_ports()

    def disconnect_ports(self):
        self.listening = False
        try:
            if self.input_port:
                self.input_port.close()
            if self.output_port:
                self.output_port.close()
            self.log("Puertos MIDI desconectados.")
        except Exception as e:
            self.log(f"Error al desconectar: {e}")
        self.connect_btn.configure(text="Conectar", fg_color="green")

    def listen_midi(self):
        while self.listening:
            for msg in self.input_port.iter_pending():
                if msg.type == "control_change":
                    self.handle_cc(msg)
        self.log("Hilo MIDI detenido.")

    def handle_cc(self, msg):
        control = msg.control
        value = msg.value
        mode = self.modes.get(control, None)
        if not mode:
            return

        if mode.get() == "momentary":
            state = value > 0
        else:
            current = self.toggle_state.get(control, False)
            state = not current

        self.toggle_state[control] = state
        self.update_button_ui(control, state)
        self.log(f"IN CC{control} val={value} → {'ON' if state else 'OFF'}")

    def send_cc(self, control, value):
        if self.output_port:
            msg = mido.Message("control_change", control=control, value=value)
            self.output_port.send(msg)
            self.log(f"OUT CC{control} val={value}")

    def update_button_ui(self, control, state):
        btn = self.buttons.get(control)
        if not btn:
            return
        if state:
            btn.configure(text=f"CC {control}: ON", fg_color="green")
            
        else:
            btn.configure(text=f"CC {control}: OFF", fg_color="gray")

    def on_button_click(self, control):
        try:
            new_cc = int(self.control_vars[control].get())
        except ValueError:
            self.log(f"CC inválido para control {control}")
            return

        mode = self.modes[control].get()
        if mode == "momentary":
            self.send_cc(new_cc, 127)
            self.after(200, lambda: self.send_cc(new_cc, 0))
        else:
            current = self.toggle_state.get(control, False)
            new_state = not current
            if not (0 <= new_cc <= 127):
                self.log(f"CC inválido para control {control}: {new_cc} (debe estar entre 0 y 127)")
                return
            self.toggle_state[control] = new_state
            self.update_button_ui(control, new_state)
            self.send_cc(new_cc, 127 if new_state else 0)


if __name__ == "__main__":
    app = MidiBridgeApp()
    app.mainloop()
