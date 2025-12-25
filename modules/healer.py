# Ruta: modules/healer.py

import pyautogui
import time
import logging
from .utils import GameWindow

class Healer:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def monitor(self):
        # Región de HP
        hp_region = self.config['regions']['hp_bar']
        logging.debug(f"Región HP usada para OCR: {hp_region}")

        hp_text = self.game_window.read_ocr(hp_region, self.config['ocr_config'])
        logging.debug(f"Texto OCR leído en HP: '{hp_text}'")

        hp = 100.0  # Valor por defecto alto si falla OCR
        if hp_text:
            try:
                # Limpia posibles espacios o caracteres extra
                cleaned = hp_text.strip().replace('%', '').replace(' ', '')
                hp = float(cleaned)
                logging.info(f"HP detectado correctamente: {hp}%")
            except ValueError:
                logging.warning(f"No se pudo convertir HP a número: '{hp_text}'. Usando valor seguro (100%).")
        else:
            logging.warning("No se detectó texto en la barra de HP.")

        # Región de Mana
        mana_region = self.config['regions']['mana_bar']
        logging.debug(f"Región Mana usada para OCR: {mana_region}")

        mana_text = self.game_window.read_ocr(mana_region, self.config['ocr_config'])
        logging.debug(f"Texto OCR leído en Mana: '{mana_text}'")

        mana = 100.0  # Valor por defecto alto si falla OCR
        if mana_text:
            try:
                cleaned = mana_text.strip().replace('%', '').replace(' ', '')
                mana = float(cleaned)
                logging.info(f"Mana detectado correctamente: {mana}%")
            except ValueError:
                logging.warning(f"No se pudo convertir Mana a número: '{mana_text}'. Usando valor seguro (100%).")
        else:
            logging.warning("No se detectó texto en la barra de Mana.")

        # Acciones basadas en umbrales
        if hp < self.config.get('hp_threshold', 75):
            pyautogui.press(self.config['hotkeys']['heal_spell'])
            logging.info(f"HP bajo ({hp}%) → Usando heal spell ({self.config['hotkeys']['heal_spell']})")

        if hp < self.config.get('strong_heal_below', 45):
            pyautogui.press(self.config['hotkeys']['uh_hotkey'])  # UH si existe en hotkeys
            logging.info(f"HP crítico ({hp}%) → Usando UH ({self.config['hotkeys'].get('uh_hotkey', 'f3')})")

        if hp < self.config.get('eat_food_threshold', 50):
            pyautogui.press(self.config['hotkeys']['food'])
            logging.info(f"HP bajo ({hp}%) → Comiendo comida ({self.config['hotkeys']['food']})")

        if mana < self.config.get('mp_threshold', 40) and self.config.get('use_mana_potion', True):
            pyautogui.press(self.config['hotkeys']['mana_potion'])
            logging.info(f"Mana bajo ({mana}%) → Usando mana potion ({self.config['hotkeys']['mana_potion']})")

        # Si todo está bien, logueamos estado normal
        if hp >= 75 and mana >= 40:
            logging.debug(f"Estado saludable: HP {hp}%, Mana {mana}% → Sin acción necesaria")