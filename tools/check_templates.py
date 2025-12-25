# tools/check_templates.py
import json
import os
from typing import Any, List, Set

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG_PATH = os.path.join(ROOT, "config.json")

IMG_EXTS = (".png", ".jpg", ".jpeg", ".npy")


def collect_paths(obj: Any, out: List[str]) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            collect_paths(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_paths(v, out)
    elif isinstance(obj, str):
        if obj.lower().endswith(IMG_EXTS):
            out.append(obj)


def main() -> int:
    if not os.path.exists(CONFIG_PATH):
        print(f"[ERROR] No existe {CONFIG_PATH}")
        return 1

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    paths: List[str] = []
    collect_paths(cfg, paths)

    unique: Set[str] = set(paths)
    missing = []
    for p in sorted(unique):
        full = os.path.join(ROOT, p)
        if not os.path.exists(full):
            missing.append(p)

    print("===================================================")
    print("AUDITORÍA DE TEMPLATES (config.json)")
    print("===================================================")
    print(f"Total referenciados: {len(unique)}")
    print(f"Faltan: {len(missing)}")
    print("---------------------------------------------------")
    for p in missing:
        print(f"[MISSING] {p}")

    return 0 if not missing else 2


if __name__ == "__main__":
    raise SystemExit(main())
