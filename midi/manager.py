import mido
import threading
from config.settings import AppSettings

class MidiManager:
    def __init__(self):
        self.input_port = None
        self.output_port = None
        self.listening = False
        self.message_callback = None
        self.settings = AppSettings()
    
    def get_input_ports_truncated(self):
        """Obtiene lista de puertos de entrada truncados"""
        return [self.truncate_port_name(name) for name in mido.get_input_names()]
    
    def get_output_ports_truncated(self):
        """Obtiene lista de puertos de salida truncados"""
        return [self.truncate_port_name(name) for name in mido.get_output_names()]
    
    def truncate_port_name(self, name, max_length=None):
        """Trunca el nombre del puerto MIDI si es muy largo"""
        if max_length is None:
            max_length = self.settings.MAX_PORT_NAME_LENGTH
            
        if len(name) > max_length:
            return name[:max_length-3] + "..."
        return name
    
    def get_real_port_name(self, truncated_name, port_list):
        """Obtiene el nombre real del puerto a partir del nombre truncado"""
        for real_name in port_list:
            if self.truncate_port_name(real_name) == truncated_name:
                return real_name
        return truncated_name  # Si no encuentra, devuelve el original
    
    def connect_ports(self, input_port_truncated, output_port_truncated, message_callback):
        """Conecta a los puertos MIDI usando nombres truncados"""
        try:
            # Obtener nombres reales
            input_ports_real = mido.get_input_names()
            output_ports_real = mido.get_output_names()
            
            real_input = self.get_real_port_name(input_port_truncated, input_ports_real)
            real_output = self.get_real_port_name(output_port_truncated, output_ports_real)
            
            if real_input not in input_ports_real:
                raise Exception(f"Puerto de entrada no encontrado: {real_input}")
            if real_output not in output_ports_real:
                raise Exception(f"Puerto de salida no encontrado: {real_output}")
            
            self.input_port = mido.open_input(real_input)
            self.output_port = mido.open_output(real_output)
            self.message_callback = message_callback
            self.listening = True
            
            # Iniciar hilo de escucha
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error conectando puertos MIDI: {e}")
            return False
    
    def _listen_loop(self):
        """Bucle de escucha de mensajes MIDI"""
        while self.listening:
            try:
                for msg in self.input_port.iter_pending():
                    if self.message_callback:
                        self.message_callback(msg)
            except Exception as e:
                if self.listening:  # Solo loguear errores si todavía estamos escuchando
                    print(f"Error en listen_loop: {e}")
                break
    
    def disconnect_ports(self):
        """Desconecta los puertos MIDI"""
        self.listening = False
        try:
            if self.input_port:
                self.input_port.close()
            if self.output_port:
                self.output_port.close()
        except Exception as e:
            print(f"Error desconectando puertos: {e}")
        finally:
            self.input_port = None
            self.output_port = None
            self.message_callback = None
    
    def send_cc(self, control, value):
        """Envía un mensaje CC"""
        if self.output_port and self.listening:
            try:
                control_int = int(control)
                if 0 <= control_int <= 127 and 0 <= value <= 127:
                    msg = mido.Message("control_change", control=control_int, value=value)
                    self.output_port.send(msg)
                    return True
                else:
                    print(f"Valores CC inválidos: control={control_int}, value={value}")
            except ValueError:
                print(f"CC inválido: {control}")
            except Exception as e:
                print(f"Error enviando CC: {e}")
        return False
    
    def is_connected(self):
        """Verifica si está conectado"""
        return self.listening and self.input_port and self.output_port