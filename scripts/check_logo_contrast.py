#!/usr/bin/env python3
"""Detect logo assets that need a dark presentation background.

The viewer renders logos on a light card by default. This check looks at
opaque raster pixels or explicit SVG colors and marks light-only logos with
``"dark": true`` in logos.json. Run it after adding or refreshing assets:

    python3 scripts/check_logo_contrast.py --write

Use the default check mode to review suggestions without changing the
manifest. Raster analysis uses Pillow when available; SVG analysis needs only
the Python standard library.
"""

import argparse
import json
import re
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "logos.json"
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
NAMED = re.compile(r"(?:fill|stroke)\s*=\s*[\"'](white|black|red|blue|green|orange)[\"']", re.I)
NAMED_RGB = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "green": (0, 128, 0),
    "orange": (255, 165, 0),
}


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hex_rgb(value):
    raw = value[1:]
    if len(raw) in (3, 4):
        raw = "".join(ch * 2 for ch in raw[:3])
    elif len(raw) == 8:
        raw = raw[:6]
    if len(raw) != 6:
        return None
    return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))


def svg_needs_dark(path):
    text = path.read_text(errors="ignore")
    colors = [rgb for value in HEX.findall(text) if (rgb := hex_rgb(value))]
    colors.extend(NAMED_RGB[value.lower()] for value in NAMED.findall(text))
    if not colors:
        return False
    light = sum(luminance(rgb) >= 225 for rgb in colors)
    dark = sum(luminance(rgb) < 100 for rgb in colors)
    return light > 0 and dark == 0


def raster_needs_dark(path):
    try:
        from PIL import Image
    except ImportError:
        return False
    try:
        image = Image.open(path).convert("RGBA")
    except Exception:
        return False
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        pixels = [pixel for pixel in image.getdata() if pixel[3] >= 32]
    if not pixels:
        return False
    if not any(pixel[3] < 250 for pixel in pixels):
        return False
    bright = sum(luminance(pixel[:3]) >= 225 for pixel in pixels) / len(pixels)
    dark = sum(luminance(pixel[:3]) < 100 for pixel in pixels) / len(pixels)
    mean = sum(luminance(pixel[:3]) for pixel in pixels) / len(pixels)
    return bright >= 0.72 and dark < 0.08 and mean >= 190


def needs_dark(path):
    return svg_needs_dark(path) if path.suffix.lower() == ".svg" else raster_needs_dark(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write detected dark flags into logos.json")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    changed = False
    for name, entry in manifest.items():
        if not entry.get("path"):
            print(f"{name}: unresolved ({entry.get('reason', 'no asset path')})")
            continue
        path = ROOT / entry["path"]
        detected = needs_dark(path)
        previous = entry.get("dark", False)
        print(f"{name}: dark={'yes' if detected else 'no'} (manifest={'yes' if previous else 'no'})")
        if args.write and previous != detected:
            if detected:
                entry["dark"] = True
            else:
                entry.pop("dark", None)
            changed = True
    if args.write and changed:
        MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        print(f"Updated {MANIFEST}")


if __name__ == "__main__":
    main()
