# tests/conftest.py
import pytest
import numpy as np
import cv2

@pytest.fixture
def mock_screen():
    # Imagen RGB 1920x1080 (fondo oscuro de Tibia)
    screen = np.zeros((1080, 1920, 3), dtype=np.uint8)
    screen[:] = [46, 46, 46]  # Color oscuro típico
    # Barra HP 50% (verde + rojo)
    screen[85:107, 320:460] = [0, 255, 0]  # Verde
    screen[85:107, 460:600] = [0, 0, 255]  # Rojo (baja)
    # Barra MP 70%
    screen[112:134, 320:530] = [255, 150, 0]  # Azul mana
    return screen

@pytest.fixture
def mock_gray_screen():
    return cv2.cvtColor(np.zeros((1080, 1920, 3), dtype=np.uint8), cv2.COLOR_BGR2GRAY)