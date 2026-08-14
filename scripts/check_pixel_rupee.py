#!/usr/bin/env python3
"""Block releases that lose the reviewed Pixel Indian rupee design."""

from __future__ import annotations

import argparse
from pathlib import Path

import glyphsLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont


CODEPOINT = 0x20B9
GLYPH_NAME = "rupeeIndian"
EXPECTED_WIDTH = 646
EXPECTED_COMPONENTS = 109
GRID_UNIT = 38
STYLES = ("Circle", "Grid", "Line", "Square", "Triangle")


def validate_source(path: Path) -> list[str]:
    errors: list[str] = []
    source = glyphsLib.load(path)
    glyph = source.glyphs[GLYPH_NAME]
    if glyph is None:
        return [f"{path}: missing {GLYPH_NAME}"]
    if (glyph.unicode or "").upper() != f"{CODEPOINT:04X}":
        errors.append(f"{path}: {GLYPH_NAME} has Unicode {glyph.unicode!r}")
    if not glyph.export:
        errors.append(f"{path}: {GLYPH_NAME} must export")
    layer = glyph.layers["m01"]
    if layer is None:
        return errors + [f"{path}: {GLYPH_NAME} is missing master layer m01"]
    if round(layer.width) != EXPECTED_WIDTH:
        errors.append(
            f"{path}: {GLYPH_NAME} width is {layer.width}, expected {EXPECTED_WIDTH}"
        )
    components = list(layer.components)
    if len(components) != EXPECTED_COMPONENTS:
        errors.append(
            f"{path}: {GLYPH_NAME} has {len(components)} components, "
            f"expected {EXPECTED_COMPONENTS}"
        )
    if len(components) != len(layer.shapes):
        errors.append(f"{path}: {GLYPH_NAME} may contain only pixel components")
    positions = []
    for component in components:
        x, y = map(round, component.position)
        positions.append((x, y))
        if component.name != "pixel":
            errors.append(f"{path}: unexpected component {component.name!r}")
        if x % GRID_UNIT or y % GRID_UNIT:
            errors.append(f"{path}: off-grid component at {(x, y)}")
    if len(positions) != len(set(positions)):
        errors.append(f"{path}: duplicate pixel components")
    return errors


def validate_font(path: Path, *, expect_static: bool = True) -> list[str]:
    errors: list[str] = []
    font = TTFont(path, recalcTimestamp=False)
    try:
        glyph_name = (font.getBestCmap() or {}).get(CODEPOINT)
        if glyph_name is None:
            return [f"{path}: missing U+20B9 ₹"]
        width, _ = font["hmtx"][glyph_name]
        if width != EXPECTED_WIDTH:
            errors.append(
                f"{path}: U+20B9 has width {width}, expected {EXPECTED_WIDTH}"
            )
        pen = BoundsPen(font.getGlyphSet())
        font.getGlyphSet()[glyph_name].draw(pen)
        if pen.bounds is None:
            errors.append(f"{path}: U+20B9 must contain ink")
        else:
            x_min, y_min, x_max, y_max = pen.bounds
            if x_min < 0 or x_max > width or y_min < 0 or y_max > 722:
                errors.append(f"{path}: U+20B9 bounds {pen.bounds} exceed its cell")
        if expect_static and "fvar" in font:
            errors.append(f"{path}: Pixel static unexpectedly contains fvar")
        if not expect_static and "fvar" not in font:
            errors.append(f"{path}: Pixel variable font is missing fvar")
    finally:
        font.close()
    return errors


def expected_fonts(root: Path) -> list[Path]:
    release = root / "fonts" / "NamcheShadowPixel"
    paths = [
        release / directory / f"NamcheShadowPixel-{style}.{suffix}"
        for directory, suffix in (("otf", "otf"), ("ttf", "ttf"), ("webfonts", "woff2"))
        for style in STYLES
    ]
    npm = root / "packages" / "next" / "dist" / "fonts" / "namche-shadow-pixel"
    paths.extend(npm / f"NamcheShadowPixel-{style}.woff2" for style in STYLES)
    return paths


def validate_release(root: Path) -> list[str]:
    source = root / "sources" / "NamcheShadowPixel.glyphspackage"
    errors = validate_source(source)
    for path in expected_fonts(root):
        if not path.is_file():
            errors.append(f"missing expected Pixel release font: {path}")
            continue
        errors.extend(validate_font(path))
    variable = (
        root
        / "fonts"
        / "NamcheShadowPixel"
        / "variable"
        / "NamcheShadowPixel[ELSH].ttf"
    )
    if not variable.is_file():
        errors.append(f"missing expected Pixel variable font: {variable}")
    else:
        errors.extend(validate_font(variable, expect_static=False))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = validate_release(args.root.resolve())
    if errors:
        print("Pixel Indian rupee validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Verified ₹ in the Pixel source, variable font, and 20 release/npm statics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
