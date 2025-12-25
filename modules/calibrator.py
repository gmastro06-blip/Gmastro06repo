# modules/calibrator.py
# Calibrador automático de regiones (HP/MP, inventory, battle list, etc.)

import time
import cv2  # ← IMPORTADO AQUÍ
import pyautogui
from modules.utils import capture_screen, locate, CONFIG, logger

class Calibrator:
    def __init__(self):
        logger.info("[Calibrator] Iniciando calibración automática")

    def calibrate_region(self, template_path, name):
        logger.info(f"[Calibrator] Calibrando {name}...")
        logger.info("Tienes 5 segundos para posicionar Tibia correctamente...")
        time.sleep(5)

        screen = capture_screen()
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            logger.error(f"[Calibrator] No se pudo cargar el template: {template_path}")
            return None

        pos = locate(screen, template, confidence=0.9)
        if pos:
            logger.info(f"[Calibrator] {name} detectado: {pos}")
            return pos
        else:
            logger.warning(f"[Calibrator] {name} no detectado. Usa calibración manual.")
            return None

    def run(self):
        logger.info("=== INICIANDO CALIBRACIÓN AUTOMÁTICA ===")
        # Ejemplos de calibración
        hp_pos = self.calibrate_region("templates/statsBar/hp_bar_primary.png", "HP Bar")
        mp_pos = self.calibrate_region("templates/statsBar/mp_bar_primary.png", "MP Bar")
        minimap_pos = self.calibrate_region("templates/radar/minimap.png", "Minimap")
        battle_list_pos = self.calibrate_region("templates/battleList/battle_list_header.png", "Battle List")

        logger.info("[Calibrator] Calibración completada. Actualiza config.json con los valores detectados.")

if __name__ == "__main__":
    calibrator = Calibrator()
    calibrator.run()