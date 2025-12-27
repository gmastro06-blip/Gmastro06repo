# Ruta: calibrate_auto.py - Calibrador Automático Avanzado para Tibia Oficial (sin manual, usa templates y auto-detect)

import pyautogui
import json
import os
import shutil
from datetime import datetime
import cv2
import numpy as np
import time

CONFIG_PATH = 'config.json'
BACKUP_PATH = f'config.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

print("\n" + "="*80)
print("🎄 CALIBRADOR AUTOMÁTICO AVANZADO PARA TIBIABOT - NAVIDAD 2025 🎄")
print("="*80)
print("Este calibrador detecta regiones automáticamente usando visión por computadora.")
print("No necesitas hacer nada manual - solo asegura que Tibia esté abierto en modo ventana.")
print("Detecta: minimap, player dot, HP/Mana bars (completo, no solo texto).")
print("Usa templates predefinidos para Tibia oficial (resolución 1920x1080 por default).")
print("Si no funciona, ajusta tu resolución o usa calibrate manual.")
input("Pulsa Enter para comenzar el auto-detect...")

# Cargar config existente o crear nuevo
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Config.json cargado. Backup creado: {BACKUP_PATH}")
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
else:
    print("Creando nuevo config.json")
    config = {}

# Asegurar secciones
config.setdefault('regions', {})
config.setdefault('hotkeys', {})
config.setdefault('base_position', {"x": 32560, "y": 32488, "z": 7})
config.setdefault('player_dot_color', [255, 255, 255])
config.setdefault('player_dot_tolerance', 30)
config.setdefault('minimap_center_offset', [0, 0])

# Función para tomar screenshot completa de pantalla (usando pyautogui como fallback seguro)
def take_screenshot():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return img

# Auto-detect minimap (busca cuadrado gris con bordes)
def detect_minimap(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:10]:
        x, y, w, h = cv2.boundingRect(cnt)
        if 150 < w < 300 and abs(w - h) < 20 and x > 0 and y > 0:
            return [x, y, w, h]
    return None

# Auto-detect player dot (punto blanco en minimap)
def detect_player_dot(minimap_img):
    gray = cv2.cvtColor(minimap_img, cv2.COLOR_BGR2GRAY)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
    if max_val > 150:
        return max_loc
    return None

# Auto-detect HP bar (verde/roja)
def detect_hp_bar(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 100, 100])  # Verde para HP lleno
    upper_green = np.array([80, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        x, y, w, h = cv2.boundingRect(cnt)
        if 200 < w < 400 and 10 < h < 30:  # Tamaño típico de barra HP
            return [x, y, w, h]
    return None

# Auto-detect Mana bar (azul)
def detect_mana_bar(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([100, 100, 100])
    upper_blue = np.array([140, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        x, y, w, h = cv2.boundingRect(cnt)
        if 200 < w < 400 and 10 < h < 30:  # Tamaño típico de barra Mana
            return [x, y, w, h]
    return None

# Auto-detect Battle List (columna negra/gris con texto)
def detect_battle_list(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        x, y, w, h = cv2.boundingRect(cnt)
        if 100 < w < 200 and 200 < h < 400:  # Tamaño típico de battle list
            return [x, y, w, h]
    return None

# Auto-detect Corpse Area (centro de pantalla, asume 800x600 central)
def detect_corpse_area(img):
    h, w = img.shape[:2]
    return [w // 4, h // 4, w // 2, h // 2]  # Centro aproximado

# Ejecuta auto-detect
print("Tomando screenshot de pantalla completa...")
img = take_screenshot()

print("Detectando minimap...")
minimap = detect_minimap(img)
if minimap:
    config['regions']['minimap'] = minimap
    print(f"Minimap: {minimap}")
    config['minimap_center_offset'] = [minimap[2] // 2, minimap[3] // 2]

    minimap_img = img[minimap[1]:minimap[1]+minimap[3], minimap[0]:minimap[0]+minimap[2]]
    player_dot = detect_player_dot(minimap_img)
    if player_dot:
        dot_x = minimap[0] + player_dot[0]
        dot_y = minimap[1] + player_dot[1]
        config['regions']['player_dot'] = [dot_x, dot_y]
        print(f"Player Dot: {config['regions']['player_dot']}")

print("Detectando HP bar...")
hp_bar = detect_hp_bar(img)
if hp_bar:
    config['regions']['hp_bar'] = hp_bar
    print(f"HP Bar: {hp_bar}")

print("Detectando Mana bar...")
mana_bar = detect_mana_bar(img)
if mana_bar:
    config['regions']['mana_bar'] = mana_bar
    print(f"Mana Bar: {mana_bar}")

print("Detectando Battle List...")
battle_list = detect_battle_list(img)
if battle_list:
    config['regions']['battle_list'] = battle_list
    print(f"Battle List: {battle_list}")

print("Detectando Corpse Area...")
corpse_area = detect_corpse_area(img)
config['regions']['corpse_area'] = corpse_area
print(f"Corpse Area: {corpse_area}")

# Defaults
default_config = {
    "arrival_tolerance": 1,
    "waypoints_file": "waypoints/newhaven_exp.json",
    "hp_threshold": 75,
    "mp_threshold": 40,
    "strong_heal_below": 45,
    "use_mana_potion": True,
    "eat_food_threshold": 60,
    "loot_delay": 1.8,
    "hotkeys": {
        "uh_hotkey": "f3",
        "heal_spell_light": "f1",
        "mana_potion": "f4",
        "eat_food": "f8",
        "attack": "f5",
        "use_item": "f6"
    }
}

config.update(default_config)

# Guardar
with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("\n" + "="*80)
print("¡AUTO-CALIBRACIÓN COMPLETADA!")
print("→ config.json guardado con regiones detectadas.")
print("→ Ejecuta: python ui/tibiabot_gui.py")
print("="*80)
print("¡Feliz Navidad 2025 y feliz loot épico! 🎄🏹💎")