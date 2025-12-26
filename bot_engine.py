# Ruta: bot_engine.py - Motor del bot OPTIMIZADO al 100% (threading, anti-ban, modular)

import logging
import time
import random
import keyboard
import pyautogui
import json
import threading
import numpy as np  
from modules.utils import GameWindow
from modules.cavebot import Cavebot
from modules.targeting import Targeting
from modules.looter import Looter
from modules.healer import Healer
from modules.level_up import LevelUp
from modules.refill import Refill

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class TibiabotEngine:
    def __init__(self):
        self.config = self._load_config()
        if not self.config:
            return

        self.game_window = GameWindow(self.config)

        # Módulos principales
        self.cavebot = Cavebot(self.game_window, self.config)
        self.targeting = Targeting(self.game_window, self.config)
        self.looter = Looter(self.game_window, self.config)
        self.healer = Healer(self.game_window, self.config)
        self.level_up = LevelUp(self.game_window, self.config)
        self.refill = Refill(self.game_window, self.config)

        # ← AÑADIDO: Inicializa stop_event aquí
        self.stop_event = threading.Event()

        # Control de ejecución
        self.running = False

        # Hilos paralelos
        self.healer_thread = None
        self.targeting_thread = None

        logging.info("=== TIBIABOT ENGINE INICIALIZADO ===")

    def _load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            logging.info("Config.json cargado correctamente")
            return config
        except Exception as e:
            logging.error(f"Error cargando config.json: {e}")
            return None

    def _human_delay(self, min_sec=0.3, max_sec=1.0):
        time.sleep(random.uniform(min_sec, max_sec))

    def _random_mouse_move(self):
        if random.random() < 0.25:
            x, y = pyautogui.position()
            pyautogui.moveTo(
                x + random.randint(-80, 80),
                y + random.randint(-80, 80),
                duration=random.uniform(0.2, 0.5)
            )
            self._human_delay(0.1, 0.3)
            pyautogui.moveTo(x, y, duration=random.uniform(0.2, 0.4))

    def _random_break(self):
        if random.random() < 0.08:
            delay = random.uniform(3, 10)
            logging.info(f"Anti-ban: Pausa natural de {delay:.1f}s")
            time.sleep(delay)

    def _healer_loop(self):
        while not self.stop_event.is_set():
            try:
                self.healer.monitor()
                time.sleep(random.uniform(0.25, 0.5))
            except Exception as e:
                logging.debug(f"Healer loop error: {e}")
                time.sleep(0.5)

    def _targeting_loop(self):
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

    def run(self):
        if self.running:
            return

        logging.info("=== INICIANDO TIBIABOT v2.1 - Modo anti-ban PRO ===")
        logging.info("Presiona ESC o STOP en GUI para detener")

        self.running = True
        self.stop_event.clear()

        self.healer_thread = threading.Thread(target=self._healer_loop, daemon=True)
        self.targeting_thread = threading.Thread(target=self._targeting_loop, daemon=True)

        self.healer_thread.start()
        self.targeting_thread.start()

        cycle = 0
        try:
            while self.running and not self.stop_event.is_set():
                if keyboard.is_pressed('esc'):
                    logging.info("ESC presionado → Deteniendo bot")
                    break

                cycle += 1

                self._random_mouse_move()
                if cycle % 12 == 0:
                    self._random_break()

                self.cavebot.navigate()
                self._human_delay(0.3, 0.8)

                self.level_up.check()
                self._human_delay(0.1, 0.3)

                if cycle % 600 == 0:
                    self.refill.refill_if_low()

                time.sleep(random.uniform(0.3, 0.8))

        except Exception as e:
            logging.error(f"Error crítico en bucle principal: {e}")
        finally:
            self.stop()
            logging.info("=== BOT DETENIDO SEGURAMENTE ===")

    def stop(self):
        self.running = False
        self.stop_event.set()

        if self.healer_thread and self.healer_thread.is_alive():
            self.healer_thread.join(timeout=1)
        if self.targeting_thread and self.targeting_thread.is_alive():
            self.targeting_thread.join(timeout=1)

# === FUNCIÓN GLOBAL PARA LA GUI ===
def run_bot():
    engine = TibiabotEngine()
    engine.run()

if __name__ == "__main__":
    run_bot()