# modules/utils.py - Captura estable con screenshots in-game (versión mínima y robusta)

import logging
import os
import time
import pyautogui
from PIL import Image

class GameWindow:
    def __init__(self, config: dict):
        self.config = config
        # Ruta estándar de screenshots de Tibia oficial
        self.screenshot_folder = os.path.expanduser(r'~\AppData\Local\Tibia\packages\Tibia\screenshots')
        # Hotkey configurado en Tibia para tomar screenshot
        self.hotkey_screenshot = config.get('hotkeys', {}).get('screenshot', 'f12')
        
        self.last_mtime = 0
        self.last_path = None
        
        if not os.path.exists(self.screenshot_folder):
            logging.warning(f"Carpeta de screenshots no encontrada: {self.screenshot_folder}")
            logging.info("Abre Tibia y toma un screenshot manual (F12) para crear la carpeta.")

    def trigger_screenshot(self):
        """Presiona el hotkey de screenshot en Tibia"""
        pyautogui.press(self.hotkey_screenshot)
        time.sleep(1.0)  # Tiempo suficiente para que Tibia guarde el PNG

    def get_latest_screenshot_path(self):
        """Devuelve la ruta del screenshot más reciente si es nuevo"""
        if not os.path.exists(self.screenshot_folder):
            return None

        try:
            files = [f for f in os.listdir(self.screenshot_folder) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not files:
                return None
                
            latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(self.screenshot_folder, f)))
            path = os.path.join(self.screenshot_folder, latest_file)
            mtime = os.path.getmtime(path)
            
            if mtime > self.last_mtime:
                self.last_mtime = mtime
                self.last_path = path
                logging.debug(f"Nuevo screenshot detectado: {latest_file}")
                return path
                
            return None  # No hay nuevo
        except Exception as e:
            logging.error(f"Error leyendo screenshots: {e}")
            return None

    def capture_region(self, region):
        """Toma screenshot y recorta la región"""
        self.trigger_screenshot()
        
        path = self.get_latest_screenshot_path()
        if path is None:
            # Si no hay nuevo, usa el último disponible
            if self.last_path and os.path.exists(self.last_path):
                path = self.last_path
                logging.debug("Usando screenshot anterior")
            else:
                logging.warning("No hay screenshot disponible")
                return None

        try:
            img = Image.open(path)
            x, y, w, h = region
            cropped = img.crop((x, y, x + w, y + h))
            return cropped
        except Exception as e:
            logging.error(f"Error recortando imagen: {e}")
            return None

    # Métodos básicos (mantenidos simples por ahora)
    def get_pixel_color(self, x, y):
        img = self.capture_region((x - 1, y - 1, 2, 2))
        if img:
            return img.getpixel((0, 0))
        return None

    def detect_by_color(self, pos, expected_color, atol=20):
        color = self.get_pixel_color(*pos)
        if color and np.allclose(color, expected_color, atol=atol):
            return True
        return False