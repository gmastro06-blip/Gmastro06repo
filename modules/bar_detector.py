# En modules/bar_detector.py

import numpy as np
import cv2
from modules.utils import GameWindow

class BarDetector:
    def __init__(self, game_window: GameWindow, config: dict):
        self.game_window = game_window
        self.hp_region = config['regions']['hp_bar']
        self.mana_region = config['regions']['mana_bar']

        # Colores típicos Tibia oficial 2025 (ajusta si tu UI es diferente)
        self.hp_color_lower = np.array([40, 200, 100])   # Verde brillante HP
        self.hp_color_upper = np.array([80, 255, 255])
        self.mana_color_lower = np.array([100, 200, 100])  # Azul brillante Mana
        self.mana_color_upper = np.array([140, 255, 255])

    def get_bar_percent(self, region, lower, upper) -> float:
        img = self.game_window.capture_region(region)
        if img is None:
            return 100.0  # Fallback seguro

        arr = np.array(img)
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)

        mask = cv2.inRange(hsv, lower, upper)
        filled_pixels = np.sum(mask > 0)
        total_pixels = mask.shape[1]  # Ancho de la barra (altura puede variar)

        if total_pixels == 0:
            return 100.0

        percent = (filled_pixels / total_pixels) * 100
        return max(0, min(100, percent))  # Clamp 0-100

    def get_hp_percent(self) -> float:
        return self.get_bar_percent(self.hp_region, self.hp_color_lower, self.hp_color_upper)

    def get_mana_percent(self) -> float:
        return self.get_bar_percent(self.mana_region, self.mana_color_lower, self.mana_color_upper)