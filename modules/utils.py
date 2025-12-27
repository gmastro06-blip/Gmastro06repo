# modules/utils.py - Captura preview OBS para bypass 100%

import logging
import threading
import numpy as np
from PIL import Image
import os
import time
import pyautogui
import cv2
import mss

try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except Exception:
    pytesseract = None

class GameWindow:
    def __init__(self, config: dict):
        self.config = config
        self.sct = mss.mss()
        self.preview_region = config.get('regions', {}).get('obs_preview', [0, 0, 1920, 1080])  # Ajusta a tu preview OBS

    def capture_region(self, region):
        x, y, w, h = region
        monitor = {"left": x, "top": y, "width": w, "height": h}
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        if np.mean(np.array(img)) < 10:  # Check negro
            logging.warning("Capture negra - chequea OBS")
            return None
        return img

    # Resto igual (get_pixel_color, read_ocr, detect_by_color)
    def get_pixel_color(self, x, y):
        img = self.capture_region((x - 1, y - 1, 2, 2))
        if img:
            return img.getpixel((0, 0))
        return None

    def read_ocr(self, region):
        if pytesseract is None:
            return ""

        img = self.capture_region(region)
        if img is None:
            return ""

        try:
            img_array = np.array(img)
            resized = cv2.resize(img_array, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            processed_img = Image.fromarray(thresh)
            text = pytesseract.image_to_string(processed_img, config='--psm 7 -c tessedit_char_whitelist=0123456789/').strip()
            logging.debug(f"OCR en {region}: '{text}'")
            return text
        except Exception as e:
            logging.error(f"Error OCR: {e}")
            return ""

    def detect_by_color(self, pos, expected_color, atol=20):
        color = self.get_pixel_color(*pos)
        if color and np.allclose(color, expected_color, atol=atol):
            return True
        return False