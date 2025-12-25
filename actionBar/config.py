# templates/actionBar/config.py
from __future__ import annotations

from typing import Dict, Any, Tuple

from templates.core import module_paths, load_gray, hash_gray


paths = module_paths("actionBar")
arrows = paths.images_root / "arrows"
cooldowns = paths.images_root / "cooldowns"
digits = paths.images_root / "digits"

hashes: Dict[str, Any] = {
    "cooldowns": {
        hash_gray(cooldowns / "attack.png"): "attack",
        hash_gray(cooldowns / "healing.png"): "healing",
        hash_gray(cooldowns / "support.png"): "support",
    }
}

images: Dict[str, Any] = {
    "arrows": {
        "left": load_gray(arrows / "left.png"),
        "right": load_gray(arrows / "right.png"),
    },
    "cooldowns": {
        "attack": load_gray(cooldowns / "attack.png"),
        "healing": load_gray(cooldowns / "healing.png"),
        "support": load_gray(cooldowns / "support.png"),
    },
    "digits": {
        hash_gray(digits / "0.png"): 0,
        hash_gray(digits / "1.png"): 1,
        hash_gray(digits / "2.png"): 2,
        hash_gray(digits / "3.png"): 3,
        hash_gray(digits / "4.png"): 4,
        hash_gray(digits / "5.png"): 5,
        hash_gray(digits / "6.png"): 6,
        hash_gray(digits / "7.png"): 7,
        hash_gray(digits / "8.png"): 8,
        hash_gray(digits / "9.png"): 9,
    },
}
