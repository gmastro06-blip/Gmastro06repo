# Ruta: calibrate.py - Calibrador mejorado para Tibiabot (genera config.json perfecto)

import pyautogui
import json
import os
import shutil
from datetime import datetime

CONFIG_PATH = 'config.json'
BACKUP_PATH = f'config.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

print("\n" + "="*70)
print("🎄 CALIBRADOR MEJORADO PARA TIBIABOT - NAVIDAD 2025 🎄")
print("="*70)
print("Abre Tibia en modo ventana (no fullscreen).")
print("Maximiza el minimapa (Alt + M) si está pequeño.")
print("Mueve el mouse con precisión y presiona Enter en cada paso.\n")
input("Pulsa Enter para comenzar...")

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

def get_point(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    input("   Mueve el mouse al centro exacto → Pulsa Enter")
    x, y = pyautogui.position()
    print(f"   Posición: ({x}, {y})")
    return [x, y]

def get_region(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    input("   1. Esquina superior izquierda → Pulsa Enter")
    x1, y1 = pyautogui.position()
    print(f"      Superior izquierda: ({x1}, {y1})")

    input("   2. Esquina inferior derecha → Pulsa Enter")
    x2, y2 = pyautogui.position()
    print(f"      Inferior derecha: ({x2}, {y2})")

    region = [x1, y1, x2 - x1, y2 - y1]
    print(f"   Región: {region}")
    return region

# === CALIBRACIÓN EN ORDEN ÓPTIMO ===
print("\n=== CALIBRANDO REGIONES CLAVE ===")

config['regions']['player_dot'] = get_point(
    "Player Dot (CRUCIAL)",
    "Centro EXACTO del punto blanco en el minimapa. ¡Este es el más importante!"
)

config['regions']['hp_bar'] = get_region(
    "HP Bar",
    "SOLO el texto del porcentaje de HP (ej: '85%'). Zona pequeña."
)

config['regions']['mana_bar'] = get_region(
    "Mana Bar",
    "SOLO el texto del porcentaje de Mana (ej: '90%'). Zona pequeña."
)

config['regions']['minimap'] = get_region(
    "Minimap completo",
    "Todo el cuadro del minimapa (incluyendo bordes)."
)

config['regions']['battle_list'] = get_region(
    "Battle List",
    "Toda la columna donde aparecen nombres de criaturas."
)

config['regions']['corpse_area'] = get_region(
    "Corpse Area",
    "Centro de pantalla donde aparecen cadáveres (para loot)."
)

config['regions']['level_up_button'] = get_region(
    "Botón Level Up",
    "Zona donde aparece el mensaje de level up."
)

# Calcular offset del centro del minimapa
minimap = config['regions']['minimap']
config['minimap_center_offset'] = [minimap[2] // 2, minimap[3] // 2]

# === COMPLETAR CONFIG CON VALORES POR DEFECTO ===
default_config = {
    "window_region": [0, 0, 1920, 1080],
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
    },
    "monster_priority": ["muglex_assassin", "muglex_footman"],
    "bosses": ["ferumbras", "orshabaal", "ghazbaran", "morgaroth"]
}

# Fusionar con defaults
for key, value in default_config.items():
    if key not in config:
        config[key] = value
    elif isinstance(value, dict):
        config[key].update(value)

# === GUARDAR CONFIG ===
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("\n" + "="*70)
print("¡CALIBRACIÓN COMPLETADA Y CONFIG.JSON GENERADO!")
print("→ Tu bot ahora tiene regiones perfectas para Tibia oficial.")
print("→ Ejecuta: python ui/tibiabot_gui.py")
print("→ START BOT → ¡A cazar en Newhaven!")
print("="*70)
print("¡Feliz Navidad 2025 y feliz loot épico! 🎄🏹💎")