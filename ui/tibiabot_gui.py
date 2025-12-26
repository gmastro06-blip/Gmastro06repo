# Ruta: ui/tibiabot_gui.py - Versión FINAL CORREGIDA y OPTIMIZADA al 100%

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

# Importar motor del bot
try:
    from bot_engine import run_bot
except ImportError as e:
    logging.error(f"No se pudo importar bot_engine.py: {e}")
    def run_bot():
        logging.info("Bot no disponible.")
        messagebox.showwarning("Advertencia", "bot_engine.py no encontrado.")

# Logging
logs_dir = os.path.join(project_root, 'logs')
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, 'bot_log.txt')
open(log_file, 'w').close()

logging.basicConfig(level=logging.INFO, format='[%(H:%M:%S] %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

class ColoredTextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.tags = {
            logging.INFO: "lime",
            logging.WARNING: "yellow",
            logging.ERROR: "red",
            logging.DEBUG: "gray"
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
        self.root.geometry("1300x850")
        self.root.configure(bg="#1e1e2e")
        self.root.state('zoomed')

        self.bot_running = False
        self.bot_thread = None

        self.config_path = os.path.join(project_root, 'config.json')
        self.config = self._load_config()

        self.waypoints_file = self.config.get('waypoints_file', 'waypoints/newhaven_exp.json')

        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#1e1e2e")
        style.configure("TNotebook.Tab", background="#2d2d44", foreground="white", padding=[15, 8])
        style.map("TNotebook.Tab", background=[("selected", "#3a3a5a")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)

        # Pestañas
        self.control_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        self.calibrate_frame = ttk.Frame(self.notebook)
        self.logs_frame = ttk.Frame(self.notebook)
        self.healing_frame = ttk.Frame(self.notebook)
        self.waypoints_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.control_frame, text="Control")
        self.notebook.add(self.settings_frame, text="Settings")
        self.notebook.add(self.calibrate_frame, text="Calibrar")
        self.notebook.add(self.logs_frame, text="Logs")
        self.notebook.add(self.healing_frame, text="Healing Status")
        self.notebook.add(self.waypoints_frame, text="Waypoints")

        # Setup pestañas
        self._setup_control_tab()
        self._setup_settings_tab()
        self._setup_calibrate_tab()
        self._setup_logs_tab()
        self._setup_healing_tab()
        self._setup_waypoints_tab()

        logging.info("=== TIBIABOT PRO GUI INICIADO ===")
        logging.info("Interfaz gráfica cargada correctamente.")

        self._auto_load_and_calibrate()

    def _load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando config.json: {e}")
        return {"regions": {}, "hotkeys": {}, "base_position": {"x": 32560, "y": 32488, "z": 7}}

    def _save_config(self):
        try:
            backup = self.config_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.config_path):
                shutil.copy(self.config_path, backup)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            logging.info("Configuración guardada")
            messagebox.showinfo("Guardado", "Configuración guardada correctamente")
        except Exception as e:
            logging.error(f"Error guardando config: {e}")
            messagebox.showerror("Error", "No se pudo guardar")

    # === CONTROL ===
    def _setup_control_tab(self):
        f = ttk.Frame(self.control_frame)
        f.pack(expand=True)

        tk.Label(f, text="TIBIABOT v2.1 PRO", font=("Arial", 42, "bold"), bg="#1e1e2e", fg="#00d4ff").pack(pady=60)
        tk.Label(f, text="Grok Edition - Newhaven Hunt 🎄", font=("Arial", 18), bg="#1e1e2e", fg="#a0a0ff").pack(pady=10)

        btn_f = ttk.Frame(f)
        btn_f.pack(pady=60)

        self.start_button = tk.Button(btn_f, text="START BOT", font=("Arial", 24, "bold"), bg="#27ae60", fg="white",
                                      width=25, height=3, command=self.start_bot)
        self.start_button.pack(pady=30)

        self.stop_button = tk.Button(btn_f, text="STOP BOT", font=("Arial", 24, "bold"), bg="#c0392b", fg="white",
                                     width=25, height=3, command=self.stop_bot, state="disabled")
        self.stop_button.pack(pady=20)

        self.status_label = tk.Label(f, text="Estado: Detenido", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="#e74c3c")
        self.status_label.pack(pady=50)

    def start_bot(self):
        if self.bot_running:
            return
        logging.info("=== BOT INICIADO ===")
        self.bot_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="Estado: Ejecutándose", fg="#27ae60")
        def thread_target():
            try:
                run_bot()
            except Exception as e:
                logging.error(f"Error en hilo del bot: {e}")
            finally:
                self.root.after(0, self._bot_finished)

        self.bot_thread = threading.Thread(target=thread_target, daemon=True)
        self.bot_thread.start()

    def stop_bot(self):
        logging.info("=== BOT DETENIDO POR USUARIO ===")
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Estado: Detenido", fg="#e74c3c")

    def _bot_finished(self):
        self.bot_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="Estado: Detenido", fg="#e74c3c")
        logging.info("Hilo del bot terminado. Botón START reactivado.")

    # === SETTINGS ===
    def _setup_settings_tab(self):
        f = ttk.Frame(self.settings_frame)
        f.pack(fill='both', expand=True, padx=30, pady=30)

        tk.Label(f, text="PERSONALIZACIÓN", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="#00d4ff").pack(pady=20)

        # Hotkeys
        hotkeys_f = tk.LabelFrame(f, text="Hotkeys", font=("Arial", 16), bg="#2d2d44", fg="white")
        hotkeys_f.pack(fill='x', pady=10, padx=20)

        self.hotkey_entries = {}
        defaults = {"uh_hotkey": "f3", "heal_spell_light": "f1", "mana_potion": "f4", "eat_food": "f8", "attack": "f5"}

        for key, default in defaults.items():
            row = ttk.Frame(hotkeys_f)
            row.pack(fill='x', pady=5, padx=10)
            ttk.Label(row, text=key.replace("_", " ").title() + ":", width=20).pack(side='left')
            entry = ttk.Entry(row, width=15)
            entry.insert(0, self.config.get('hotkeys', {}).get(key, default))
            entry.pack(side='left', padx=10)
            self.hotkey_entries[key] = entry

        # Thresholds
        thresholds_f = tk.LabelFrame(f, text="Umbrales de Healing", font=("Arial", 16), bg="#2d2d44", fg="white")
        thresholds_f.pack(fill='x', pady=10, padx=20)

        self.threshold_vars = {}
        thresholds = {
            "hp_threshold": ("HP para heal light", 75),
            "strong_heal_below": ("HP para UH", 45),
            "mp_threshold": ("Mana para potion", 40),
            "eat_food_threshold": ("HP para comida", 60)
        }

        for key, (label, default) in thresholds.items():
            row = ttk.Frame(thresholds_f)
            row.pack(fill='x', pady=8, padx=10)
            ttk.Label(row, text=label + ":", width=30).pack(side='left')
            var = tk.IntVar(value=self.config.get(key, default))
            ttk.Spinbox(row, from_=1, to=100, textvariable=var, width=10).pack(side='left')
            self.threshold_vars[key] = var

        # Botones
        btn_f = ttk.Frame(f)
        btn_f.pack(pady=30)
        tk.Button(btn_f, text="GUARDAR CONFIG", font=("Arial", 16, "bold"), bg="#4CAF50", fg="white", command=self._save_settings).pack(side='left', padx=20)
        tk.Button(btn_f, text="RELOAD CONFIG", font=("Arial", 16, "bold"), bg="#FF9800", fg="white", command=self._reload_config).pack(side='left', padx=20)

    def _save_settings(self):
        if 'hotkeys' not in self.config:
            self.config['hotkeys'] = {}
        for key, entry in self.hotkey_entries.items():
            self.config['hotkeys'][key] = entry.get()
        for key, var in self.threshold_vars.items():
            self.config[key] = var.get()
        self._save_config()

    def _reload_config(self):
        self.config = self._load_config()
        messagebox.showinfo("Reload", "Config recargada")

    # === CALIBRAR ===
    def _setup_calibrate_tab(self):
        f = ttk.Frame(self.calibrate_frame)
        f.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(f, text="Calibración Automática por Screenshot", font=("Arial", 18, "bold")).pack(pady=10)

        tk.Button(f, text="1. CARGAR SCREENSHOT DE TIBIA", font=("Arial", 14), bg="#2196F3", fg="white", command=self._load_screenshot).pack(pady=15)

        self.canvas = tk.Canvas(f, bg="#e0e0e0", highlightthickness=1, highlightbackground="black")
        self.canvas.pack(fill='both', expand=True, pady=10)

        tk.Button(f, text="2. CALIBRAR AUTOMÁTICAMENTE", font=("Arial", 16, "bold"), bg="#FF9800", fg="white", command=self._auto_calibrate).pack(pady=15)
        tk.Button(f, text="GUARDAR CONFIG.JSON", font=("Arial", 12), bg="#4CAF50", fg="white", command=self._save_config).pack(pady=5)

        self.image_path = None
        self.original_img = None
        self.photo = None

    def _load_screenshot(self):
        path = filedialog.askopenfilename(title="Selecciona captura de Tibia", filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp")])
        if not path:
            return

        self.image_path = path
        try:
            img = Image.open(path)
            self.original_img = cv2.imread(path)

            ratio = 900 / img.width
            resized = img.resize((900, int(img.height * ratio)))
            self.photo = ImageTk.PhotoImage(resized)

            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
            logging.info("Screenshot cargada")
            messagebox.showinfo("Éxito", "Screenshot cargada! Pulsa 'CALIBRAR AUTOMÁTICAMENTE'")
        except Exception as e:
            logging.error(f"Error cargando imagen: {e}")
            messagebox.showerror("Error", "No se pudo cargar la imagen")

    def _auto_calibrate(self):
        if self.original_img is None:
            messagebox.showerror("Error", "Primero carga una screenshot")
            return

        logging.info("Iniciando calibración automática...")
        img = self.original_img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        regions = {}

        # HP Bar
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hp_mask = cv2.inRange(hsv, np.array([0, 100, 100]), np.array([10, 255, 255]))
        contours = cv2.findContours(hp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if contours:
            regions['hp_bar'] = list(cv2.boundingRect(max(contours, key=cv2.contourArea)))

        # Mana Bar
        mana_mask = cv2.inRange(hsv, np.array([100, 100, 100]), np.array([130, 255, 255]))
        contours = cv2.findContours(mana_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if contours:
            regions['mana_bar'] = list(cv2.boundingRect(max(contours, key=cv2.contourArea)))

        # Minimap
        minimap_mask = cv2.inRange(gray, 0, 60)
        contours = cv2.findContours(minimap_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = [c for c in contours if 5000 < cv2.contourArea(c) < 30000]
        if contours:
            regions['minimap'] = list(cv2.boundingRect(max(contours, key=cv2.contourArea)))

        # Player dot
        white_mask = cv2.inRange(img, np.array([240, 240, 240]), np.array([255, 255, 255]))
        contours = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = [c for c in contours if cv2.contourArea(c) < 200]
        if contours:
            dot = max(contours, key=cv2.contourArea)
            M = cv2.moments(dot)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                regions['player_dot'] = [cx, cy]

        # Battle list
        text_mask = cv2.inRange(gray, 200, 255)
        right_mask = text_mask[:, int(w * 0.75):]
        contours = cv2.findContours(right_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if contours:
            box = cv2.boundingRect(max(contours, key=cv2.contourArea))
            regions['battle_list'] = [int(w * 0.75) + box[0], box[1], box[2], box[3]]

        # Corpse y level up
        regions['corpse_area'] = [w // 2 - 50, h // 2 - 50, 100, 100]
        regions['level_up_button'] = [w - 300, 200, 200, 80]

        # Guardar
        self.config['regions'] = regions
        if 'minimap' in regions:
            m = regions['minimap']
            self.config['minimap_center_offset'] = [m[2] // 2, m[3] // 2]

        self._save_config()

        result = "\n".join([f"{k}: {v}" for k, v in regions.items()])
        logging.info(f"Calibración completada:\n{result}")
        messagebox.showinfo("Calibración completada", f"Regiones detectadas:\n\n{result}")

    # === LOGS ===
    def _setup_logs_tab(self):
        f = ttk.Frame(self.logs_frame)
        f.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(f, text="Logs en Tiempo Real", font=("Arial", 20, "bold"), bg="#1e1e2e", fg="#00d4ff").pack(pady=10)

        self.log_text = tk.Text(f, wrap='word', state='disabled', font=("Courier", 11), bg="black")
        self.log_text.pack(fill='both', expand=True, pady=10)

        self.log_text.tag_config("lime", foreground="lime")
        self.log_text.tag_config("yellow", foreground="yellow")
        self.log_text.tag_config("red", foreground="red")
        self.log_text.tag_config("gray", foreground="gray")

        scrollbar = ttk.Scrollbar(f, orient='vertical', command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)

        tk.Button(f, text="Limpiar Logs", font=("Arial", 12), bg="#444", fg="white", command=self._clear_logs).pack(pady=10)

        handler = ColoredTextHandler(self.log_text)
        handler.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def _clear_logs(self):
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')

    # === HEALING STATUS ===
    def _setup_healing_tab(self):
        f = ttk.Frame(self.healing_frame)
        f.pack(expand=True, fill='both')

        tk.Label(f, text="HEALING STATUS", font=("Arial", 36, "bold"), bg="#1e1e2e", fg="#00d4ff").pack(pady=50)

        # HP
        hp_f = tk.Frame(f, bg="#1e1e2e")
        hp_f.pack(pady=20)
        self.hp_label = tk.Label(hp_f, text="HP: --%", font=("Arial", 32, "bold"), bg="#1e1e2e", fg="white")
        self.hp_label.pack()
        self.hp_bar = ttk.Progressbar(hp_f, length=600, maximum=100)
        self.hp_bar.pack(pady=15)

        # Mana
        mana_f = tk.Frame(f, bg="#1e1e2e")
        mana_f.pack(pady=20)
        self.mana_label = tk.Label(mana_f, text="Mana: --%", font=("Arial", 32, "bold"), bg="#1e1e2e", fg="white")
        self.mana_label.pack()
        self.mana_bar = ttk.Progressbar(mana_f, length=600, maximum=100)
        self.mana_bar.pack(pady=15)
        style = ttk.Style()
        style.configure("blue.Horizontal.TProgressbar", background='blue')
        self.mana_bar.configure(style="blue.Horizontal.TProgressbar")

        self.status_healing_label = tk.Label(f, text="Estado: Desconocido", font=("Arial", 40, "bold"), bg="#1e1e2e", fg="gray")
        self.status_healing_label.pack(pady=60)

        self.last_action_label = tk.Label(f, text="Última acción: Ninguna", font=("Arial", 20), bg="#1e1e2e", fg="#9b59b6")
        self.last_action_label.pack(pady=20)

        tk.Button(f, text="EMERGENCY UH", font=("Arial", 28, "bold"), bg="#e74c3c", fg="white", width=30, height=3, command=self._emergency_heal).pack(pady=60)

    def _emergency_heal(self):
        key = self.config['hotkeys'].get('uh_hotkey', 'f3')
        pyautogui.press(key)
        logging.info(f"EMERGENCY UH ({key})")
        self.last_action_label.config(text=f"Última acción: Emergency UH ({key.upper()})", fg="red")
        self.status_healing_label.config(text="EMERGENCY ACTIVADO", fg="red")

    def update_healing_status(self, hp, mana, action=""):
        self.hp_label.config(text=f"HP: {hp:.1f}%")
        self.hp_bar['value'] = hp
        self.hp_bar.configure(style="red.Horizontal.TProgressbar" if hp < 40 else "Horizontal.TProgressbar")

        self.mana_label.config(text=f"Mana: {mana:.1f}%")
        self.mana_bar['value'] = mana

        status, color = ("CRÍTICO", "red") if hp < 30 else ("PELIGRO", "orange") if hp < 60 else ("SEGURO", "lime")
        self.status_healing_label.config(text=f"Estado: {status}", fg=color)

        if action:
            self.last_action_label.config(text=f"Última acción: {action}", fg="#9b59b6")

    # === WAYPOINTS ===
    def _setup_waypoints_tab(self):
        f = ttk.Frame(self.waypoints_frame)
        f.pack(fill='both', expand=True, padx=30, pady=30)

        tk.Label(f, text="WAYPOINTS PERSONALIZADOS - Newhaven Hunt", font=("Arial", 28, "bold"), bg="#1e1e2e", fg="#00d4ff").pack(pady=20)

        tk.Button(f, text="AÑADIR POSICIÓN ACTUAL", font=("Arial", 16, "bold"), bg="#9b59b6", fg="white", command=self._add_current_position).pack(pady=10)

        input_f = tk.LabelFrame(f, text="Añadir Manualmente", font=("Arial", 16), bg="#2d2d44", fg="white")
        input_f.pack(fill='x', pady=10, padx=20)

        coord_f = ttk.Frame(input_f)
        coord_f.pack(pady=10)

        ttk.Label(coord_f, text="X:").grid(row=0, column=0, padx=5)
        self.x_entry = ttk.Entry(coord_f, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)

        ttk.Label(coord_f, text="Y:").grid(row=0, column=2, padx=5)
        self.y_entry = ttk.Entry(coord_f, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)

        tk.Button(input_f, text="AÑADIR MANUAL", font=("Arial", 14, "bold"), bg="#27ae60", fg="white", command=self._add_manual_waypoint).pack(pady=10)

        list_f = tk.LabelFrame(f, text="Waypoints Actuales", font=("Arial", 16), bg="#2d2d44", fg="white")
        list_f.pack(fill='both', expand=True, pady=10, padx=20)

        self.waypoints_listbox = tk.Listbox(list_f, font=("Courier", 12), bg="#1e1e2e", fg="lime", selectbackground="#3a3a5a")
        self.waypoints_listbox.pack(fill='both', expand=True, padx=10, pady=10)

        btn_row = ttk.Frame(list_f)
        btn_row.pack(pady=5)
        tk.Button(btn_row, text="ELIMINAR", bg="#c0392b", fg="white", command=self._delete_waypoint).pack(side='left', padx=10)
        tk.Button(btn_row, text="GUARDAR", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=self._save_waypoints).pack(side='left', padx=10)

        self._load_current_waypoints()

    def _load_current_waypoints(self):
        self.waypoints_listbox.delete(0, tk.END)
        try:
            with open(self.waypoints_file, 'r', encoding='utf-8') as f:
                wps = json.load(f)
            for wp in wps:
                self.waypoints_listbox.insert(tk.END, str(wp))
            logging.info(f"Waypoints cargados en UI: {len(wps)}")
        except Exception as e:
            logging.error(f"Error cargando waypoints: {e}")

    def _add_current_position(self):
        dot = self.config['regions'].get('player_dot')
        if not dot:
            messagebox.showerror("Error", "Calibra player_dot primero")
            return

        m = self.config['regions']['minimap']
        off = self.config.get('minimap_center_offset', [m[2]//2, m[3]//2])
        base_x = self.config['base_position']['x']
        base_y = self.config['base_position']['y']

        x = base_x + (dot[0] - (m[0] + off[0]))
        y = base_y + (dot[1] - (m[1] + off[1]))

        wp = [int(x), int(y)]
        self.waypoints_listbox.insert(tk.END, str(wp))
        logging.info(f"Posición actual añadida: {wp}")
        messagebox.showinfo("Éxito", f"Waypoint añadido: {wp}")

    def _add_manual_waypoint(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            wp = [x, y]
            self.waypoints_listbox.insert(tk.END, str(wp))
            self.x_entry.delete(0, tk.END)
            self.y_entry.delete(0, tk.END)
            logging.info(f"Waypoint manual: {wp}")
        except ValueError:
            messagebox.showerror("Error", "X e Y deben ser números")

    def _delete_waypoint(self):
        sel = self.waypoints_listbox.curselection()
        if sel:
            self.waypoints_listbox.delete(sel[0])

    def _save_waypoints(self):
        wps = []
        for i in range(self.waypoints_listbox.size()):
            line = self.waypoints_listbox.get(i).strip('[] ')
            parts = [p.strip() for p in line.split(',')]
            wps.append([int(parts[0]), int(parts[1])])

        try:
            os.makedirs(os.path.dirname(self.waypoints_file), exist_ok=True)
            with open(self.waypoints_file, 'w', encoding='utf-8') as f:
                json.dump(wps, f, indent=4)
            logging.info(f"Waypoints guardados: {len(wps)} puntos")
            messagebox.showinfo("Guardado", f"Waypoints guardados en {os.path.basename(self.waypoints_file)}")
        except Exception as e:
            logging.error(f"Error guardando waypoints: {e}")
            messagebox.showerror("Error", "No se pudo guardar")

    def _auto_load_and_calibrate(self):
        screenshots_dir = os.path.join(project_root, 'screenshots')
        screenshot_path = os.path.join(screenshots_dir, 'tibia_screenshot.png')

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    cfg = json.load(f)
                if cfg.get('regions', {}).get('player_dot'):
                    logging.info("Calibración manual detectada. No se sobrescribe.")
                    return
            except:
                pass

        if os.path.exists(screenshot_path):
            logging.info(f"Calibración automática desde screenshot")
            self.image_path = screenshot_path
            try:
                img = Image.open(screenshot_path)
                self.original_img = cv2.imread(screenshot_path)
                ratio = 900 / img.width
                resized = img.resize((900, int(img.height * ratio)))
                self.photo = ImageTk.PhotoImage(resized)
                self.canvas.delete("all")
                self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
                self._auto_calibrate()
            except Exception as e:
                logging.error(f"Error en calibración automática: {e}")
        else:
            logging.info("No hay screenshot para calibración automática. Usa manual.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TibiabotGUI(root)
    root.mainloop()