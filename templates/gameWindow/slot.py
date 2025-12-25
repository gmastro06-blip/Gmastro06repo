# templates/gameWindow/slot.py
from __future__ import annotations

from typing import Tuple

import modules.utils as utils

BBox = Tuple[int, int, int, int]  # (x, y, w, h) en este archivo (ojo: distinto a locate)
Slot = Tuple[int, int]            # (slotX, slotY)


def getSlotPosition(slot: Slot, gameWindowPosition: BBox) -> Slot:
    """
    Convierte slot (grid) a coordenadas absolutas aproximadas dentro de la ventana.
    Mantiene la fórmula original (centrado +32).
    """
    (gw_x, gw_y, gw_w, gw_h) = gameWindowPosition
    (slotX, slotY) = slot

    slotHeight = gw_h // 11
    slotWidth = gw_w // 15

    slotXCoordinate = gw_x + (slotX * slotWidth)
    slotYCoordinate = gw_y + (slotY * slotHeight)

    return (slotXCoordinate + 32, slotYCoordinate + 32)


def moveToSlot(slot: Slot, gameWindowPosition: BBox):
    # No tenemos "moveTo" real en utils, pero podemos simular un click “suave” si lo necesitas.
    # Aquí lo dejamos como NO-OP: el proyecto actual no necesita mover sin click.
    return


def clickSlot(slot: Slot, gameWindowPosition: BBox):
    pos = getSlotPosition(slot, gameWindowPosition)
    utils.simulate_mouse_click(pos, button="left")


def rightClickSlot(slot: Slot, gameWindowPosition: BBox):
    pos = getSlotPosition(slot, gameWindowPosition)
    utils.simulate_mouse_click(pos, button="right")


def clickUseBySlot(slot: Slot, gameWindowPosition: BBox):
    xPos, yPos = getSlotPosition(slot, gameWindowPosition)
    utils.simulate_mouse_click((xPos + 15, yPos + 25), button="left")
