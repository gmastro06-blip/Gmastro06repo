# templates/core.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

import modules.utils as utils


@dataclass(frozen=True)
class TemplateModulePaths:
    repo_root: Path
    templates_root: Path
    module_root: Path
    images_root: Path


def repo_root() -> Path:
    """
    .../TibiaBot (donde está config.json)
    templates/core.py => parents[1] = templates, parents[2] = repo (depende)
    Con tu estructura: .../TibiaBot/templates/core.py
    """
    return Path(__file__).resolve().parents[1]


def templates_root() -> Path:
    return repo_root() / "templates"


def module_paths(module_name: str) -> TemplateModulePaths:
    """
    module_name: 'actionBar', 'battleList', ...
    """
    root = repo_root()
    troot = root / "templates"
    mroot = troot / module_name
    iroot = mroot / "images"
    return TemplateModulePaths(
        repo_root=root,
        templates_root=troot,
        module_root=mroot,
        images_root=iroot,
    )


def load_gray(path: Path):
    img = utils.loadFromRGBToGray(str(path))
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar template: {path}")
    return img


def try_load_gray(path: Path):
    """
    Igual que load_gray, pero devuelve None si falta
    (útil para configs donde no quieres explotar si falta un PNG).
    """
    return utils.loadFromRGBToGray(str(path))


def hash_img(img) -> int:
    return utils.hashit(img)


def hash_gray(path: Path) -> int:
    return utils.hashit(load_gray(path))


def flatten_images_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Path]:
    """
    Convierte un dict anidado {k: Path | dict | ...} en { "a/b/c": Path }
    Útil para validación si modelas images como rutas.
    """
    out: Dict[str, Path] = {}
    for k, v in d.items():
        key = f"{prefix}/{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten_images_dict(v, key))
        elif isinstance(v, Path):
            out[key] = v
    return out
