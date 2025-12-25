# Ruta: modules/level_up.py

import pyautogui
import time
import logging
import numpy as np  # <--- AÑADIDO para evitar el error
from .utils import GameWindow

class LevelUp:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config

    def check(self):
        logging.debug("Ejecutando módulo LevelUp")

        level_region = self.config['regions'].get('level_up_button', [1690, 220, 150, 60])
        logging.debug(f"Región de level up: {level_region}")

        # Detectar por color (oro brillante típico del botón level up)
        center_x = level_region[0] + level_region[2] // 2
        center_y = level_region[1] + level_region[3] // 2
        color = self.game_window.get_pixel_color(center_x, center_y)

        if color is None:
            logging.warning("No se pudo capturar color para level up")
            return

        logging.debug(f"Color detectado en botón level up: {color}")

        # Color típico de botón level up en Tibia (oro: ~ (255, 215, 0))
        expected = (255, 215, 0)
        tolerance = 80

        if np.allclose(color, expected, atol=tolerance):
            logging.info(f"¡LEVEL UP DETECTADO! Color {color} → Asignando stats")
            # Presiona hotkeys de skills en orden de prioridad
            for skill, priority in sorted(self.config['skill_priority'].items(), key=lambda x: x[1], reverse=True):
                hotkey = self.config['skill_hotkeys'].get(skill)
                if hotkey:
                    pyautogui.press(hotkey)
                    logging.info(f"Asignando {skill.upper()} con {hotkey}")
                    time.sleep(0.3)
        else:
            logging.debug("No se detectó botón de level up activo")