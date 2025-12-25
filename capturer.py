# modules/capturer.py
# Capturador de templates - Versión con retardo fijo de 5 segundos

import time
import os
import cv2
import numpy as np
import pyautogui

try:
    from modules.utils import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("Capturer")
    logger.addHandler(logging.StreamHandler())

# Tamaños estándar
SIZES = {
    "hp_bar_primary": (280, 22),
    "mp_bar_primary": (280, 22),
    "muglex_assassin": (50, 50),
    "muglex_footman": (50, 50),
    "npc_gustavo": (60, 80),
    "npc_viola": (60, 80),
    "npc_supplier": (60, 80),
    "chest_viola": (80, 80),
    "level_up": (200, 60),
    "pk_player": (60, 60),
    "up_stair": (40, 40),
    "down_stair": (40, 40),
    "rope_spot": (40, 40),
    "hole": (40, 40),
}

os.makedirs("templates", exist_ok=True)

def capture_and_save(name, size):
    logger.info(f"[Capturer] Preparando captura de '{name}' ({size[0]}x{size[1]} px)")
    logger.info("Posiciona el mouse en la esquina SUPERIOR IZQUIERDA de la región deseada...")
    logger.info("Esperando 5 segundos para la captura...")
    
    time.sleep(5)  # Retardo fijo de 5 segundos

    x, y = pyautogui.position()
    screenshot = pyautogui.screenshot(region=(x, y, size[0], size[1]))
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    path = f"templates/{name}.png"
    cv2.imwrite(path, image)
    logger.info(f"[Capturer] ¡Captura completada y guardada en: {path}")
    logger.info(f"   Coordenadas usadas: x={x}, y={y}")

if __name__ == "__main__":
    logger.info("=== CAPTURADOR DE TEMPLATES - NAVIDAD 2025 ===")
    logger.info("Ejecuta desde la carpeta raíz del proyecto (TibiaBot)")
    logger.info("Se capturarán todos los templates con 5 segundos de retardo cada uno.\n")

    for name, size in SIZES.items():
        capture_and_save(name, size)
        time.sleep(1)  # Pequeña pausa entre capturas

    logger.info("\n=== ¡Todas las capturas completadas! ===")
    logger.info("Revisa la carpeta 'templates/' y usa las imágenes en tu config.json")
    logger.info("¡Feliz Navidad y feliz farmeo! 🎄🏹")