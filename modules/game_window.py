# modules/game_window.py
# Detección precisa del game window usando flechas (como bots profesionales)

import pathlib
from typing import Optional, Tuple

from modules.utils import (
    capture_screen,
    locate,
    hashit,
    loadFromRGBToGray,
    CONFIG,
    logger,
)

currentPath = pathlib.Path(__file__).parent.resolve()
arrowsPath = f"{currentPath}/../templates/gameWindow/images/arrows"

# Cargar imágenes de flechas (GRIS para hash)
arrows = {
    "leftGameWindow00": loadFromRGBToGray(f"{arrowsPath}/leftGameWindow00.png"),
    "leftGameWindow01": loadFromRGBToGray(f"{arrowsPath}/leftGameWindow01.png"),
    "leftGameWindow10": loadFromRGBToGray(f"{arrowsPath}/leftGameWindow10.png"),
    "leftGameWindow11": loadFromRGBToGray(f"{arrowsPath}/leftGameWindow11.png"),
    "rightGameWindow00": loadFromRGBToGray(f"{arrowsPath}/rightGameWindow00.png"),
    "rightGameWindow01": loadFromRGBToGray(f"{arrowsPath}/rightGameWindow01.png"),
    "rightGameWindow10": loadFromRGBToGray(f"{arrowsPath}/rightGameWindow10.png"),
    "rightGameWindow11": loadFromRGBToGray(f"{arrowsPath}/rightGameWindow11.png"),
}

# Hashes para detección rápida
arrowsHashes = {hashit(img): name for name, img in arrows.items() if img is not None}

# Cache para rendimiento
gameWindowCache = {
    "left": {"arrow": None, "position": None},
    "right": {"arrow": None, "position": None},
}


def getLeftArrowPosition(screenshot):
    """
    screenshot puede venir en BGR/BGRA/GRAY.
    NO conviertas aquí con cv2.cvtColor: utils.locate ya normaliza.
    """
    global gameWindowCache

    if gameWindowCache["left"]["position"] is not None:
        return gameWindowCache["left"]["position"]

    for name in ["leftGameWindow01", "leftGameWindow11", "leftGameWindow10", "leftGameWindow00"]:
        tpl = arrows.get(name)
        if tpl is None:
            continue
        pos = locate(screenshot, tpl, confidence=0.90)
        if pos:
            gameWindowCache["left"]["arrow"] = name
            gameWindowCache["left"]["position"] = pos
            logger.info(f"[GameWindow] Flecha izquierda detectada: {name}")
            return pos

    return None


def getRightArrowPosition(screenshot):
    """
    screenshot puede venir en BGR/BGRA/GRAY.
    NO conviertas aquí con cv2.cvtColor: utils.locate ya normaliza.
    """
    global gameWindowCache

    if gameWindowCache["right"]["position"] is not None:
        return gameWindowCache["right"]["position"]

    for name in ["rightGameWindow01", "rightGameWindow11", "rightGameWindow10", "rightGameWindow00"]:
        tpl = arrows.get(name)
        if tpl is None:
            continue
        pos = locate(screenshot, tpl, confidence=0.90)
        if pos:
            gameWindowCache["right"]["arrow"] = name
            gameWindowCache["right"]["position"] = pos
            logger.info(f"[GameWindow] Flecha derecha detectada: {name}")
            return pos

    return None


def getGameWindowPositionAndSize(screenshot=None) -> Optional[Tuple[int, int, int, int]]:
    """
    - Si 'screenshot' viene como argumento, NO recaptura (mejor para rendimiento y tests).
    - Si viene None, captura usando window_region.
    """
    if screenshot is None:
        screenshot = capture_screen(region=CONFIG.get("window_region"))

    left = getLeftArrowPosition(screenshot)
    right = getRightArrowPosition(screenshot)

    if not left or not right:
        logger.warning("[GameWindow] No se detectaron ambas flechas. Usando fallback.")
        return None

    # Calcular centro entre flechas
    center_x = (left[0] + left[2] + right[0]) // 2
    x = center_x - 480  # Mitad del ancho (960/2 para 1080)
    y = left[1] + 5

    width = 960   # 1080p
    height = 704

    position = (x, y, width, height)
    logger.info(f"[GameWindow] Detectado: {position}")
    return position
