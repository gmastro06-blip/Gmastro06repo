# Ruta: modules/healer.py - Healer inteligente y humano

import pyautogui
import time
import random
import logging
from .utils import GameWindow

class Healer:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def monitor(self):
        logging.debug("Ejecutando módulo Healer (modo humano y seguro)")

        hp_region = self.config['regions']['hp_bar']
        mana_region = self.config['regions']['mana_bar']

        hp_text = self.game_window.read_ocr(hp_region)
        mana_text = self.game_window.read_ocr(mana_region)

        hp = 100.0
        mana = 100.0

        if hp_text:
            try:
                hp = float(''.join(filter(str.isdigit, hp_text.strip('%'))))
                hp = min(hp, 100)
            except:
                hp = 100.0

        if mana_text:
            try:
                mana = float(''.join(filter(str.isdigit, mana_text.strip('%'))))
                mana = min(mana, 100)
            except:
                mana = 100.0

        logging.info(f"HP detectado: {hp:.1f}% | Mana: {mana:.1f}%")

        strong_threshold = self.config.get('strong_heal_below', 45)
        light_threshold = self.config.get('hp_threshold', 75)
        food_threshold = self.config.get('eat_food_threshold', 60)
        mana_threshold = self.config.get('mp_threshold', 30)

        last_action = "Ninguna"

        if hp < strong_threshold:
            pyautogui.press(self.config['hotkeys'].get('uh_hotkey', 'f3'))
            logging.info(f"¡HP CRÍTICO ({hp}%)! → Ultimate Healing")
            last_action = "UH usada"
            time.sleep(random.uniform(0.8, 1.5))

        elif hp < light_threshold:
            if random.random() < 0.88:
                pyautogui.press(self.config['hotkeys'].get('heal_spell_light', 'f1'))
                logging.info(f"HP bajo ({hp}%) → Heal light")
                last_action = "Heal light"
                time.sleep(random.uniform(0.5, 1.0))

        if hp < food_threshold and random.random() < 0.75:
            pyautogui.press(self.config['hotkeys'].get('eat_food', 'f8'))
            logging.info(f"Comiendo comida (HP {hp}%)")
            last_action = "Comiendo comida"
            time.sleep(random.uniform(1.2, 2.8))

        if mana < mana_threshold and self.config.get('use_mana_potion', True):
            if random.random() < 0.92:
                pyautogui.press(self.config['hotkeys'].get('mana_potion', 'f4'))
                logging.info(f"Mana bajo ({mana}%) → Mana potion")
                last_action = "Mana potion"
                time.sleep(random.uniform(0.6, 1.2))

        # Actualizar UI si está abierta
        try:
            gui_module = __import__('ui.tibiabot_gui', fromlist=['app'])
            if hasattr(gui_module, 'app') and gui_module.app:
                gui_module.app.update_healing_status(hp, mana, last_action)
        except:
            pass

        time.sleep(random.uniform(0.3, 0.9))