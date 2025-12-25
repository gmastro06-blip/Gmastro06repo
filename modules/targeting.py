# Ruta: modules/targeting.py

import pyautogui
import time
import logging
import numpy as np
from PIL import Image
import cv2  # Para preprocesado
import pytesseract  # Import explícito
from .utils import GameWindow

class Targeting:
    def __init__(self, game_window, config):
        self.game_window = game_window
        self.config = config
        self.priority_monsters = self.config.get('monster_priority', ['muglex_assassin', 'muglex_footman'])

    def detect(self):
        logging.debug("Ejecutando módulo Targeting - Detección de enemigos en battle list")

        battle_region = self.config['regions'].get('battle_list')
        if not battle_region:
            logging.warning("Región 'battle_list' no definida en config.json. Targeting desactivado.")
            return False

        logging.debug(f"Región de battle list: {battle_region}")

        img = self.game_window.capture_region(battle_region)
        if img is None:
            logging.warning("No se pudo capturar la battle list")
            return False

        try:
            img_array = np.array(img)

            # Escalado x3 para texto pequeño
            height, width = img_array.shape[:2]
            resized = cv2.resize(img_array, (width * 3, height * 3), interpolation=cv2.INTER_LINEAR)

            # Gris + umbral adaptativo + limpieza
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)
            kernel = np.ones((3,3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

            processed_img = Image.fromarray(cleaned)

            ocr_config = '--psm 6 --oem 3'

            text = pytesseract.image_to_string(processed_img, config=ocr_config).strip()
            logging.debug(f"Texto completo leído en battle list: '{text}'")

            if not text:
                logging.debug("Battle list vacía o texto no legible.")
                return False

            text_lower = text.lower()

            for monster in self.priority_monsters:
                if monster.lower() in text_lower:
                    logging.info(f"¡ENEMIGO DETECTADO! → {monster.upper()}")
                    pyautogui.press(self.config['hotkeys'].get('attack', 'f1'))
                    time.sleep(0.3)
                    return True

            return False

        except Exception as e:
            logging.error(f"Error en detección de enemigos: {e}")
            # Fallback simple
            try:
                text = pytesseract.image_to_string(img, config='--psm 6').strip()
                text_lower = text.lower()
                for monster in self.priority_monsters:
                    if monster.lower() in text_lower:
                        logging.info(f"ENEMIGO DETECTADO (fallback): {monster.upper()}")
                        pyautogui.press(self.config['hotkeys'].get('attack', 'f1'))
                        return True
                return False
            except Exception as e2:
                logging.error(f"Fallback también falló: {e2}")
                return False