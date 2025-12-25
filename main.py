# main.py
import os
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from modules.healer import Healer
from modules.targeting import Targeting
from modules.cavebot import Cavebot
from modules.macros import Macros
from modules.level_up import LevelUp
from modules.npc_talker import NPCTalker
from modules.game_window import getGameWindowPositionAndSize
from modules.utils import CONFIG, logger
from modules.looter import Looter
from modules.utils import CONFIG, logger, capture_screen

if not os.path.exists('config.json'):
    messagebox.showerror("Error", "Falta config.json")
    exit()

class TibiaBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TibiaBot v2.1 - Pro Edition")
        self.root.geometry("520x720")
        self.root.configure(bg="#2c3e50")
        self.root.resizable(False, False)
        self.looter = Looter()

        self.bot_running = False
        self.main_loop_thread = None

        # Módulos
        self.cavebot = Cavebot()
        self.healer = Healer()
        self.targeting = Targeting()
        self.macros = Macros()
        self.level_up = LevelUp()
        self.npc_talker = NPCTalker()

        self.threaded_modules = [self.healer, self.targeting, self.cavebot]

        self.setup_ui()
        logger.info("[Main] Interfaz cargada - Bot Pro Edition listo")

    def setup_ui(self):
        title = tk.Label(self.root, text="TIBIABOT v2.1", font=("Arial", 24, "bold"), fg="#ecf0f1", bg="#2c3e50")
        title.pack(pady=20)

        subtitle = tk.Label(self.root, text="Pro Pixel Bot - Navidad 2025\nDetección avanzada con flechas!",
                            font=("Arial", 10), fg="#bdc3c7", bg="#2c3e50")
        subtitle.pack(pady=10)

        btn_frame = tk.Frame(self.root, bg="#2c3e50")
        btn_frame.pack(pady=30)

        self.start_btn = tk.Button(btn_frame, text="INICIAR BOT", font=("Arial", 14, "bold"),
                                   bg="#27ae60", fg="white", width=20, height=2, command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=20)

        self.stop_btn = tk.Button(btn_frame, text="DETENER BOT", font=("Arial", 14, "bold"),
                                  bg="#c0392b", fg="white", width=20, height=2, command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=20)

        self.status_label = tk.Label(self.root, text="Estado: DETENIDO", font=("Arial", 12, "bold"),
                                     fg="#e74c3c", bg="#2c3e50")
        self.status_label.pack(pady=20)

        modules_frame = tk.LabelFrame(self.root, text=" Módulos ", font=("Arial", 10, "bold"),
                                      fg="#ecf0f1", bg="#34495e", padx=10, pady=10)
        modules_frame.pack(pady=20, padx=40, fill="x")

        self.module_labels = {
            "Healer": tk.Label(modules_frame, text="● Healer: Detenido", fg="#e74c3c", bg="#34495e"),
            "Targeting": tk.Label(modules_frame, text="● Targeting: Detenido", fg="#e74c3c", bg="#34495e"),
            "Cavebot": tk.Label(modules_frame, text="● Cavebot: Detenido", fg="#e74c3c", bg="#34495e"),
            "Macros": tk.Label(modules_frame, text="● Macros: Listo", fg="#f1c40f", bg="#34495e"),
            "LevelUp": tk.Label(modules_frame, text="● LevelUp: Listo", fg="#f1c40f", bg="#34495e"),
            "Talker": tk.Label(modules_frame, text="● NPCTalker: Listo", fg="#f1c40f", bg="#34495e")
        }
        for label in self.module_labels.values():
            label.pack(anchor="w", pady=3)

        warning = tk.Label(self.root, text="⚠️ Uso solo en OTS permitidos\nNo usar en Tibia oficial - Riesgo de ban",
                           font=("Arial", 9), fg="#e67e22", bg="#2c3e50", justify="center")
        warning.pack(pady=20)

        credit = tk.Label(self.root, text="Hecho con ❤️ para la mejor Navidad 2025", font=("Arial", 8), fg="#95a5a6", bg="#2c3e50")
        credit.pack(side=tk.BOTTOM, pady=15)

    def update_status(self, module, state):
        color = "#27ae60" if state == "running" else "#e74c3c"
        text = f"● {module}: {'Ejecutándose' if state == 'running' else 'Detenido'}"
        self.module_labels[module].config(text=text, fg=color)

    def start_bot(self):
        if self.bot_running:
            return
        self.bot_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Estado: EJECUTÁNDOSE", fg="#27ae60")

        for module in self.threaded_modules:
            module.start()
            self.update_status(module.__class__.__name__, "running")

        self.main_loop_thread = threading.Thread(target=self.main_loop, daemon=True)
        self.main_loop_thread.start()

        messagebox.showinfo("¡Bot Activado!", "TibiaBot v2.1 Pro Edition está listo para Newhaven.\n¡Feliz Navidad!")

    def stop_bot(self):
        if not self.bot_running:
            return
        self.bot_running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Estado: DETENIDO", fg="#e74c3c")

        for module in self.threaded_modules:
            module.stop()
            self.update_status(module.__class__.__name__, "stopped")

        messagebox.showinfo("Bot Detenido", "Módulos detenidos de forma segura.")

    def main_loop(self):
        logger.info("[Main] Bucle principal iniciado")
        while self.bot_running:
            try:
                screen_full = capture_screen()
                game_window = getGameWindowPositionAndSize(screen_full)
                screen = capture_screen(region=game_window) if game_window else screen_full
                self.macros.run_safety_checks(screen)
                self.level_up.run_check(screen)
                self.looter.open_and_loot(screen)

                time.sleep(0.5)
            except Exception as e:
                logger.error(f"[Main Loop] Error: {e}")
                time.sleep(2)

if __name__ == "__main__":
    logger.info("="*70)
    logger.info("TIBIABOT v2.1 - Pro Edition - Navidad 2025")
    logger.info("Detección avanzada con flechas - ¡El mejor bot personal!")
    logger.info("="*70)

    root = tk.Tk()
    app = TibiaBotGUI(root)
    root.mainloop()