#!/usr/bin/env python3
"""Block releases that lose Namche Shadow Pixel ligature caret positions."""

from __future__ import annotations

from pathlib import Path
import sys

from fontTools.ttLib import TTFont

if __package__:
    from .finalize_pixel_statics import (
        ligature_caret_coordinates,
        source_ligature_carets,
    )
else:
    from finalize_pixel_statics import (
        ligature_caret_coordinates,
        source_ligature_carets,
    )


STYLES = ("Circle", "Grid", "Line", "Square", "Triangle")


def validate_font(path: Path) -> list[str]:
    font = TTFont(path, lazy=True)
    errors = []
    try:
        expected = source_ligature_carets()
        for glyph_name, expected_coordinates in expected.items():
            if glyph_name not in font.getGlyphOrder():
                errors.append(f"{path}: missing {glyph_name} ligature glyph")
                continue
            actual = ligature_caret_coordinates(font, glyph_name)
            if actual != expected_coordinates:
                errors.append(
                    f"{path}: {glyph_name} caret coordinates {actual!r}; "
                    f"expected {expected_coordinates!r} from the Pixel source"
                )
                continue
            advance = font["hmtx"].metrics[glyph_name][0]
            if any(not 0 < coordinate < advance for coordinate in actual):
                errors.append(
                    f"{path}: {glyph_name} caret {actual!r} falls outside "
                    f"its {advance}-unit advance"
                )
    finally:
        font.close()
    return errors


def release_paths(root: Path) -> list[Path]:
    release = root / "fonts" / "NamcheShadowPixel"
    paths = [
        release / directory / f"NamcheShadowPixel-{style}.{suffix}"
        for style in STYLES
        for directory, suffix in (
            ("otf", "otf"),
            ("ttf", "ttf"),
            ("webfonts", "woff2"),
        )
    ]
    npm = root / "packages" / "next" / "dist" / "fonts" / "namche-shadow-pixel"
    paths.extend(npm / f"NamcheShadowPixel-{style}.woff2" for style in STYLES)
    return paths


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors = []
    paths = release_paths(root)
    for path in paths:
        if not path.exists():
            errors.append(f"missing expected Pixel release font: {path}")
            continue
        errors.extend(validate_font(path))
    if errors:
        print("Pixel ligature-caret validation failed:", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(
        "Verified all source-defined ligature caret positions in "
        f"{len(paths)} Pixel release and npm fonts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
