# Ruta: ui/tibiabot_gui.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import json
import os
import shutil
import threading
import time
import logging
from datetime import datetime
import sys

# Añadir la carpeta raíz del proyecto al path para poder importar main.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Ahora sí podemos importar desde main.py
try:
    from main import run_bot  # Asegúrate de que main.py tenga una función def run_bot(): o similar
except ImportError as e:
    print("Error al importar main.py:", e)
    print("Asegúrate de que main.py existe en la raíz del proyecto y tiene una función que inicia el bot.")
    # Fallback: función vacía para que la UI arranque aunque el bot no funcione
    def run_bot():
        logging.info("Bot no disponible - main.py no encontrado o sin función run_bot()")
        time.sleep(1)