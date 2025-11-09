# Mvave MIDI Bridge

This small utility converts messages from the **Mvave Chocolate** (or any other Bluetooth/USB MIDI controller) into usable events for your DAW.  
It allows you to map pedal switches to control tracks, effects, or any MIDI-mappable parameter with greater flexibility.

---

## 🚀 Installation & Setup

### 1. Install **loopMIDI**
- Download and install **loopMIDI** from [https://www.tobias-erichsen.de/software/loopmidi.html](https://www.tobias-erichsen.de/software/loopmidi.html)
- Open it and create a new port named **`mvave_midi`** by clicking the **`+`** button.

---

### 2. Run **mvave_midi.exe**
- Launch the `mvave_midi.exe` file (keep it running while using your DAW).
- When started, the program will ask you to select the input port:
  - If you’re using **Bluetooth**, the device will appear as `FootCtrl-bt`
  - If you’re using **USB-C**, it will appear as `USB-Midi`
- Then, select **`mvave_midi`** as the output port.

---

### 3. Configure your DAW (example: Ableton Live)
1. Open **Ableton Live**  
2. Go to **Options → Preferences → Link, Tempo & MIDI**
3. Under **MIDI Ports**, find **`mvave_midi`**
4. Enable the following options:
   - **Track**
   - **Remote**
5. Done! Your pedal can now control tracks, FX, or any parameter that supports MIDI mapping.

---

## 💡 Tips
- Keep **loopMIDI** and **mvave_midi.exe** open before launching your DAW.  
- If you rename the port in loopMIDI, make sure to select the same name when running the program.  
- You can use any other pedal or controller that sends standard MIDI messages.

---

## 🧠 Author
Experimental project developed to bridge Bluetooth MIDI controllers with DAWs using Python and Mido.  
Inspired by the need to **control Ableton with your feet without spending hundreds on dedicated hardware**.

---

## ⚙️ Dependencies (if running the Python source)
- Python 3.10+
- `mido`
- `python-rtmidi`

Example setup on Windows:
```bash
mvave_midi/Scripts/activate
pip install -r requirements.txt
python mvave_midi.py
```

## TODO

* Add graphical interface
* Control selector
* Better exception handling