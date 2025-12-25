# tests/test_cavebot.py
import pytest
from modules.cavebot import Cavebot
from modules.utils import CONFIG

def test_cavebot_init():
    cavebot = Cavebot()
    assert len(cavebot.waypoints) >= 0
    cavebot.start()
    assert cavebot.running == True
    cavebot.stop()
    assert cavebot.running == False

def test_load_waypoints():
    cavebot = Cavebot()
    cavebot.reload_waypoints("waypoints/newhaven_exp.json")
    assert len(cavebot.waypoints) > 0