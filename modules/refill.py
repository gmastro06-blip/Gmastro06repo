# Ruta: modules/refill.py

import pyautogui
import time
import logging
import numpy as np  # <--- AÑADIDO: necesario para np.allclose si lo usas en colores
from .utils import GameWindow

class Refill:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def refill_if_low(self):
        logging.debug("Ejecutando módulo Refill")

        # Ejemplo simple: si mana bajo, habla con NPC
        mana_region = self.config['regions']['mana_bar']
        mana_text = self.game_window.read_ocr(mana_region, self.config['ocr_config'])
        try:
            mana = float(mana_text.replace('%', '')) if mana_text else 100.0
        except:
            mana = 100.0

        if mana < self.config.get('mp_threshold', 40):
            logging.info(f"Mana bajo ({mana}%) → Intentando refill con NPC")
            # Mueve mouse a posición NPC y click (ajusta coords)
            npc_pos = [1000, 500]  # Ejemplo - calibra con pyautogui.position()
            pyautogui.click(npc_pos[0], npc_pos[1])
            time.sleep(1)
            pyautogui.typewrite('hi')
            pyautogui.press('enter')
            time.sleep(self.config.get('dialog_delay', 1.5))
        else:
            logging.debug(f"Mana OK ({mana}%). No refill necesario.")