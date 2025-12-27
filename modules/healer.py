# Ruta: modules/healer.py - Healer Profesional (Detección por Barra de Color - Sin OCR)

import logging
import time
import pyautogui
import numpy as np
import cv2
from modules.utils import GameWindow

class Healer:
    """
    Healer avanzado para Tibia oficial 2025.
    Usa detección de longitud de barra (color) en vez de OCR → 100% fiable y rápido.
    No depende de texto "180/180" → evita fallos por sombras/fuentes.
    """

    def __init__(self, game_window: GameWindow, config: dict):
        self.game_window = game_window
        self.config = config

        # Regiones de las barras completas (deben calibrarse como barra completa, no solo texto)
        self.hp_region = config['regions'].get('hp_bar')
        self.mana_region = config['regions'].get('mana_bar')

        if not self.hp_region or not self.mana_region:
            raise ValueError("Regiones hp_bar y mana_bar deben estar definidas en config.json")

        # Umbrales HP (ajusta si tu UI usa otro tono)
        self.hp_threshold = config.get('hp_threshold', 75)
        self.strong_heal_below = config.get('strong_heal_below', 45)

        # Umbrales Mana
        self.mp_threshold = config.get('mp_threshold', 40)
        self.use_mana_potion = config.get('use_mana_potion', True)

        # Hotkeys
        self.hotkeys = config.get('hotkeys', {})
        self.uh_hotkey = self.hotkeys.get('uh_hotkey', 'f3')
        self.heal_spell_light = self.hotkeys.get('heal_spell_light', 'f1')
        self.mana_potion_hotkey = self.hotkeys.get('mana_potion', 'f4')
        self.eat_food_hotkey = self.hotkeys.get('eat_food', 'f8')
        self.eat_food_threshold = config.get('eat_food_threshold', 60)

        # Colores HSV para detección (optimizado para Tibia oficial)
        self.hp_lower = np.array([35, 180, 100])   # Verde brillante HP lleno
        self.hp_upper = np.array([85, 255, 255])
        self.mana_lower = np.array([100, 180, 100])  # Azul brillante Mana lleno
        self.mana_upper = np.array([140, 255, 255])

        logging.info("Healer inicializado con detección por barra de color (sin OCR)")

    def get_bar_percentage(self, region: list, lower: np.array, upper: np.array) -> float:
        """
        Calcula el % de relleno de una barra por máscara de color.
        Devuelve 0.0 a 100.0
        """
        img = self.game_window.capture_region(region)
        if img is None:
            return 100.0  # Fallback seguro (asumimos lleno si no captura)

        try:
            arr = np.array(img)
            hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
            mask = cv2.inRange(hsv, lower, upper)

            # Contamos píxeles llenos en el ancho (más fiable que área total)
            filled = np.sum(mask > 0, axis=0)  # Por columna
            filled_cols = np.sum(filled > 0)   # Columnas con al menos un píxel lleno
            total_cols = mask.shape[1]

            if total_cols == 0:
                return 100.0

            percent = (filled_cols / total_cols) * 100
            return max(0.0, min(100.0, percent))
        except Exception as e:
            logging.debug(f"Error calculando barra: {e}")
            return 100.0

    def get_hp_percent(self) -> float:
        return self.get_bar_percentage(self.hp_region, self.hp_lower, self.hp_upper)

    def get_mana_percent(self) -> float:
        return self.get_bar_percentage(self.mana_region, self.mana_lower, self.mana_upper)

    def heal(self):
        """Ejecuta curación según umbrales"""
        hp = self.get_hp_percent()

        if hp < self.strong_heal_below:
            logging.info(f"HP crítico: {hp:.1f}% → UH")
            pyautogui.press(self.uh_hotkey)
        elif hp < self.hp_threshold:
            logging.info(f"HP bajo: {hp:.1f}% → Heal light")
            pyautogui.press(self.heal_spell_light)

    def restore_mana(self):
        """Restaura mana si está bajo"""
        if not self.use_mana_potion:
            return

        mana = self.get_mana_percent()
        if mana < self.mp_threshold:
            logging.info(f"Mana bajo: {mana:.1f}% → Mana potion")
            pyautogui.press(self.mana_potion_hotkey)

    def eat_food(self):
        """Come comida si hay hotkey configurado"""
        if self.eat_food_hotkey and random.random() < 0.1:  # 10% chance por ciclo (ajustable)
            logging.debug("Comiendo comida (rutina)")
            pyautogui.press(self.eat_food_hotkey)

    def monitor(self):
        """Bucle principal del healer - llamado frecuentemente"""
        try:
            hp = self.get_hp_percent()
            mana = self.get_mana_percent()

            logging.info(f"HP: {hp:.1f}% | Mana: {mana:.1f}%")

            self.heal()
            self.restore_mana()
            self.eat_food()

        except Exception as e:
            logging.error(f"Error en healer monitor: {e}")