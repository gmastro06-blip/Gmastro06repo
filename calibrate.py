# Ruta: calibrate.py - Calibrador optimizado para OCR de minimapa y regiones críticas

import pyautogui
import json
import os
import shutil
from datetime import datetime

CONFIG_PATH = 'config.json'
BACKUP_PATH = f'config.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

# Configuración de pyautogui para precisión
pyautogui.FAILSAFE = True  # Mueve el mouse a la esquina superior izquierda para abortar
pyautogui.PAUSE = 0.1  # Pequeña pausa entre acciones

print("=== CALIBRADOR OPTIMIZADO PARA TIBIABOT ===")
print("Abre Tibia en modo ventana (NO fullscreen).")
print("Asegúrate de que las coordenadas (x,y,z) sean visibles en el minimapa.")
print("Mueve el mouse con precisión a las posiciones indicadas y presiona Enter.")
print("Para abortar, mueve el mouse a la esquina superior izquierda.\n")
input("Presiona Enter para comenzar...")

# Cargar config existente
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Config.json cargado. Backup creado en: {BACKUP_PATH}\n")
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
else:
    print("config.json no encontrado. Creando uno nuevo.")
    config = {}

# Asegurar secciones necesarias
if 'regions' not in config:
    config['regions'] = {}
if 'hotkeys' not in config:
    config['hotkeys'] = {}
if 'base_position' not in config:
    config['base_position'] = {"x": 32560, "y": 32488, "z": 7}

def get_region(name, description):
    print(f"\n→ Calibrando: {name}")
    print(f"   {description}")
    print("   1. Esquina SUPERIOR IZQUIERDA → presiona Enter")
    input()
    x1, y1 = pyautogui.position()
    print(f"      Superior izquierda: ({x1}, {y1})")

    print("   2. Esquina INFERIOR DERECHA → presiona Enter")
    input()
    x2, y2 = pyautogui.position()
    print(f"      Inferior derecha: ({x2}, {y2})")

    width = x2 - x1
    height = y2 - y1
    if width <= 0 or height <= 0:
        print("      ¡Error! La región tiene dimensiones inválidas. Intenta de nuevo.")
        return get_region(name, description)
    region = [x1, y1, width, height]
    print(f"      Región calculada: {region}")
    return region

def get_point(name, description):
    print(f"\n→ Calibrando: {name}")
    print(f"   {description}")
    print("   Mueve el mouse EXACTAMENTE al centro del elemento → presiona Enter")
    input()
    x, y = pyautogui.position()
    print(f"      Posición: ({x}, {y})")
    return [x, y]

# === CALIBRACIÓN DE REGIONES EN ORDEN LÓGICO ===
print("\n=== CALIBRANDO REGIONES CRÍTICAS PARA OCR ===")
config['regions']['hp_bar'] = get_region(
    "Barra de HP",
    "Solo el área del porcentaje o número de HP (ej: '85%'). Ajusta muy cerca del texto."
)
config['regions']['mana_bar'] = get_region(
    "Barra de Mana",
    "Solo el área del porcentaje o número de Mana (ej: '90%'). Ajusta muy cerca del texto."
)
config['regions']['battle_list'] = get_region(
    "Battle List",
    "El área completa de la battle list donde aparecen nombres de enemigos."
)

print("\n=== CALIBRANDO REGIONES DE MINIMAPA ===")
config['regions']['minimap'] = get_region(
    "Minimap completo",
    "Todo el cuadro del minimapa, incluyendo el área de coordenadas."
)
config['regions']['minimap_coords_text'] = get_region(
    "Texto de coordenadas (x,y,z)",
    "SOLO el texto de coordenadas en el minimapa (ej: '32560,32488,7'). ¡MUY IMPORTANTE! Ajusta justo alrededor del texto."
)
config['regions']['player_dot'] = get_point(
    "Punto blanco del jugador",
    "EXACTAMENTE el centro del punto blanco que representa al jugador en el minimapa."
)

print("\n=== CALIBRANDO REGIONES OPCIONALES ===")
config['regions']['corpse_area'] = get_region(
    "Área de cadáveres",
    "El área central de la pantalla donde aparecen los cadáveres abiertos."
)
config['regions']['level_up_button'] = get_region(
    "Botón de Level Up",
    "El botón que aparece en la interfaz cuando subes de nivel."
)
config['regions']['inventory_slots'] = {
    "ring": get_region("Slot de anillo", "El slot del inventario donde va el anillo."),
    "amulet": get_region("Slot de amuleto", "El slot del inventario donde va el amuleto."),
    "weapon": get_region("Slot de arma", "El slot del inventario donde va el arma."),
    "shield": get_region("Slot de escudo", "El slot del inventario donde va el escudo.")
}

# === CALCULAR OFFSET DEL CENTRO DEL MINIMAPA ===
minimap = config['regions']['minimap']
config['minimap_center_offset'] = [minimap[2] // 2, minimap[3] // 2]

# === MANTENER CONFIGURACIÓN EXISTENTE ===
# Preservar claves importantes que no se recalibran
default_config = {
    "window_region": [0, 0, 1920, 1080],
    "hp_bar_region_primary": [320, 85, 280, 22],
    "mp_bar_region_primary": [320, 112, 280, 22],
    "hp_bar_region_secondary": [1565, 780, 200, 16],
    "mp_bar_region_secondary": [1565, 802, 200, 16],
    "player_dot_color": [255, 255, 255],
    "player_dot_tolerance": 30,
    "level_text_color_threshold": 200,
    "base_position": {"x": 32560, "y": 32488, "z": 7},
    "arrival_tolerance": 1,
    "waypoints_file": "waypoints/newhaven_exp.json",
    "hp_threshold": 75,
    "mp_threshold": 40,
    "strong_heal_below": 45,
    "use_mana_potion": True,
    "eat_food_threshold": 50,
    "logout_threshold_level": 3,
    "inventory_region": [1550, 600, 350, 400],
    "loot_delay": 1.8,
    "auto_bank": True,
    "bank_npc": "supplier",
    "bank_dialog": ["hi", "deposit all", "yes"],
    "dialog_delay": 1.5,
    "auto_equip": True,
    "equip_check_interval": 300,
    "quick_loot": True,
    "quick_loot_mode": "premium",
    "quick_loot_hotkey": "alt",
    "quick_loot_priority": [
        "gold coin", "platinum coin", "mana potion",
        "strong health potion", "ultimate health potion", "rare item"
    ],
    "auto_level_up": True,
    "skill_priority": {
        "melee": 80,
        "distance": 0,
        "magic": 20,
        "shielding": 70
    },
    "hotkeys": {
        "heal_spell_light": "f1",
        "heal_spell_strong": "f2",
        "uh_hotkey": "f3",
        "mana_potion": "f4",
        "attack_spell_default": "f5",
        "use_rope": "f6",
        "use_shovel": "f7",
        "eat_food": "f8",
        "attack": "f1",
        "equip_ring": "f5",
        "talk_hi": "enter",
        "logout": "ctrl+q",
        "enter_chat": "enter"
    },
    "equip_hotkeys": {
        "ring": "f10",
        "amulet": "f11",
        "weapon": "f12",
        "shield": "f13"
    },
    "skill_hotkeys": {
        "melee": "f9",
        "distance": "f10",
        "magic": "f11",
        "shielding": "f12"
    },
    "monster_priority": ["muglex_assassin", "muglex_footman"],
    "npcs": {
        "gustavo": {
            "name": "Gustavo",
            "position": [32560, 32488, 7],
            "dialog": ["hi", "mission", "yes"]
        },
        "viola": {
            "name": "Viola",
            "position": [32571, 32507, 7],
            "dialog": ["hi", "mission", "yes", "book"]
        },
        "supplier": {
            "name": "Supplier",
            "position": [32565, 32485, 7],
            "dialog": ["hi", "trade"],
            "buy": {
                "mana potion": 50,
                "strong health potion": 20,
                "ultimate health potion": 10
            }
        }
    },
    "ocr_config": "--psm 7 -c tessedit_char_whitelist=0123456789.%",
    "expected_colors": {
        "hp_low": [255, 0, 0],
        "mana_low": [0, 0, 255],
        "arrow_present": [255, 255, 255]
    },
    "arrow_pos": [120, 60]
}

# Fusionar configuración existente con la nueva
for key, value in default_config.items():
    if key not in config or key == 'regions':
        config[key] = value
    elif isinstance(value, dict) and key in config:
        config[key].update(value)

# === GUARDAR CONFIG ORDENADA ===
ordered_keys = [
    "window_region", "hp_bar_region_primary", "mp_bar_region_primary",
    "hp_bar_region_secondary", "mp_bar_region_secondary",
    "minimap_region", "minimap_center_offset", "player_dot_color", "player_dot_tolerance",
    "level_region", "level_text_color_threshold", "base_position", "arrival_tolerance",
    "waypoints_file", "hp_threshold", "mp_threshold", "strong_heal_below",
    "use_mana_potion", "eat_food_threshold", "logout_threshold_level",
    "inventory_region", "loot_delay", "auto_bank", "bank_npc", "bank_dialog",
    "dialog_delay", "auto_equip", "equip_check_interval", "quick_loot",
    "quick_loot_mode", "quick_loot_hotkey", "quick_loot_priority", "auto_level_up",
    "skill_priority", "hotkeys", "equip_hotkeys", "skill_hotkeys",
    "monster_priority", "npcs", "ocr_config", "expected_colors", "arrow_pos",
    "regions"
]

ordered_config = {}
for key in ordered_keys:
    if key in config:
        ordered_config[key] = config[key]

for key, value in config.items():
    if key not in ordered_keys:
        ordered_config[key] = value

with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(ordered_config, f, indent=4, ensure_ascii=False)

print("\n\n¡CALIBRACIÓN COMPLETA!")
print("→ config.json actualizado con regiones optimizadas para OCR.")
print(f"→ Backup guardado: {BACKUP_PATH}")
print("\nEjecuta 'python main.py' para probar el bot.")
print("Si el OCR sigue fallando, verifica que las regiones sean precisas y que Tibia esté en modo ventana.")