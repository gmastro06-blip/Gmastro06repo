# Ruta: calibrate.py - Calibrador para Tibia oficial (sin coordenadas visibles)

import pyautogui
import json
import os
import shutil
from datetime import datetime

CONFIG_PATH = 'config.json'
BACKUP_PATH = f'config.json.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

print("=== CALIBRADOR PARA TIBIA OFICIAL v15.20 (sin coordenadas visibles) ===")
print("Abre Tibia en modo ventana.")
print("Usaremos el punto blanco del jugador (player_dot) como posición principal.")
print("Mueve el mouse con precisión y presiona Enter.\n")
input("Presiona Enter para comenzar...")

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"Config cargado. Backup: {BACKUP_PATH}")
    shutil.copy(CONFIG_PATH, BACKUP_PATH)
else:
    print("Creando nuevo config.json")
    config = {}

if 'regions' not in config:
    config['regions'] = {}

def get_region(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    print("   1. Superior izquierda → Enter")
    input()
    x1, y1 = pyautogui.position()
    print(f"      ({x1}, {y1})")

    print("   2. Inferior derecha → Enter")
    input()
    x2, y2 = pyautogui.position()
    print(f"      ({x2}, {y2})")

    region = [x1, y1, x2 - x1, y2 - y1]
    print(f"      Región: {region}")
    return region

def get_point(name, desc):
    print(f"\n→ {name}")
    print(f"   {desc}")
    print("   Mouse en el centro → Enter")
    input()
    x, y = pyautogui.position()
    print(f"      ({x}, {y})")
    return [x, y]

# === CALIBRACIÓN ESENCIAL ===
config['regions']['hp_bar'] = get_region("Barra de HP", "Solo el porcentaje o número de HP")
config['regions']['mana_bar'] = get_region("Barra de Mana", "Solo el porcentaje o número de Mana")
config['regions']['battle_list'] = get_region("Battle List", "Toda la lista de criaturas")
config['regions']['minimap'] = get_region("Minimap completo", "Todo el cuadro del minimapa")
config['regions']['player_dot'] = get_point("Punto blanco del jugador", "CENTRO EXACTO del punto blanco en el minimapa (¡CRUCIAL!)")
config['regions']['corpse_area'] = get_region("Área de cadáveres", "Centro de pantalla donde aparecen cadáveres")

# Calcular offset del centro
minimap = config['regions']['minimap']
config['minimap_center_offset'] = [minimap[2] // 2, minimap[3] // 2]

# Guardar
with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print("\n\n¡CALIBRACIÓN COMPLETA!")
print("→ El bot usará el player_dot para posición (muy preciso en Tibia oficial).")
print("→ Ejecuta la GUI y START BOT.")