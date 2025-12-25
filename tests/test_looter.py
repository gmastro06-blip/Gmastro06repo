# tests/test_looter.py
import pytest
from modules.looter import Looter
from modules.utils import CONFIG

def test_looter_init():
    looter = Looter()
    assert looter.running == True
    looter.stop()
    assert looter.running == False

def test_find_corpse():
    looter = Looter()
    assert looter.find_corpse(None) is None  # Asegura no crashea