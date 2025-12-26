# Ruta: modules/targeting.py - Targeting con detección de bosses

import pyautogui
import time
import logging
import numpy as np
import cv2
from PIL import Image
import pytesseract
from .utils import GameWindow

class Targeting:
    def __init__(self, game_window, config):
        self.gw = game_window
        self.cfg = config
        self.priority_monsters = [m.lower() for m in config.get('monster_priority', [])]
        self.bosses = [b.lower() for b in config.get('bosses', [])]
        self.attack_key = config['hotkeys'].get('attack', 'f5')
        self.uh_key = config['hotkeys'].get('uh_hotkey', 'f3')
        self.last_attack_time = 0
        self.attack_cooldown = 0.4

    def _preprocess_image(self, img_array):
        """Preprocesado extremo para texto pequeño"""
        h, w = img_array.shape[:2]
        resized = cv2.resize(img_array, (w * 4, h * 4), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 8)
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
        cleaned = cv2.dilate(cleaned, kernel, iterations=1)
        return Image.fromarray(cleaned)

    def detect(self):
        """Detecta enemigos y bosses. Devuelve True si hay amenaza."""
        region = self.cfg['regions'].get('battle_list')
        if not region:
            return False

        img = self.gw.capture_region(region)
        if img is None:
            return False

        try:
            processed = self._preprocess_image(np.array(img))
            text = pytesseract.image_to_string(processed, config='--psm 6 --oem 3').strip()
            text_lower = text.lower()

            if not text_lower:
                return False

            # === DETECCIÓN DE BOSS (PRIORIDAD MÁXIMA) ===
            for boss in self.bosses:
                if boss in text_lower:
                    logging.info(f"¡¡¡BOSS DETECTADO!!! → {boss.upper()}")
                    pyautogui.press(self.uh_key)  # UH inmediata
                    time.sleep(0.3)
                    pyautogui.press(self.attack_key)
                    return True

            # === DETECCIÓN DE MONSTRUOS PRIORITARIOS ===
            for monster in self.priority_monsters:
                if monster in text_lower:
                    current_time = time.time()
                    if current_time - self.last_attack_time >= self.attack_cooldown:
                        logging.info(f"Enemigo prioritario detectado → {monster.upper()}")
                        pyautogui.press(self.attack_key)
                        self.last_attack_time = current_time
                    return True

            return False

        except Exception as e:
            logging.debug(f"Error en targeting: {e}")
            return False

    def is_enemy_present(self):
        """Verifica si hay cualquier enemigo (para loops de combate)"""
        region = self.cfg['regions'].get('battle_list')
        if not region:
            return False

        img = self.gw.capture_region(region)
        if img is None:
            return False

        try:
            processed = self._preprocess_image(np.array(img))
            text = pytesseract.image_to_string(processed, config='--psm 6').strip()
            return bool(text)
        except:
            return False

    def attack_target(self):
        """Ataque con cooldown anti-spam"""
        current_time = time.time()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            pyautogui.press(self.attack_key)
            self.last_attack_time = current_time