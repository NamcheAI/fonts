#!/usr/bin/env python3
"""Block releases that lose the inkless Pixel separator glyphs."""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


SEPARATORS = (0x2028, 0x2029)
SEPARATOR_WIDTH = 600
STYLES = ("Circle", "Grid", "Line", "Square", "Triangle")


def has_ink(font: TTFont, glyph_name: str) -> bool:
    pen = BoundsPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.bounds is not None


def validate_font(path: Path) -> list[str]:
    errors: list[str] = []
    font = TTFont(path, recalcTimestamp=False)
    try:
        cmap = font.getBestCmap() or {}
        for codepoint in SEPARATORS:
            label = f"U+{codepoint:04X}"
            glyph_name = cmap.get(codepoint)
            if glyph_name is None:
                errors.append(f"{path}: missing {label}")
                continue
            width, left_sidebearing = font["hmtx"][glyph_name]
            if (width, left_sidebearing) != (SEPARATOR_WIDTH, 0):
                errors.append(
                    f"{path}: {label} has metrics {(width, left_sidebearing)}, "
                    f"expected {(SEPARATOR_WIDTH, 0)}"
                )
            if has_ink(font, glyph_name):
                errors.append(f"{path}: {label} must remain inkless")
    finally:
        font.close()
    return errors


def expected_fonts(root: Path) -> list[Path]:
    release_root = root / "fonts" / "NamcheShadowPixel"
    paths = [
        release_root / directory / f"NamcheShadowPixel-{style}.{suffix}"
        for directory, suffix in (("otf", "otf"), ("ttf", "ttf"), ("webfonts", "woff2"))
        for style in STYLES
    ]
    paths.extend(
        root
        / "packages"
        / "next"
        / "dist"
        / "fonts"
        / "namche-shadow-pixel"
        / f"NamcheShadowPixel-{style}.woff2"
        for style in STYLES
    )
    return paths


def validate_release(root: Path) -> list[str]:
    errors: list[str] = []
    for path in expected_fonts(root):
        if not path.is_file():
            errors.append(f"missing expected Pixel release font: {path}")
            continue
        errors.extend(validate_font(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = validate_release(args.root.resolve())
    if errors:
        print("Pixel separator validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Verified inkless U+2028/U+2029 in 20 Pixel release and npm fonts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
