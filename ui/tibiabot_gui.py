# Ruta: ui/tibiabot_gui.py - Clase TibiabotGUI COMPLETA y FINAL

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import os
import shutil
import threading
import time
import logging
from datetime import datetime
import sys
import pyautogui

# Ruta raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Importar el motor del bot
try:
    from bot_engine import run_bot
except ImportError as e:
    logging.error(f"No se pudo importar bot_engine.py: {e}")
    def run_bot():
        logging.info("Bot no disponible - bot_engine.py no encontrado.")
        messagebox.showwarning("Advertencia", "bot_engine.py no encontrado o sin función run_bot().")

# Configuración de logging
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, 'bot_log.txt')
open(log_file, 'w').close()  # Limpiar log

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

class ColoredTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.tags = {
            logging.DEBUG: "gray",
            logging.INFO: "lime",
            logging.WARNING: "yellow",
            logging.ERROR: "red",
            logging.CRITICAL: "orange"
        }

    def emit(self, record):
        msg = self.format(record)
        color = self.tags.get(record.levelno, "white")
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n', color)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)

class TibiabotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tibiabot v2.1 PRO - Grok Edition 🎄")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e2e")
        self.root.state('zoomed')  # Maximizar ventana

        self.bot_running = False
        self.bot_thread = None

        self.config_path = os.path.join(project_root, 'config.json')
        self.config = self.load_config()

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1e1e2e")
        style.configure("TNotebook.Tab", background="#2d2d44", foreground="white", padding=[20, 10])
        style.map("TNotebook.Tab", background=[("selected", "#3a3a5a")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        self.control_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.calibrate_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)
        self.healing_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.control_frame, text="Control")
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.calibrate_frame, text="Calibrar")
        self.notebook.add(self.logs_frame, text="Logs")
        self.notebook.add(self.healing_frame, text="Healing Status")

        self.setup_control_tab()
        self.setup_settings_tab()
        self.setup_calibrate_tab()
        self.setup_logs_tab()
        self.setup_healing_tab()

        logging.info("=== TIBIABOT PRO GUI INICIADO ===")
        logging.info("Interfaz gráfica cargada correctamente.")

        self.auto_load_and_calibrate()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando config.json: {e}")
                return {"regions": {}, "hotkeys": {}}
        return {"regions": {}, "hotkeys": {}}

    def save_config(self):
        try:
            backup_path = self.config_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.config_path):
                shutil.copy(self.config_path, backup_path)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("config.json guardado correctamente.")
            messagebox.showinfo("Guardado", "Configuración guardada!")
        except Exception as e:
            logging.error(f"No se pudo guardar config.json: {e}")
            messagebox.showerror("Error", "No se pudo guardar config.json")

    # === CONTROL TAB ===
    def setup_control_tab(self):
        frame = ttk.Frame(self.control_frame)
        frame.pack(expand=True)

        title = tk.Label(frame, text="TIBIABOT v2.1 PRO", font=("Arial", 40, "bold"), bg="#1e1e2e", fg="#00d4ff")
        title.pack(pady=60)

        subtitle = tk.Label(frame, text="Grok Edition - Full Autonomous 🎄", font=("Arial", 18), bg="#1e1e2e", fg="#a0a0ff")
        subtitle.pack(pady=10)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=60)

        self.start_button = tk.Button(btn_frame, text="START BOT", font=("Arial", 24, "bold"), bg="#27ae60", fg="white",
                                      width=25, height=3, command=self.start_bot)
        self.start_button.pack(pady=30)

        self.stop_button = tk.Button(btn_frame, text="STOP BOT", font=("Arial", 24, "bold"), bg="#c0392b", fg="white",
                                     width=25, height=3, command=self.stop_bot, state="disabled")
        self.stop_button.pack(pady=20)

        self.status_label = tk.Label(frame, text="Estado: Detenido", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="#e74c3c")
        self.status_label.pack(pady=50)

    def start_bot(self):
        if self.bot_running:
            return
        logging.info("=== BOT INICIADO ===")
        self.bot_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Estado: Ejecutándose", fg="#27ae60")
        self.bot_thread = threading.Thread(target=run_bot, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        logging.info("=== BOT DETENIDO POR USUARIO ===")
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Estado: Detenido", fg="#e74c3c")

    # === SETTINGS TAB ===
    def setup_settings_tab(self):
        frame = ttk.Frame(self.settings_frame)
        frame.pack(fill='both', expand=True, padx=30, pady=30)

        title = tk.Label(frame, text="PERSONALIZACIÓN", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="#00d4ff")
        title.pack(pady=20)

        # Hotkeys
        hotkeys_frame = tk.LabelFrame(frame, text="Hotkeys", font=("Arial", 16), bg="#2d2d44", fg="white")
        hotkeys_frame.pack(fill='x', pady=10, padx=20)

        self.hotkey_entries = {}
        default_hotkeys = {
            "uh_hotkey": "f3",
            "heal_spell_light": "f1",
            "mana_potion": "f4",
            "eat_food": "f8",
            "attack": "f5"
        }

        for key, default in default_hotkeys.items():
            row = ttk.Frame(hotkeys_frame)
            row.pack(fill='x', pady=5, padx=10)
            ttk.Label(row, text=key.replace("_", " ").title() + ":", width=20).pack(side='left')
            entry = ttk.Entry(row, width=15)
            entry.insert(0, self.config.get('hotkeys', {}).get(key, default))
            entry.pack(side='left', padx=10)
            self.hotkey_entries[key] = entry

        # Thresholds
        thresholds_frame = tk.LabelFrame(frame, text="Umbrales de Healing", font=("Arial", 16), bg="#2d2d44", fg="white")
        thresholds_frame.pack(fill='x', pady=10, padx=20)

        self.threshold_vars = {}
        thresholds = {
            "hp_threshold": ("HP para heal light", 75),
            "strong_heal_below": ("HP para UH (crítico)", 45),
            "mp_threshold": ("Mana para potion", 40),
            "eat_food_threshold": ("HP para comida", 60)
        }

        for key, (label, default) in thresholds.items():
            row = ttk.Frame(thresholds_frame)
            row.pack(fill='x', pady=8, padx=10)
            ttk.Label(row, text=label + ":", width=30).pack(side='left')
            var = tk.IntVar(value=self.config.get(key, default))
            spin = ttk.Spinbox(row, from_=1, to=100, textvariable=var, width=10)
            spin.pack(side='left')
            self.threshold_vars[key] = var

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=30)

        save_btn = tk.Button(btn_frame, text="GUARDAR CONFIG", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", command=self.save_settings)
        save_btn.pack(side='left', padx=20)

        reload_btn = tk.Button(btn_frame, text="RELOAD CONFIG", font=("Arial", 16, "bold"), bg="#FF9800", fg="white", command=self.reload_config)
        reload_btn.pack(side='left', padx=20)

    def save_settings(self):
        # Guardar hotkeys
        if 'hotkeys' not in self.config:
            self.config['hotkeys'] = {}
        for key, entry in self.hotkey_entries.items():
            self.config['hotkeys'][key] = entry.get()

        # Guardar thresholds
        for key, var in self.threshold_vars.items():
            self.config[key] = var.get()

        self.save_config()

    def reload_config(self):
        self.config = self.load_config()
        messagebox.showinfo("Reload", "Config recargada desde archivo")

    # === CALIBRAR TAB ===
    def setup_calibrate_tab(self):
        frame = ttk.Frame(self.calibrate_frame)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        title = tk.Label(frame, text="Calibración Automática por Screenshot", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        load_btn = tk.Button(frame, text="1. CARGAR SCREENSHOT DE TIBIA", font=("Arial", 14), bg="#2196F3", fg="white", command=self.load_screenshot)
        load_btn.pack(pady=15)

        self.canvas = tk.Canvas(frame, bg="#e0e0e0", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(fill='both', expand=True, pady=10)

        calib_btn = tk.Button(frame, text="2. CALIBRAR AUTOMÁTICAMENTE", font=("Arial", 16, "bold"), bg="#FF9800", fg="white", command=self.auto_calibrate)
        calib_btn.pack(pady=15)

        save_btn = tk.Button(frame, text="GUARDAR CONFIG.JSON", font=("Arial", 12), bg="#4CAF50", fg="white", command=self.save_config)
        save_btn.pack(pady=5)

        self.image_path = None
        self.original_img = None
        self.photo = None

    def load_screenshot(self):
        path = filedialog.askopenfilename(
            title="Selecciona una captura completa de Tibia",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")]
        )
        if not path:
            return

        self.image_path = path
        try:
            img = Image.open(path)
            self.original_img = cv2.imread(path)

            display_width = 900
            ratio = display_width / img.width
            display_height = int(img.height * ratio)
            img_resized = img.resize((display_width, display_height))
            self.photo = ImageTk.PhotoImage(img_resized)

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            logging.info("Screenshot cargada correctamente.")
            messagebox.showinfo("Éxito", "Screenshot cargada!\nPresiona 'CALIBRAR AUTOMÁTICAMENTE'")
        except Exception as e:
            logging.error(f"No se pudo cargar la imagen: {e}")
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def auto_calibrate(self):
        if self.original_img is None:
            messagebox.showerror("Error", "Primero carga una screenshot")
            return

        logging.info("Iniciando calibración automática...")
        img = self.original_img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        regions = {}

        # HP Bar
        hp_lower = np.array([0, 100, 100])
        hp_upper = np.array([10, 255, 255])
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hp_mask = cv2.inRange(hsv, hp_lower, hp_upper)
        hp_contours, _ = cv2.findContours(hp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if hp_contours:
            hp_box = cv2.boundingRect(max(hp_contours, key=cv2.contourArea))
            regions['hp_bar'] = list(hp_box)

        # Mana Bar
        mana_lower = np.array([100, 100, 100])
        mana_upper = np.array([130, 255, 255])
        mana_mask = cv2.inRange(hsv, mana_lower, mana_upper)
        mana_contours, _ = cv2.findContours(mana_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if mana_contours:
            mana_box = cv2.boundingRect(max(mana_contours, key=cv2.contourArea))
            regions['mana_bar'] = list(mana_box)

        # Minimap
        minimap_mask = cv2.inRange(gray, 0, 60)
        minimap_contours, _ = cv2.findContours(minimap_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        minimap_contours = [c for c in minimap_contours if 5000 < cv2.contourArea(c) < 30000]
        if minimap_contours:
            minimap_box = cv2.boundingRect(max(minimap_contours, key=cv2.contourArea))
            regions['minimap'] = list(minimap_box)

        # Coordenadas texto
        text_mask = cv2.inRange(gray, 200, 255)
        text_contours, _ = cv2.findContours(text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        text_contours = [c for c in text_contours if 300 < cv2.contourArea(c) < 3000]
        if text_contours:
            text_box = cv2.boundingRect(max(text_contours, key=cv2.contourArea))
            regions['minimap_coords_text'] = list(text_box)

        # Player dot
        white_mask = cv2.inRange(img, np.array([240, 240, 240]), np.array([255, 255, 255]))
        white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        white_contours = [c for c in white_contours if cv2.contourArea(c) < 200]
        if white_contours:
            dot = max(white_contours, key=cv2.contourArea)
            M = cv2.moments(dot)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                regions['player_dot'] = [cx, cy]

        # Battle list
        right_mask = text_mask[:, int(w * 0.75):]
        right_contours, _ = cv2.findContours(right_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if right_contours:
            right_box = cv2.boundingRect(max(right_contours, key=cv2.contourArea))
            regions['battle_list'] = [int(w * 0.75) + right_box[0], right_box[1], right_box[2], right_box[3]]

        # Corpse area
        regions['corpse_area'] = [w // 2 - 50, h // 2 - 50, 100, 100]

        # Level up
        regions['level_up_button'] = [w - 300, 200, 200, 80]

        # Guardar
        self.config['regions'] = regions
        if 'minimap' in regions:
            mm = regions['minimap']
            self.config['minimap_center_offset'] = [mm[2] // 2, mm[3] // 2]

        self.save_config()

        result = "\n".join([f"{k}: {v}" for k, v in regions.items()])
        logging.info(f"Calibración completada:\n{result}")
        messagebox.showinfo("¡Calibración completada!", f"Regiones detectadas:\n\n{result}")

    # === LOGS TAB ===
    def setup_logs_tab(self):
        frame = ttk.Frame(self.logs_frame)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        title = tk.Label(frame, text="Logs en Tiempo Real", font=("Arial", 20, "bold"), bg="#1e1e2e", fg="#00d4ff")
        title.pack(pady=10)

        self.log_text = tk.Text(frame, wrap='word', state='disabled', font=("Courier", 11), bg="black")
        self.log_text.pack(fill='both', expand=True, pady=10)

        self.log_text.tag_config("gray", foreground="gray")
        self.log_text.tag_config("lime", foreground="lime")
        self.log_text.tag_config("yellow", foreground="yellow")
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("orange", foreground="orange")

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)

        clear_btn = tk.Button(frame, text="Limpiar Logs", font=("Arial", 12), bg="#444", fg="white", command=self.clear_logs)
        clear_btn.pack(pady=10)

        handler = ColoredTextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

    # === HEALING STATUS TAB ===
    def setup_healing_tab(self):
        frame = ttk.Frame(self.healing_frame)
        frame.pack(expand=True, fill='both')

        title = tk.Label(frame, text="HEALING STATUS", font=("Arial", 36, "bold"), bg="#1e1e2e", fg="#00d4ff")
        title.pack(pady=50)

        # HP
        hp_container = tk.Frame(frame, bg="#1e1e2e")
        hp_container.pack(pady=20)
        self.hp_label = tk.Label(hp_container, text="HP: --%", font=("Arial", 32, "bold"), bg="#1e1e2e", fg="white")
        self.hp_label.pack()
        self.hp_bar = ttk.Progressbar(hp_container, orient="horizontal", length=600, mode="determinate", maximum=100)
        self.hp_bar.pack(pady=15)

        # Mana
        mana_container = tk.Frame(frame, bg="#1e1e2e")
        mana_container.pack(pady=20)
        self.mana_label = tk.Label(mana_container, text="Mana: --%", font=("Arial", 32, "bold"), bg="#1e1e2e", fg="white")
        self.mana_label.pack()
        self.mana_bar = ttk.Progressbar(mana_container, orient="horizontal", length=600, mode="determinate", maximum=100)
        self.mana_bar.pack(pady=15)
        style = ttk.Style()
        style.configure("blue.Horizontal.TProgressbar", background='blue')
        self.mana_bar.configure(style="blue.Horizontal.TProgressbar")

        # Estado
        self.status_healing_label = tk.Label(frame, text="Estado: Desconocido", font=("Arial", 40, "bold"), bg="#1e1e2e", fg="gray")
        self.status_healing_label.pack(pady=60)

        # Última acción
        self.last_action_label = tk.Label(frame, text="Última acción: Ninguna", font=("Arial", 20), bg="#1e1e2e", fg="#9b59b6")
        self.last_action_label.pack(pady=20)

        # Emergency
        emergency_btn = tk.Button(frame, text="EMERGENCY UH", font=("Arial", 28, "bold"), bg="#e74c3c", fg="white",
                                  width=30, height=3, command=self.emergency_heal)
        emergency_btn.pack(pady=60)

    def emergency_heal(self):
        uh_key = self.config['hotkeys'].get('uh_hotkey', 'f3')
        pyautogui.press(uh_key)
        logging.info(f"EMERGENCY UH manual ({uh_key})")
        self.last_action_label.config(text=f"Última acción: Emergency UH ({uh_key.upper()})", fg="red")
        self.status_healing_label.config(text="EMERGENCY ACTIVADO", fg="red")

    def update_healing_status(self, hp_percent, mana_percent, last_action=""):
        self.hp_label.config(text=f"HP: {hp_percent:.1f}%")
        self.hp_bar['value'] = hp_percent
        if hp_percent < 40:
            style = ttk.Style()
            style.configure("red.Horizontal.TProgressbar", background='red')
            self.hp_bar.configure(style="red.Horizontal.TProgressbar")
        else:
            self.hp_bar.configure(style="Horizontal.TProgressbar")

        self.mana_label.config(text=f"Mana: {mana_percent:.1f}%")
        self.mana_bar['value'] = mana_percent

        if hp_percent < 30:
            status, color = "CRÍTICO", "red"
        elif hp_percent < 60:
            status, color = "PELIGRO", "orange"
        else:
            status, color = "SEGURO", "lime"

        self.status_healing_label.config(text=f"Estado: {status}", fg=color)

        if last_action:
            self.last_action_label.config(text=f"Última acción: {last_action}", fg="#9b59b6")

    def auto_load_and_calibrate(self):
        screenshots_dir = os.path.join(project_root, 'screenshots')
        default_screenshot = os.path.join(screenshots_dir, 'tibia_screenshot.png')

        # Solo calibrar automática si config.json no tiene calibración manual
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                if existing.get('regions', {}).get('player_dot'):
                    logging.info("Config.json ya tiene calibración manual. No se sobrescribe.")
                    return
            except:
                pass

        if os.path.exists(default_screenshot):
            logging.info(f"Calibración automática desde: {default_screenshot}")
            self.image_path = default_screenshot
            try:
                img = Image.open(default_screenshot)
                self.original_img = cv2.imread(default_screenshot)

                display_width = 900
                ratio = display_width / img.width
                display_height = int(img.height * ratio)
                img_resized = img.resize((display_width, display_height))
                self.photo = ImageTk.PhotoImage(img_resized)

                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

                self.auto_calibrate()
            except Exception as e:
                logging.error(f"Error al cargar imagen automática: {e}")
        else:
            logging.info("No se encontró tibia_screenshot.png en screenshots/. Calibración manual disponible.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TibiabotGUI(root)
    root.mainloop()