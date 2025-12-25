# templates/gameWindow/core.py
from __future__ import annotations

from typing import Tuple, Union

import numpy as np
import modules.utils as utils

from .config import arrowsImagesHashes, gameWindowCache, images


# Tipos básicos para no depender de src.shared.typings
BBox = Tuple[int, int, int, int]          # (x1, y1, x2, y2) en locate (tu utils.locate devuelve esto)
Coordinate = Tuple[int, int]              # (x, y)
GrayImage = np.ndarray
Slot = Tuple[int, int]                    # (slotX, slotY)


def getLeftArrowPosition(screenshot: GrayImage) -> Union[BBox, None]:
    global gameWindowCache

    if gameWindowCache["left"]["position"] is not None:
        left_arrow_img = images["arrows"][gameWindowCache["left"]["arrow"]]
        left_hash = utils.hashit(left_arrow_img)
        if arrowsImagesHashes.get(left_hash) is not None:
            return gameWindowCache["left"]["position"]

    for key in ["leftGameWindow01", "leftGameWindow11", "leftGameWindow10", "leftGameWindow00"]:
        pos = utils.locate(screenshot, images["arrows"][key], confidence=0.95)
        if pos is not None:
            gameWindowCache["left"]["arrow"] = key
            gameWindowCache["left"]["position"] = pos
            return pos

    return None


def getRightArrowPosition(screenshot: GrayImage) -> Union[BBox, None]:
    global gameWindowCache

    if gameWindowCache["right"]["position"] is not None:
        right_arrow_img = images["arrows"][gameWindowCache["right"]["arrow"]]
        right_hash = utils.hashit(right_arrow_img)
        if arrowsImagesHashes.get(right_hash) is not None:
            return gameWindowCache["right"]["position"]

    for key in ["rightGameWindow01", "rightGameWindow11", "rightGameWindow10", "rightGameWindow00"]:
        pos = utils.locate(screenshot, images["arrows"][key], confidence=0.95)
        if pos is not None:
            gameWindowCache["right"]["arrow"] = key
            gameWindowCache["right"]["position"] = pos
            return pos

    return None


def getCoordinate(screenshot: GrayImage, gameWindowSize: Tuple[int, int]) -> Union[BBox, None]:
    """
    Retorna el bbox (x, y, w, h) del game window completo.
    OJO: tu locate devuelve (x1,y1,x2,y2), pero aquí la función original
    devuelve (x,y,width,height). Mantenemos el contrato original del snippet.
    """
    left_pos = getLeftArrowPosition(screenshot)
    if left_pos is None:
        return None
    right_pos = getRightArrowPosition(screenshot)
    if right_pos is None:
        return None

    # Mantengo tu fórmula tal cual:
    x = ((left_pos[0] + 7 + right_pos[0]) // 2) - 480
    y = left_pos[1] + 5
    return (x, y, gameWindowSize[0], gameWindowSize[1])


def getImageByCoordinate(screenshot: GrayImage, coordinate: Tuple[int, int, int, int], gameWindowSize: Tuple[int, int]) -> GrayImage:
    x, y, _, _ = coordinate
    return screenshot[y:y + gameWindowSize[1], x:x + gameWindowSize[0]]


def getSlotFromCoordinate(currentCoordinate: Coordinate, coordinate: Coordinate) -> Union[Slot, None]:
    diffX = coordinate[0] - currentCoordinate[0]
    if abs(diffX) > 7:
        return None
    diffY = coordinate[1] - currentCoordinate[1]
    if abs(diffY) > 5:
        return None
    return (7 + diffX, 5 + diffY)


def getSlotImage(gameWindowImage: GrayImage, slot: Slot, slotWidth: int) -> GrayImage:
    x = slot[0] * slotWidth
    y = slot[1] * slotWidth
    return gameWindowImage[y:y + slotWidth, x:x + slotWidth]


def isHoleOpen(
    gameWindowImage: GrayImage,
    holeOpenImage: GrayImage,
    coordinate: Coordinate,
    targetCoordinate: Coordinate
) -> bool:
    # slotWidth = ancho de cada sqm (15 columnas)
    slotWidth = len(gameWindowImage[1]) // 15
    slot = getSlotFromCoordinate(coordinate, targetCoordinate)
    if slot is None:
        return False

    slotImage = getSlotImage(gameWindowImage, slot, slotWidth)
    return utils.locate(slotImage, holeOpenImage, confidence=0.8) is not None
