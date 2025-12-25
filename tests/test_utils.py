# tests/test_utils.py
import pytest
from modules.utils import random_delay, simulate_key_press, CONFIG

def test_random_delay():
    random_delay(0.1, 0.2)  # Asegura no crashea

def test_simulate_key_press():
    simulate_key_press("a")  # Asegura no crashea