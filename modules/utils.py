# modules/utils.py (o modules/game_window.py)
import logging
import threading
import numpy as np
from PIL import Image

try:
    import mss  # type: ignore
except Exception:
    mss = None

try:
    import pytesseract  # type: ignore
except Exception:
    pytesseract = None

try:
    import win32gui  # type: ignore
except Exception:
    win32gui = None


class GameWindow:
    _sct = None
    _lock = threading.Lock()

    @classmethod
    def get_sct(cls):
        if mss is None:
            raise RuntimeError("mss no está disponible. Instala: pip install mss")
        if cls._sct is None:
            with cls._lock:
                if cls._sct is None:
                    cls._sct = mss.mss()
        return cls._sct

    def __init__(self, config: dict):
        self.config = config
        self.sct = self.get_sct()
        self.window_handle = None
        self.window_rect = None

        # Si no hay win32gui (no Windows / no pywin32), seguimos con global
        if win32gui is None:
            logging.warning("[GameWindow] win32gui no disponible. Captura será global.")
        else:
            self.find_window()

    def find_window(self):
        if win32gui is None:
            return

        def enum_handler(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "tibia" in title.lower():
                    result.append((hwnd, title))

        windows = []
        win32gui.EnumWindows(enum_handler, windows)

        if windows:
            self.window_handle = windows[0][0]
            self.window_rect = win32gui.GetWindowRect(self.window_handle)
            title = windows[0][1]
            logging.info(f"[GameWindow] Ventana Tibia: '{title}' (handle: {self.window_handle})")
        else:
            logging.warning("[GameWindow] No se encontró ventana con 'Tibia'. Captura global.")

    def _monitor_from_region(self, region):
        # region = (x, y, w, h)
        x, y, w, h = region

        # Si tenemos ventana Tibia, convertir region relativa a cliente -> screen
        if win32gui is not None and self.window_handle:
            try:
                client_top_left = win32gui.ClientToScreen(self.window_handle, (0, 0))
                abs_left = client_top_left[0] + x
                abs_top = client_top_left[1] + y
                return {"left": int(abs_left), "top": int(abs_top), "width": int(w), "height": int(h)}
            except Exception:
                # Si algo falla, caer a global
                return {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}

        # Captura global
        return {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}

    def capture_region(self, region):
        with GameWindow._lock:
            try:
                monitor = self._monitor_from_region(region)
                screenshot = self.sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                return img

            except Exception as e:
                # Silenciar srcdc (común en threading / mss en Windows)
                if "srcdc" in str(e).lower():
                    return None
                logging.error(f"[GameWindow] Error en captura: {e}")
                return None

    def get_pixel_color(self, x, y):
        img = self.capture_region((x - 1, y - 1, 2, 2))
        if img:
            return img.getpixel((0, 0))
        return None

    def read_ocr(self, region, ocr_config="--psm 7"):
        if pytesseract is None:
            logging.warning("[GameWindow] pytesseract no disponible. OCR deshabilitado.")
            return ""

        img = self.capture_region(region)
        if img is None:
            logging.warning(f"[GameWindow] Falló captura para OCR en región {region}")
            return ""

        try:
            import cv2  # type: ignore
            img_array = np.array(img)

            h, w = img_array.shape[:2]
            resized = cv2.resize(img_array, (w * 4, h * 4), interpolation=cv2.INTER_LINEAR)
            gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 21, 10
            )
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
            cleaned = cv2.dilate(cleaned, kernel, iterations=1)

            processed_img = Image.fromarray(cleaned)

            custom_config = (
                r"--oem 3 --psm 7 "
                r"-c tessedit_char_whitelist=0123456789.%xyz, "
                r"-c preserve_interword_spaces=1"
            )
            return pytesseract.image_to_string(processed_img, config=custom_config).strip()

        except Exception as e:
            logging.error(f"[GameWindow] Error OCR: {e}")
            return pytesseract.image_to_string(img, config=ocr_config).strip()

    def detect_by_color(self, pos, expected_color, atol=20):
        color = self.get_pixel_color(*pos)
        if color and np.allclose(color, expected_color, atol=atol):
            return True
        return False
