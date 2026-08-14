#!/usr/bin/env python3
"""Block releases that lose the reviewed Pixel Indian rupee design."""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path

import glyphsLib
from fontTools.pens.basePen import NullPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont


CODEPOINT = 0x20B9
GLYPH_NAME = "rupeeIndian"
EXPECTED_WIDTH = 646
EXPECTED_COMPONENTS = 109
GRID_UNIT = 38
STYLES = ("Circle", "Grid", "Line", "Square", "Triangle")
EXPECTED_POSITION_DIGEST = (
    "38f4e10146d6ed0f627b33c409f485d5d95072ae1103b93f866e33edc1b47a06"
)
EXPECTED_OUTLINE_DIGESTS = {
    ("cff", "Circle"): "080822327e2c6a8f8ba0fbf5fbd59d88d2be781063b10a46f724b43c53a965ca",
    ("cff", "Grid"): "0efe1fe09b61297ec6d059a36e99a0d79409f3c2b45d74ff9847d98c13e83f99",
    ("cff", "Line"): "5161427ea65d9b74270e3fc513f9559d6abe1805953861582bf66bddbbefbc4d",
    ("cff", "Square"): "9b85e9c7bfde36ab8bceb7d20f5e1bed330081189b8a6c9221363c78c3ab4de5",
    ("cff", "Triangle"): "8568851b4a2083f2ab09af5b6d5f89df3b3298451d704477e5d5efa9bfbb93ca",
    ("truetype", "Circle"): "2e98a45f877a885ebc1c571d9763424020fca36a59ff81b152544e7c9a5e0d78",
    ("truetype", "Grid"): "bd281252e955b4862fc1bca0c96169946f48472a2efb73d315aca4a658e2c86d",
    ("truetype", "Line"): "65338e5ee12d8eda5d62de573d5ebe08806e26665935f48f0f4278c8e8019ed7",
    ("truetype", "Square"): "fbba015f303f2911810fd66d5a075a9ebf4bde8874b85a2036b9d3ef4fae31a7",
    ("truetype", "Triangle"): "ad329e0c6fc839e72269bb8ae1c50e98cbc0b3c6f627124e2887c511afc70192",
}


def digest(value: object) -> str:
    return sha256(repr(value).encode()).hexdigest()


def normalize_recording_value(value: object) -> object:
    if isinstance(value, (int, float)):
        rounded = round(value)
        return int(rounded) if abs(value - rounded) < 1e-6 else round(value, 6)
    if isinstance(value, (list, tuple)):
        return tuple(normalize_recording_value(item) for item in value)
    return value


def canonical_outline(recording: list[tuple[str, tuple]]) -> tuple:
    """Ignore contour serialization order while preserving exact geometry."""
    contours: list[tuple] = []
    current: list[tuple] = []
    for operation, arguments in recording:
        if operation == "moveTo" and current:
            contours.append(tuple(current))
            current = []
        current.append((operation, normalize_recording_value(arguments)))
        if operation in {"closePath", "endPath"}:
            contours.append(tuple(current))
            current = []
    if current:
        contours.append(tuple(current))
    return tuple(sorted(contours, key=repr))


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
    if digest(tuple(sorted(positions))) != EXPECTED_POSITION_DIGEST:
        errors.append(f"{path}: {GLYPH_NAME} component positions changed")
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
        if "CFF " in font:
            charstring = font["CFF "].cff.topDictIndex[0].CharStrings[glyph_name]
            charstring.draw(NullPen())
            if round(charstring.width) != width:
                errors.append(
                    f"{path}: U+20B9 CFF width is {charstring.width}, "
                    f"but hmtx width is {width}"
                )
        pen = BoundsPen(font.getGlyphSet())
        font.getGlyphSet()[glyph_name].draw(pen)
        if pen.bounds is None:
            errors.append(f"{path}: U+20B9 must contain ink")
        else:
            x_min, y_min, x_max, y_max = pen.bounds
            if x_min < 0 or x_max > width or y_min < 0 or y_max > 722:
                errors.append(f"{path}: U+20B9 bounds {pen.bounds} exceed its cell")
        if expect_static:
            style = next((style for style in STYLES if f"-{style}." in path.name), None)
            outline_kind = "cff" if "CFF " in font else "truetype"
            if style is None:
                errors.append(f"{path}: cannot identify Pixel style from filename")
            else:
                recording = RecordingPen()
                font.getGlyphSet()[glyph_name].draw(recording)
                actual_digest = digest(canonical_outline(recording.value))
                expected_digest = EXPECTED_OUTLINE_DIGESTS[(outline_kind, style)]
                if actual_digest != expected_digest:
                    errors.append(
                        f"{path}: U+20B9 {style} {outline_kind} outline changed"
                    )
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
