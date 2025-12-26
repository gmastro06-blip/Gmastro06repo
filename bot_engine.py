# Ruta: bot_engine.py - Motor del bot completo (anti-ban, healer, cavebot, targeting, looter)

import logging
import time
import random
import keyboard
import pyautogui
import json
from modules.utils import GameWindow
from modules.cavebot import Cavebot
from modules.targeting import Targeting
from modules.looter import Looter
from modules.healer import Healer
from modules.level_up import LevelUp
from modules.refill import Refill

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s - %(message)s')

def human_delay(min_sec=0.3, max_sec=1.2):
    time.sleep(random.uniform(min_sec, max_sec))

def random_mouse_move():
    if random.random() < 0.3:
        current_x, current_y = pyautogui.position()
        offset_x = random.randint(-100, 100)
        offset_y = random.randint(-100, 100)
        pyautogui.moveTo(current_x + offset_x, current_y + offset_y, duration=random.uniform(0.2, 0.6))
        human_delay(0.1, 0.4)
        pyautogui.moveTo(current_x, current_y, duration=random.uniform(0.2, 0.5))

def random_break():
    if random.random() < 0.1:
        delay = random.uniform(2, 8)
        logging.info(f"Anti-ban: Pausa humana de {delay:.1f} segundos")
        time.sleep(delay)

def run_bot():
    logging.info("=== INICIANDO TIBIABOT v2.1 - Modo anti-ban activado ===")
    logging.info("Presiona ESC para detener el bot en cualquier momento.")

    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        logging.info("Config loaded successfully")
    except Exception as e:
        logging.error(f"Error cargando config.json: {e}")
        return

    game_window = GameWindow(config)

    cavebot = Cavebot(game_window, config)
    targeting = Targeting(game_window, config)
    looter = Looter(game_window, config)
    healer = Healer(game_window, config)
    level_up = LevelUp(game_window, config)
    refill = Refill(game_window, config)

    logging.info("Bot inicializado. Bucle principal con anti-ban iniciado...")

    cycle_count = 0

    try:
        while True:
            if keyboard.is_pressed('esc'):
                logging.info("Tecla ESC presionada → Deteniendo el bot de forma segura.")
                break

            cycle_count += 1

            random_mouse_move()

            if cycle_count % 10 == 0:
                random_break()

            healer.monitor()
            human_delay(0.2, 0.6)

            cavebot.navigate()
            human_delay(0.3, 0.8)

            level_up.check()
            human_delay(0.1, 0.4)

            refill.refill_if_low()
            human_delay(0.2, 0.5)

            time.sleep(random.uniform(0.4, 1.1))

    except Exception as e:
        logging.error(f"Error crítico en el bucle principal: {e}")

    finally:
        logging.info("=== BOT DETENIDO SEGURAMENTE ===")

if __name__ == "__main__":
    run_bot()