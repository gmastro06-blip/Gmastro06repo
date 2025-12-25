# modules/utils.py
import cv2
import numpy as np
import time
import random
import json
import os
import logging
from datetime import datetime
"""Utilidades base del bot.

Nota importante para tests/CI:
  - pyautogui y pynput pueden fallar al importarse en entornos headless.
  - Para que los tests unitarios puedan importar el paquete, hacemos
    importaciones tolerantes a fallos y degradamos algunas funciones a NO-OP.
"""

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

try:
    from pynput.keyboard import Controller as KeyboardController  # type: ignore
    from pynput.mouse import Controller as MouseController  # type: ignore
except Exception:  # pragma: no cover
    KeyboardController = None
    MouseController = None

from pathlib import Path

# Configurar logger
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename=f"logs/bot_log_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TibiaBot")
logger.addHandler(logging.StreamHandler())

# Cargar configuración global
def load_config():
    config_path = 'config.json'
    if not os.path.exists(config_path):
        raise FileNotFoundError("config.json no encontrado")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

CONFIG = load_config()

# Controladores (pueden ser None en entornos headless)
keyboard = KeyboardController() if KeyboardController else None
mouse = MouseController() if MouseController else None


def _to_gray_safe(img: np.ndarray) -> np.ndarray:
    """
    Convierte img a gris de forma segura soportando:
      - (H,W) gris
      - (H,W,1) gris con canal
      - (H,W,3) BGR
      - (H,W,4) BGRA
    """
    if img is None:
        return img
    if img.ndim == 2:
        return img
    if img.ndim == 3:
        c = img.shape[2]
        if c == 1:
            return img[:, :, 0]
        if c == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        if c == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    # formato raro: intentar aplanar
    return img


def _to_bgr_safe(img: np.ndarray) -> np.ndarray:
    """
    Garantiza BGR 3 canales (para inRange y lectura de barras).
    Soporta gris (H,W) y (H,W,1).
    """
    if img is None:
        return img
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.ndim == 3:
        c = img.shape[2]
        if c == 3:
            return img
        if c == 4:
            return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        if c == 1:
            return cv2.cvtColor(img[:, :, 0], cv2.COLOR_GRAY2BGR)
    return img


# Captura
def capture_screen(region=None):
    if pyautogui is None:
        raise RuntimeError(
            "pyautogui no está disponible (probablemente entorno headless). "
            "Para tests, pasa 'screen' mockeado y/o parchea capture_screen."
        )
    if region is None:
        region = CONFIG.get("window_region", (0, 0, 1920, 1080))

    screenshot = pyautogui.screenshot(region=region)
    arr = np.array(screenshot)

    # PIL suele dar RGB/RGBA, pero a veces puede llegar gris (H,W) o (H,W,1)
    if arr.ndim == 3 and arr.shape[2] == 4:
        # PIL -> RGBA
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
        return _to_bgr_safe(bgr)
    if arr.ndim == 3 and arr.shape[2] == 3:
        # PIL -> RGB
        bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        return _to_bgr_safe(bgr)

    # Si llega en gris u otro formato, normalizar a BGR
    return _to_bgr_safe(arr)


def loadFromRGBToGray(path):
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    return _to_gray_safe(img)


def locate(image, template, confidence=0.8):
    # Convertir a gris de forma segura (soporta 1 canal)
    image_g = _to_gray_safe(image)
    template_g = _to_gray_safe(template)

    result = cv2.matchTemplate(image_g, template_g, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        h, w = template_g.shape[:2]
        return (max_loc[0], max_loc[1], max_loc[0] + w, max_loc[1] + h)
    return None


def hashit(image):
    return hash(np.packbits(image).tobytes())


def template_matching(image, template_path, threshold=0.8):
    if not os.path.exists(template_path):
        logger.warning(f"Template no encontrado: {template_path}")
        return None
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        return None

    # Pasar ambos a gris para robustez (y evitar 3 vs 4 vs 1 canales)
    img_g = _to_gray_safe(image)
    tpl_g = _to_gray_safe(template)

    result = cv2.matchTemplate(img_g, tpl_g, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        return max_loc
    return None


def get_hp_percentage(screen, hp_bar_region):
    screen = _to_bgr_safe(screen)
    x, y, w, h = hp_bar_region
    bar = screen[y:y+h, x:x+w]

    # HP = tramo VERDE (vida actual). No sumar rojo.
    mask = cv2.inRange(bar, np.array([0, 200, 0]), np.array([100, 255, 100]))

    filled = cv2.countNonZero(mask)
    total = w * h
    return round((filled / total) * 100, 1) if total > 0 else 100.0


def get_mp_percentage(screen, mp_bar_region):
    screen = _to_bgr_safe(screen)
    x, y, w, h = mp_bar_region
    bar = screen[y:y+h, x:x+w]

    # MP (mana) – rango más realista (y compatible con el mock)
    lower = np.array([200, 100, 0])   # B alto, G medio, R bajo
    upper = np.array([255, 200, 80])

    mask = cv2.inRange(bar, lower, upper)

    filled = cv2.countNonZero(mask)
    total = w * h
    return round((filled / total) * 100, 1) if total > 0 else 100.0


def detect_stair_type(screen, region=CONFIG.get("window_region")):
    stair_templates = CONFIG.get("templates", {})
    for stair_type, template_path in CONFIG.get("stair_templates", {}).items():
        pos = template_matching(screen, template_path, threshold=0.75)
        if pos:
            logger.info(f"[Utils] Detectado {stair_type} en {pos}")
            return stair_type
    return None


def simulate_key_press(key):
    """
    Simula pulsación de tecla tolerante a errores y teclas especiales.
    En tests/CI no debe reventar: si falla, se ignora.
    """
    time.sleep(random.uniform(0.01, 0.03))

    if keyboard is None:
        return

    try:
        from pynput.keyboard import Key  # type: ignore
    except Exception:
        return

    if key is None:
        return

    if isinstance(key, str):
        raw = key.strip().lower()
    else:
        raw = key

    special_map = {
        "enter": Key.enter,
        "return": Key.enter,
        "esc": Key.esc,
        "escape": Key.esc,
        "space": Key.space,
        "tab": Key.tab,
        "backspace": Key.backspace,
        "delete": Key.delete,
        "del": Key.delete,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "shift": Key.shift,
        "ctrl": Key.ctrl,
        "control": Key.ctrl,
        "alt": Key.alt,
        "cmd": Key.cmd,
        "win": Key.cmd,
    }

    fkey_map = {f"f{i}": getattr(Key, f"f{i}") for i in range(1, 13) if hasattr(Key, f"f{i}")}

    def _to_pynput_token(token: str):
        token = token.strip().lower()
        if token in fkey_map:
            return fkey_map[token]
        if token in special_map:
            return special_map[token]
        return token

    try:
        if isinstance(raw, str) and "+" in raw:
            parts = [p.strip() for p in raw.split("+") if p.strip()]
            tokens = [_to_pynput_token(p) for p in parts]

            for t in tokens[:-1]:
                keyboard.press(t)
            keyboard.press(tokens[-1])
            time.sleep(random.uniform(0.01, 0.02))
            keyboard.release(tokens[-1])
            for t in reversed(tokens[:-1]):
                keyboard.release(t)
            return

        token = _to_pynput_token(raw) if isinstance(raw, str) else raw
        keyboard.press(token)
        time.sleep(random.uniform(0.01, 0.02))
        keyboard.release(token)

    except ValueError:
        return
    except Exception:
        return


def simulate_mouse_click(position, button='left'):
    if pyautogui is None or mouse is None:
        return
    steps = 12
    current = mouse.position
    for i in range(1, steps + 1):
        nx = current[0] + (position[0] - current[0]) * i / steps
        ny = current[1] + (position[1] - current[1]) * i / steps
        mouse.position = (nx, ny)
        time.sleep(random.uniform(0.01, 0.03))
    pyautogui.click(x=position[0], y=position[1], button=button)


def simulate_mouse_drag(start_pos, end_pos):
    if pyautogui is None or mouse is None:
        return
    simulate_mouse_click(start_pos, button='left')
    time.sleep(random.uniform(0.1, 0.2))
    steps = 15
    for i in range(1, steps + 1):
        nx = start_pos[0] + (end_pos[0] - start_pos[0]) * i / steps
        ny = start_pos[1] + (end_pos[1] - start_pos[1]) * i / steps
        mouse.position = (nx, ny)
        time.sleep(random.uniform(0.01, 0.03))
    pyautogui.mouseUp(button='left')


def random_delay(min_delay=0.5, max_delay=2.0):
    time.sleep(random.uniform(min_delay, max_delay))


def a_star_pathfinding(start, goal, obstacles=set()):
    from heapq import heappush, heappop
    neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    came_from = {}
    cost = {start: 0}
    frontier = []
    heappush(frontier, (0, start))

    while frontier:
        _, current = heappop(frontier)
        if current == goal:
            break
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if neighbor in obstacles:
                continue
            new_cost = cost[current] + (1.4 if abs(dx) + abs(dy) == 2 else 1)
            if neighbor not in cost or new_cost < cost[neighbor]:
                cost[neighbor] = new_cost
                priority = new_cost + ((neighbor[0] - goal[0]) ** 2 + (neighbor[1] - goal[1]) ** 2) ** 0.5
                heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = came_from.get(current, start)
    path.reverse()
    return path


def detect_player_position(screen=None):
    """
    Detecta la posición del jugador en el minimapa.
    Retorna: (x, y, z) o None si no detecta
    """
    if screen is None:
        screen = capture_screen(region=CONFIG.get("window_region"))

    screen = _to_bgr_safe(screen)

    minimap_region = CONFIG.get("minimap_region")
    if not minimap_region:
        logger.warning("[Position] minimap_region no configurado")
        return None

    x, y, w, h = minimap_region
    minimap = screen[y:y+h, x:x+w]

    player_color = np.array(CONFIG.get("player_dot_color", [255, 255, 255]))
    tolerance = CONFIG.get("player_dot_tolerance", 50)

    lower = player_color - tolerance
    upper = player_color + tolerance
    lower = np.maximum(lower, 0)
    upper = np.minimum(upper, 255)

    mask = cv2.inRange(minimap, lower, upper)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    M = cv2.moments(largest)
    if M["m00"] == 0:
        return None

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    center_x, center_y = CONFIG.get("minimap_center_offset", [w // 2, h // 2])
    sqm_per_pixel = 1.0 / CONFIG.get("sqm_size_pixels", 10)

    rel_x = (cx - center_x) * sqm_per_pixel
    rel_y = (cy - center_y) * sqm_per_pixel

    base_x = CONFIG.get("base_position", {}).get("x", 32560)
    base_y = CONFIG.get("base_position", {}).get("y", 32488)
    base_z = CONFIG.get("base_position", {}).get("z", 7)

    current_x = int(base_x + rel_x)
    current_y = int(base_y + rel_y)
    current_z = base_z

    logger.debug(f"[Position] Detectado: {current_x}, {current_y}, {current_z}")
    return (current_x, current_y, current_z)
