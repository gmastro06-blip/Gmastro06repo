# modules/macros.py
import time

import cv2
import pytesseract

import modules.utils as utils
import modules.game_window as game_window


class Macros:
    def __init__(self):
        self.running = True

        self.pk_template = utils.CONFIG.get("templates", {}).get(
            "pk_player", "templates/battleList/pk_player.png"
        )
        self.logout_hotkey = utils.CONFIG.get("hotkeys", {}).get("logout", "ctrl+q")

        self.equip_hotkeys = utils.CONFIG.get("equip_hotkeys", {})
        self.gear_templates = utils.CONFIG.get("gear_templates", {})

        self.last_equip_check = 0
        self.equip_interval = utils.CONFIG.get("equip_check_interval", 300)

        utils.logger.info("[Macros] Módulo inicializado con auto-equip")

    def detect_pk(self, screen):
        gw = game_window.getGameWindowPositionAndSize()
        if gw:
            screen = utils.capture_screen(region=gw)

        result = utils.template_matching(screen, self.pk_template, threshold=0.7)
        if result:
            utils.logger.critical("[Macros] ¡PK DETECTADO! Logout inmediato.")
        return result is not None

    @staticmethod
    def _safe_gray(img):
        """Convierte a gris sin asumir nº de canales."""
        if img is None:
            return None
        if img.ndim == 2:
            return img
        if img.ndim == 3 and img.shape[2] == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        if img.ndim == 3 and img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if img.ndim == 3 and img.shape[2] == 1:
            return img[:, :, 0]
        return None

    def get_current_level(self, screen=None):
        if screen is None:
            screen = utils.capture_screen()

        gw = game_window.getGameWindowPositionAndSize()
        if gw:
            screen = utils.capture_screen(region=gw)

        level_region = utils.CONFIG.get("level_region", [1690, 180, 150, 40])
        x, y, w, h = level_region

        # Evitar crops fuera de rango
        if screen is None or screen.size == 0:
            return None
        H, W = screen.shape[:2]
        x2, y2 = min(x + w, W), min(y + h, H)
        x1, y1 = max(x, 0), max(y, 0)
        if x1 >= x2 or y1 >= y2:
            return None

        crop = screen[y1:y2, x1:x2]
        gray = self._safe_gray(crop)
        if gray is None:
            return None

        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        custom_config = r"--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789"
        try:
            text = pytesseract.image_to_string(thresh, config=custom_config).strip()
            if text.isdigit():
                level = int(text)
                utils.logger.info(f"[Macros] Nivel detectado por OCR: {level}")
                return level
            utils.logger.debug(f"[Macros] OCR no válido: '{text}'")
            return None
        except Exception as e:
            utils.logger.error(f"[Macros] Error OCR: {e}")
            return None

    def auto_equip(self, screen):
        if not utils.CONFIG.get("auto_equip", False):
            return

        current_time = time.time()
        if current_time - self.last_equip_check < self.equip_interval:
            return

        gw = game_window.getGameWindowPositionAndSize()
        if gw:
            screen = utils.capture_screen(region=gw)

        inventory_region = utils.CONFIG.get("inventory_region", [1550, 600, 350, 400])
        x, y, w, h = inventory_region
        inventory = screen[y : y + h, x : x + w]

        for gear_type, slot_region in utils.CONFIG.get("inventory_slots", {}).items():
            slot_x, slot_y, slot_w, slot_h = slot_region
            slot_image = inventory[slot_y : slot_y + slot_h, slot_x : slot_x + slot_w]

            best_template_path = self.gear_templates.get(f"best_{gear_type}")
            if not best_template_path:
                continue

            best_template = cv2.imread(best_template_path, cv2.IMREAD_UNCHANGED)
            if best_template is None:
                continue

            pos = utils.template_matching(slot_image, best_template_path, threshold=0.8)
            if pos:
                hotkey = self.equip_hotkeys.get(gear_type)
                if hotkey:
                    utils.simulate_key_press(hotkey)
                    utils.logger.info(f"[Macros] Equipado {gear_type} con {hotkey}")
                    utils.random_delay(0.5, 1.0)

        self.last_equip_check = current_time

    def emergency_logout(self):
        utils.logger.critical("[Macros] ¡EMERGENCIA! Logout ejecutado...")
        utils.simulate_key_press(self.logout_hotkey)
        time.sleep(1)

    def run_safety_checks(self, screen=None):
        if not self.running:
            return

        if screen is None:
            screen = utils.capture_screen()

        if self.detect_pk(screen):
            self.emergency_logout()
            return

        try:
            current_level = self.get_current_level(screen)
            logout_threshold = utils.CONFIG.get("logout_threshold_level", 3)
            if current_level is not None and current_level < logout_threshold:
                utils.logger.critical(
                    f"[Macros] Nivel crítico ({current_level}) < {logout_threshold}. Logout."
                )
                self.emergency_logout()
                return
        except Exception as e:
            utils.logger.error(f"[Macros] Error nivel: {e}")

        self.auto_equip(screen)

    def stop(self):
        self.running = False
        utils.logger.info("[Macros] Detenido")
