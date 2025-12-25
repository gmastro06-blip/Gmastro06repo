# Ruta: modules/macros.py

import pyautogui
import time
import logging
import numpy as np  # <--- AÑADIDO: necesario para np.allclose o np.array
from .utils import GameWindow

class Macros:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def auto_equip(self):
        logging.debug("Ejecutando módulo Macros - Auto-equip")

        # Ejemplo para ring (repite para amulet, weapon, shield)
        ring_region = self.config['regions']['inventory_slots']['ring']
        logging.debug(f"Región del ring: {ring_region}")

        # Leer texto en slot del ring (para detectar si está vacío o tiene item malo)
        text = self.game_window.read_ocr(ring_region, '--psm 6')
        logging.debug(f"Texto leído en slot ring: '{text}'")

        # Si no hay texto o es un ring malo, intenta equipar el mejor (click simple)
        if not text or 'empty' in text.lower():
            center_x = ring_region[0] + ring_region[2] // 2
            center_y = ring_region[1] + ring_region[3] // 2
            pyautogui.click(center_x, center_y)
            logging.info("Click en slot ring para auto-equip")
            pyautogui.press(self.config['equip_hotkeys'].get('ring', 'f10'))
            time.sleep(0.5)
        else:
            logging.debug(f"Ring OK detectado: '{text}'. No equipando.")

        # Repite para otros slots si quieres
        # amulet_region = self.config['regions']['inventory_slots']['amulet']
        # ... (añade lógica similar)