# templates/gameWindow/config.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Tuple

import modules.utils as utils


def _images_root() -> Path:
    # .../templates/gameWindow/images
    return Path(__file__).resolve().parent / "images"


def _load_gray(p: Path):
    img = utils.loadFromRGBToGray(str(p))
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar template: {p}")
    return img


images_root = _images_root()
arrows_images_path = images_root / "arrows"
waypoints_images_path = images_root / "waypoints"

images: Dict[str, Any] = {
    "arrows": {
        "leftGameWindow00": _load_gray(arrows_images_path / "leftGameWindow00.png"),
        "leftGameWindow01": _load_gray(arrows_images_path / "leftGameWindow01.png"),
        "leftGameWindow10": _load_gray(arrows_images_path / "leftGameWindow10.png"),
        "leftGameWindow11": _load_gray(arrows_images_path / "leftGameWindow11.png"),
        "rightGameWindow00": _load_gray(arrows_images_path / "rightGameWindow00.png"),
        "rightGameWindow01": _load_gray(arrows_images_path / "rightGameWindow01.png"),
        "rightGameWindow10": _load_gray(arrows_images_path / "rightGameWindow10.png"),
        "rightGameWindow11": _load_gray(arrows_images_path / "rightGameWindow11.png"),
    },
    720: {
        "holeOpen": _load_gray(waypoints_images_path / "holeOpen720.png"),
    },
    1080: {
        "holeOpen": _load_gray(waypoints_images_path / "holeOpen1080.png"),
    },
}

arrowsImagesHashes: Dict[int, str] = {
    utils.hashit(images["arrows"]["leftGameWindow01"]): "leftGameWindow01",
    utils.hashit(images["arrows"]["leftGameWindow10"]): "leftGameWindow10",
    utils.hashit(images["arrows"]["leftGameWindow11"]): "leftGameWindow11",
    utils.hashit(images["arrows"]["leftGameWindow00"]): "leftGameWindow00",
    utils.hashit(images["arrows"]["rightGameWindow01"]): "rightGameWindow01",
    utils.hashit(images["arrows"]["rightGameWindow10"]): "rightGameWindow10",
    utils.hashit(images["arrows"]["rightGameWindow11"]): "rightGameWindow11",
    utils.hashit(images["arrows"]["rightGameWindow00"]): "rightGameWindow00",
}

# (width, height) del área del game window en pixels para cada resolución
gameWindowSizes: Dict[int, Tuple[int, int]] = {
    720: (480, 352),
    1080: (960, 704),
}

gameWindowCache = {
    "left": {"arrow": None, "position": None},
    "right": {"arrow": None, "position": None},
}
