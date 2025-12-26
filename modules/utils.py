# Ruta: modules/utils.py - GameWindow SIN ERRORES 'srcdc' EN LOGS

import logging
import numpy as np
from PIL import Image
import pytesseract
import mss
import pyautogui
import win32gui
import threading

class GameWindow:
    _sct = None
    _lock = threading.Lock()

    @classmethod
    def get_sct(cls):
        if cls._sct is None:
            with cls._lock:
                if cls._sct is None:
                    cls._sct = mss.mss()
        return cls._sct

    def __init__(self, config):
        self.config = config
        self.sct = GameWindow.get_sct()
        self.window_handle = None
        self.window_rect = None
        self.find_window()

    def find_window(self):
        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if 'tibia' in title.lower():
                    result.append((hwnd, title))

        windows = []
        win32gui.EnumWindows(enum_handler, windows)

        if windows:
            self.window_handle = windows[0][0]
            self.window_rect = win32gui.GetWindowRect(self.window_handle)
            title = windows[0][1]
            logging.info(f"Ventana de Tibia encontrada: '{title}' (handle: {self.window_handle})")
        else:
            logging.warning("No se encontró ventana con 'Tibia'. Usando captura global.")

    def capture_region(self, region):
        with GameWindow._lock:
            try:
                if self.window_handle:
                    client_rect = win32gui.GetClientRect(self.window_handle)
                    client_top_left = win32gui.ClientToScreen(self.window_handle, (0, 0))
                    client_left = client_top_left[0]
                    client_top = client_top_left[1]

                    abs_left = client_left + region[0]
                    abs_top = client_top + region[1]

                    monitor = {"left": abs_left, "top": abs_top, "width": region[2], "height": region[3]}
                else:
                    monitor = {"left": region[0], "top": region[1], "width": region[2], "height": region[3]}

                screenshot = self.sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return img

            except mss.exception.ScreenShotError as e:
                # Silencia específicamente el error 'srcdc' (común en threading con mss)
                if 'srcdc' in str(e).lower():
                    return None  # Devuelve None sin loggear
                logging.error(f"Error en captura: {e}")
                return None

            except Exception as e:
                logging.error(f"Error en captura: {e}")
                return None

    def get_pixel_color(self, x, y):
        img = self.capture_region((x - 1, y - 1, 2, 2))
        if img:
            return img.getpixel((0, 0))
        return None

    def read_ocr(self, region, ocr_config='--psm 7'):
        img = self.capture_region(region)
        if img is None:
            logging.warning(f"Falló captura para OCR en región {region}")
            return ""

        try:
            import cv2
            img_array = np.array(img)

            height, width = img_array.shape[:2]
            resized = cv2.resize(img_array, (width * 4, height * 4), interpolation=cv2.INTER_LINEAR)

            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 10)
            kernel = np.ones((3,3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
            cleaned = cv2.dilate(cleaned, kernel, iterations=1)

            processed_img = Image.fromarray(cleaned)

            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.%xyz, -c preserve_interword_spaces=1'
            text = pytesseract.image_to_string(processed_img, config=custom_config).strip()

            if text:
                logging.debug(f"OCR EXITOSO en {region}: '{text}'")
            else:
                logging.debug(f"OCR vacío en {region}")
            return text

        except Exception as e:
            logging.error(f"Error OCR: {e}")
            return pytesseract.image_to_string(img, config=ocr_config).strip()

    def detect_by_color(self, pos, expected_color, atol=20):
        color = self.get_pixel_color(*pos)
        if color and np.allclose(color, expected_color, atol=atol):
            return True
        return False