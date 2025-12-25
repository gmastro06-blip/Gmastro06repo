# templates/battleList/config.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import numpy as np
import modules.utils as utils

# En tu repo existe templates/creatures.py (según tu screenshot)
# Ajusta el import si el nombre/estructura difiere.
from templates.creatures import creatures


def _images_root() -> Path:
    # .../templates/battleList/images
    return Path(__file__).resolve().parent / "images"


def _load_gray(p: Path):
    img = utils.loadFromRGBToGray(str(p))
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar template: {p}")
    return img


def _hash_gray(p: Path) -> int:
    return utils.hashit(_load_gray(p))


images_root = _images_root()
containers_path = images_root / "containers"
icons_path = images_root / "icons"
monsters_path = images_root / "monsters"
skulls_path = images_root / "skulls"

images: Dict[str, Any] = {
    "containers": {
        "bottomBar": _load_gray(containers_path / "bottomBar.png"),
    },
    "icons": {
        "ng_battleList": _load_gray(icons_path / "battleList.png"),
        "dust": _load_gray(icons_path / "dust.png"),
    },
    "skulls": {
        "black": _load_gray(skulls_path / "black.png"),
        "green": _load_gray(skulls_path / "green.png"),
        "orange": _load_gray(skulls_path / "orange.png"),
        "red": _load_gray(skulls_path / "red.png"),
        "white": _load_gray(skulls_path / "white.png"),
        "yellow": _load_gray(skulls_path / "yellow.png"),
    },
}

# Hashes de nombres de criaturas (para reconocer en battle list)
creaturesNamesImagesHashes: Dict[int, str] = {}

for creatureName in creatures:
    p = monsters_path / f"{creatureName}.png"
    creature_img = utils.loadFromRGBToGray(str(p))
    if creature_img is None:
        # No reventar si falta uno: simplemente ignorar
        # (esto es útil si tu lista de creatures es más grande que tus PNG)
        continue

    # Igual que tu lógica original:
    # recorta una “franja” donde está el texto del nombre
    strip = creature_img[8:9, 0:115]
    strip = np.ravel(strip)

    creaturesNamesImagesHashes[utils.hashit(strip)] = creatureName


# Hashes de cooldown base (si los usas en battlelist, opcional)
hashes: Dict[str, Any] = {
    # ejemplo: si luego quieres hashear algo de battlelist
}
