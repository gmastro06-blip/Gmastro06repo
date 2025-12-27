# bot_engine.py - Motor Principal del Tibiabot PRO

import logging
import time
import random
import keyboard
import pyautogui
import json
import threading
import numpy as np
import os  # ← AÑADIDO: necesario para rutas y carpetas
from typing import Optional, Dict
from modules.utils import GameWindow
from modules.cavebot import Cavebot
from modules.targeting import Targeting
from modules.looter import Looter
from modules.healer import Healer
from modules.level_up import LevelUp
from modules.refill import Refill

# Crear carpeta logs si no existe
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'bot_engine.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class TibiabotEngine:
    def __init__(self):
        self.config: Optional[Dict] = self._load_and_validate_config()
        if not self.config:
            raise ValueError("Configuración inválida. Ejecuta calibrate.py.")

        self.game_window: GameWindow = GameWindow(self.config)

        self.stop_event: threading.Event = threading.Event()

        self.cavebot: Cavebot = Cavebot(self.game_window, self.config, self.stop_event)
        self.targeting: Targeting = Targeting(self.game_window, self.config)
        self.looter: Looter = Looter(self.game_window, self.config)
        self.healer: Healer = Healer(self.game_window, self.config)
        self.level_up: LevelUp = LevelUp(self.game_window, self.config)
        self.refill: Refill = Refill(self.game_window, self.config)

        self.running: bool = False
        self.healer_thread: Optional[threading.Thread] = None
        self.targeting_thread: Optional[threading.Thread] = None

        logging.info("=== TIBIABOT ENGINE INICIALIZADO PROFESIONALMENTE ===")

    def _load_and_validate_config(self) -> Optional[Dict]:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            required_keys = ['regions', 'hotkeys', 'base_position']
            for key in required_keys:
                if key not in config:
                    raise KeyError(f"Falta clave requerida: {key}")
            logging.info("Config.json cargado y validado correctamente")
            return config
        except Exception as e:
            logging.error(f"Error cargando/validando config.json: {e}")
            return None

    def _human_delay(self, min_sec: float = 0.3, max_sec: float = 1.0) -> None:
        if self.stop_event.is_set():
            return
        time.sleep(random.uniform(min_sec, max_sec))

    def _random_mouse_move(self) -> None:
        if self.stop_event.is_set():
            return
        if random.random() < 0.25:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + random.randint(-80, 80), y + random.randint(-80, 80), duration=random.uniform(0.2, 0.5))
            self._human_delay(0.1, 0.3)
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.4))

    def _random_break(self) -> None:
        if self.stop_event.is_set():
            return
        if random.random() < 0.08:
            delay = random.uniform(3, 10)
            logging.info(f"Anti-ban: Pausa natural de {delay:.1f}s")
            time.sleep(delay)

    def _healer_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                self.healer.monitor()
                time.sleep(random.uniform(0.25, 0.5))
            except Exception as e:
                logging.debug(f"Healer loop error: {e}")
                time.sleep(0.5)

    def _targeting_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                if self.targeting.detect():
                    while self.targeting.is_enemy_present() and not self.stop_event.is_set():
                        self.targeting.attack_target()
                        time.sleep(0.3)
                    if not self.stop_event.is_set():
                        self.looter.loot(after_kill=True)
                        time.sleep(self.config.get('loot_delay', 1.5))
                time.sleep(0.2)
            except Exception as e:
                logging.debug(f"Targeting loop error: {e}")
                time.sleep(0.5)

    def run(self) -> None:
        if self.running:
            return

        logging.info("=== INICIANDO TIBIABOT v2.1 PRO - Modo anti-ban ===")
        logging.info("Presiona ESC o STOP en GUI para detener")

        self.running = True
        self.stop_event.clear()

        self.healer_thread = threading.Thread(target=self._healer_loop, daemon=True)
        self.targeting_thread = threading.Thread(target=self._targeting_loop, daemon=True)

        self.healer_thread.start()
        self.targeting_thread.start()

        cycle: int = 0
        try:
            while self.running and not self.stop_event.is_set():
                if keyboard.is_pressed('esc'):
                    logging.info("ESC presionado -> Deteniendo bot")
                    self.stop()
                    break

                cycle += 1

                self._random_mouse_move()
                if self.stop_event.is_set():
                    break

                if cycle % 12 == 0:
                    self._random_break()
                    if self.stop_event.is_set():
                        break

                self.cavebot.process_waypoints()
                if self.stop_event.is_set():
                    break
                self._human_delay(0.3, 0.8)
                if self.stop_event.is_set():
                    break

                self.level_up.check()
                if self.stop_event.is_set():
                    break
                self._human_delay(0.1, 0.3)
                if self.stop_event.is_set():
                    break

                if cycle % 600 == 0:
                    self.refill.refill_if_low()
                    if self.stop_event.is_set():
                        break

                time.sleep(random.uniform(0.3, 0.8))
                if self.stop_event.is_set():
                    break

        except Exception as e:
            logging.error(f"Error crítico en bucle principal: {e}")
        finally:
            self.stop()
            logging.info("=== BOT DETENIDO SEGURAMENTE ===")

    def stop(self) -> None:
        self.running = False
        self.stop_event.set()

        if self.healer_thread and self.healer_thread.is_alive():
            self.healer_thread.join(timeout=5.0)
        if self.targeting_thread and self.targeting_thread.is_alive():
            self.targeting_thread.join(timeout=5.0)

def run_bot():
    engine = TibiabotEngine()
    engine.run()

if __name__ == "__main__":
    run_bot()