# Ruta: modules/level_up.py - Detección de level para regresar a ciudad

import pyautogui
import time
import logging
from .utils import GameWindow

class LevelUp:
    def __init__(self, game_window, config):
        self.gw = game_window
        self.cfg = config
        self.level_region = config['regions'].get('level_up_button', [0, 0, 0, 0])

    def check(self):
        if not self.level_region:
            return

        img = self.gw.capture_region(self.level_region)
        if img:
            try:
                text = self.gw.read_ocr(self.level_region)
                level = int(''.join(filter(str.isdigit, text or "1")))
                if level >= 20:
                    logging.info("¡Level 20 alcanzado! Regresando a ciudad.")
                    pyautogui.press('esc')  # O usa un hotkey para logout
                    return True
            except:
                pass
        return False