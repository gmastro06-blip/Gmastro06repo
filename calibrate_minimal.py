# calibrate_minimal.py - Versión mínima para calibrar manualmente

import pyautogui
import json
import os
import shutil
from datetime import datetime

CONFIG_PATH = 'config.json'
BACKUP_PATH = f'config.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

print("\n" + "="*80)
print("🎄 CALIBRADOR MÍNIMO PARA TIBIABOT - NAVIDAD 2025 🎄")
print("="*80)
print("Calibración manual simple: solo mouse y Enter.")
input("Pulsa Enter para comenzar...")

if os.path.exists(CONFIG_PATH):
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
    print(f"Backup creado: {BACKUP_PATH}")

config = {}
config.setdefault('regions', {})
config.setdefault('hotkeys', {})
config.setdefault('base_position', {"x": 32560, "y": 32488, "z": 7})

def get_point(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    input("   Mueve mouse y pulsa Enter...")
    x, y = pyautogui.position()
    print(f"   Capturado: ({x}, {y})")
    return [x, y]

def get_region(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    input("   1. Esquina superior izquierda → Enter")
    x1, y1 = pyautogui.position()
    print(f"      ({x1}, {y1})")

    input("   2. Esquina inferior derecha → Enter")
    x2, y2 = pyautogui.position()
    print(f"      ({x2}, {y2})")

    w = x2 - x1
    h = y2 - y1
    if w <= 0 or h <= 0:
        print("   Región inválida. Reintenta.")
        return get_region(name, desc)

    region = [x1, y1, w, h]
    print(f"   Región final: {region}")
    return region

config['regions']['player_dot'] = get_point("Player Dot", "Centro del punto blanco en minimap")

config['regions']['minimap'] = get_region("Minimap completo", "Todo el cuadro del minimap")
config['minimap_center_offset'] = [config['regions']['minimap'][2] // 2, config['regions']['minimap'][3] // 2]

config['regions']['hp_bar'] = get_region("HP texto", "Solo el texto '180/180'")
config['regions']['mana_bar'] = get_region("Mana texto", "Solo el texto '75/75'")

config['regions']['battle_list'] = get_region("Battle List", "Columna de criaturas")
config['regions']['corpse_area'] = get_region("Corpse Area", "Centro donde caen cadáveres")

# Defaults
config.update({
    "arrival_tolerance": 1,
    "waypoints_file": "waypoints/newhaven_exp.json",
    "hotkeys": {"screenshot": "f12"}  # Asegúrate de configurar esto en Tibia
})

with open(CONFIG_PATH, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("\n¡Config guardada! Ejecuta python ui/tibiabot_gui.py")