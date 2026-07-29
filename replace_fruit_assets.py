from __future__ import annotations

import json
import time
from typing import Tuple
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Pillow is required. Install it with: python -m pip install pillow") from exc

BASE = Path(r"d:\Metanova\GameDev\01_Game\watermelon-fruit\Watermelon Fruit 2048")
IMAGES = BASE / "images"

SOURCE = IMAGES / "metanova_logo.webp"
TARGETS = [
    (IMAGES / "drop_fruit-sheet1.webp", 129, 385, 91, 95),
    (IMAGES / "ingame_next_-sheet0.webp", 185, 257, 90, 90),
]

MARGIN_RATIO = 0.04


def fit_inside(src_size: Tuple[int, int], max_size: Tuple[int, int]) -> Tuple[int, int]:
    src_w, src_h = src_size
    max_w, max_h = max_size
    scale = min(max_w / src_w, max_h / src_h)
    fitted = (max(1, round(src_w * scale)), max(1, round(src_h * scale)))
    return fitted


def composite_target(sheet_path: Path, x: int, y: int, w: int, h: int) -> None:
    with Image.open(sheet_path).convert("RGBA") as sheet, Image.open(SOURCE).convert("RGBA") as source:
        safe_w = max(1, round(w * (1 - 2 * MARGIN_RATIO)))
        safe_h = max(1, round(h * (1 - 2 * MARGIN_RATIO)))
        paste_w, paste_h = fit_inside(source.size, (safe_w, safe_h))
        resized = source.resize((paste_w, paste_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ox = (w - paste_w) // 2
        oy = (h - paste_h) // 2
        canvas.alpha_composite(resized, (ox, oy))

        sheet.alpha_composite(canvas, (x, y))
        sheet.save(sheet_path, format="WEBP")


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source image: {SOURCE}")

    for target_path, x, y, w, h in TARGETS:
        if not target_path.exists():
            raise SystemExit(f"Missing target atlas: {target_path}")
        composite_target(target_path, x, y, w, h)

    offline_path = BASE / "offline.json"
    offline_data = json.loads(offline_path.read_text(encoding="utf-8"))
    offline_data["version"] = int(time.time() * 1000)
    offline_path.write_text(json.dumps(offline_data, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
