# templates/inventory/config.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import modules.utils as utils


def _images_root() -> Path:
    # .../templates/inventory/images
    return Path(__file__).resolve().parent / "images"


def _load_gray(p: Path):
    img = utils.loadFromRGBToGray(str(p))
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar template: {p}")
    return img


def _hash_img(img) -> int:
    return utils.hashit(img)


images_root = _images_root()
containers_bars_path = images_root / "containersBars"
slots_path = images_root / "slots"

images: Dict[str, Any] = {
    "containersBars": {
        "backpack bottom": _load_gray(containers_bars_path / "backpack bottom.png"),
        "25 Years Backpack": _load_gray(containers_bars_path / "25 Years Backpack.png"),
        "Anniversary Backpack": _load_gray(containers_bars_path / "Anniversary Backpack.png"),
        "Beach Backpack": _load_gray(containers_bars_path / "Beach Backpack.png"),
        "Birthday Backpack": _load_gray(containers_bars_path / "Birthday Backpack.png"),
        "Brocade Backpack": _load_gray(containers_bars_path / "Brocade Backpack.png"),
        "Buggy Backpack": _load_gray(containers_bars_path / "Buggy Backpack.png"),
        "Cake Backpack": _load_gray(containers_bars_path / "Cake Backpack.png"),
        "Camouflage Backpack": _load_gray(containers_bars_path / "Camouflage Backpack.png"),
        "Crown Backpack": _load_gray(containers_bars_path / "Crown Backpack.png"),
        "Crystal Backpack": _load_gray(containers_bars_path / "Crystal Backpack.png"),
        "Deepling Backpack": _load_gray(containers_bars_path / "Deepling Backpack.png"),
        "Demon Backpack": _load_gray(containers_bars_path / "Demon Backpack.png"),
        "Dragon Backpack": _load_gray(containers_bars_path / "Dragon Backpack.png"),
        "Expedition Backpack": _load_gray(containers_bars_path / "Expedition Backpack.png"),
        "Fur Backpack": _load_gray(containers_bars_path / "Fur Backpack.png"),
        "Glooth Backpack": _load_gray(containers_bars_path / "Glooth Backpack.png"),
        "Heart Backpack": _load_gray(containers_bars_path / "Heart Backpack.png"),
        "locker": _load_gray(containers_bars_path / "locker.png"),
        "Minotaur Backpack": _load_gray(containers_bars_path / "Minotaur Backpack.png"),
        "Moon Backpack": _load_gray(containers_bars_path / "Moon Backpack.png"),
        "Mushroom Backpack": _load_gray(containers_bars_path / "Mushroom Backpack.png"),
        "Pannier Backpack": _load_gray(containers_bars_path / "Pannier Backpack.png"),
        "Pirate Backpack": _load_gray(containers_bars_path / "Pirate Backpack.png"),
        "Raccoon Backpack": _load_gray(containers_bars_path / "Raccoon Backpack.png"),
        "Santa Backpack": _load_gray(containers_bars_path / "Santa Backpack.png"),
        "Wolf Backpack": _load_gray(containers_bars_path / "Wolf Backpack.png"),
    },
    "slots": {
        "25 Years Backpack": _load_gray(slots_path / "25 Years Backpack.png"),
        "Anniversary Backpack": _load_gray(slots_path / "Anniversary Backpack.png"),
        "Beach Backpack": _load_gray(slots_path / "Beach Backpack.png"),
        "big empty potion flask": _load_gray(slots_path / "big empty potion flask.png"),
        "Birthday Backpack": _load_gray(slots_path / "Birthday Backpack.png"),
        "Brocade Backpack": _load_gray(slots_path / "Brocade Backpack.png"),
        "Buggy Backpack": _load_gray(slots_path / "Buggy Backpack.png"),
        "Camouflage Backpack": _load_gray(slots_path / "Camouflage Backpack.png"),
        "Crown Backpack": _load_gray(slots_path / "Crown Backpack.png"),
        "Crystal Backpack": _load_gray(slots_path / "Crystal Backpack.png"),
        "Deepling Backpack": _load_gray(slots_path / "Deepling Backpack.png"),
        "Demon Backpack": _load_gray(slots_path / "Demon Backpack.png"),
        "depot": _load_gray(slots_path / "depot.png"),
        "depot chest 1": _load_gray(slots_path / "depot chest 1.png"),
        "depot chest 2": _load_gray(slots_path / "depot chest 2.png"),
        "depot chest 3": _load_gray(slots_path / "depot chest 3.png"),
        "depot chest 4": _load_gray(slots_path / "depot chest 4.png"),
        "Dragon Backpack": _load_gray(slots_path / "Dragon Backpack.png"),
        "empty": _load_gray(slots_path / "empty.png"),
        "Expedition Backpack": _load_gray(slots_path / "Expedition Backpack.png"),
        "Fur Backpack": _load_gray(slots_path / "Fur Backpack.png"),
        "Glooth Backpack": _load_gray(slots_path / "Glooth Backpack.png"),
        "Heart Backpack": _load_gray(slots_path / "Heart Backpack.png"),
        "medium empty potion flask": _load_gray(slots_path / "medium empty potion flask.png"),
        "Minotaur Backpack": _load_gray(slots_path / "Minotaur Backpack.png"),
        "Moon Backpack": _load_gray(slots_path / "Moon Backpack.png"),
        "Mushroom Backpack": _load_gray(slots_path / "Mushroom Backpack.png"),
        "Pannier Backpack": _load_gray(slots_path / "Pannier Backpack.png"),
        "Pirate Backpack": _load_gray(slots_path / "Pirate Backpack.png"),
        "Raccoon Backpack": _load_gray(slots_path / "Raccoon Backpack.png"),
        "Santa Backpack": _load_gray(slots_path / "Santa Backpack.png"),
        "small empty potion flask": _load_gray(slots_path / "small empty potion flask.png"),
        "stash": _load_gray(slots_path / "stash.png"),
        "Wolf Backpack": _load_gray(slots_path / "Wolf Backpack.png"),
    },
}

slotsImagesHashes: Dict[int, str] = {
    _hash_img(images["slots"]["big empty potion flask"]): "empty potion flask",
    _hash_img(images["slots"]["medium empty potion flask"]): "empty potion flask",
    _hash_img(images["slots"]["small empty potion flask"]): "empty potion flask",
    _hash_img(images["slots"]["empty"]): "empty slot",
}
