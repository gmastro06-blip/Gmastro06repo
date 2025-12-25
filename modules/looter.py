# Ruta: modules/looter.py

import pyautogui
import time
import logging
import numpy as np
from .utils import GameWindow

class Looter:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.quick_loot_enabled = config.get('quick_loot', True)
        self.quick_loot_mode = config.get('quick_loot_mode', 'premium')
        self.quick_loot_hotkey = config.get('quick_loot_hotkey', 'alt')
        self.loot_priority = config.get('quick_loot_priority', [
            "gold coin", "platinum coin", "mana potion", 
            "strong health potion", "ultimate health potion", "rare item"
        ])

    def loot(self, after_kill=False):
        """Attempt to loot a corpse in the configured corpse_area"""
        logging.debug("Ejecutando módulo Looter")

        corpse_region = self.config['regions'].get('corpse_area')
        if not corpse_region:
            logging.warning("Región 'corpse_area' no definida. Loot desactivado.")
            return False

        logging.debug(f"Región de cadáver: {corpse_region}")

        # Calculate center of corpse area
        center_x = corpse_region[0] + corpse_region[2] // 2
        center_y = corpse_region[1] + corpse_region[3] // 2

        # Get color at center
        color = self.game_window.get_pixel_color(center_x, center_y)
        if color is None:
            logging.warning("No se capturó color en área de cadáver")
            return False

        logging.debug(f"Color detectado en cadáver: {color}")

        # Skip if black (likely failed capture or no corpse)
        if color == (0, 0, 0):
            logging.debug("Color negro detectado → ignorando (captura fallida o sin cadáver)")
            return False

        # Typical corpse colors in Tibia
        expected_corpse_colors = [
            (139, 69, 19),  # Brown
            (101, 67, 33),  # Dark brown
            (128, 128, 128),  # Gray
            (160, 82, 45)   # Sienna
        ]
        tolerance = 70

        is_corpse = any(np.allclose(color, expected, atol=tolerance) for expected in expected_corpse_colors)

        if is_corpse:
            logging.info(f"¡CADÁVER DETECTADO! Color {color} → Iniciando loot")
            
            if self.quick_loot_enabled and self.quick_loot_mode == 'premium':
                # Premium quick loot: hold hotkey and loot priority items
                pyautogui.keyDown(self.quick_loot_hotkey)
                time.sleep(0.1)
                for item in self.loot_priority:
                    logging.debug(f"Intentando looteo rápido de: {item}")
                    pyautogui.rightClick(center_x, center_y)
                    time.sleep(self.config.get('loot_delay', 0.3))
                pyautogui.keyUp(self.quick_loot_hotkey)
            else:
                # Non-premium: right-click to open corpse
                pyautogui.rightClick(center_x, center_y)
                time.sleep(self.config.get('loot_delay', 1.8))

            logging.info("Loot completado")
            return True
        else:
            logging.debug(f"Color {color} no es cadáver. No se looteará.")
            return False