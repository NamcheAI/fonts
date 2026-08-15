#!/usr/bin/env python3
"""Block Pixel dotted-circle and soft-dotted shaping regressions."""

from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import glyphsLib
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
import uharfbuzz as hb


CODEPOINT = 0x25CC
GLYPH_NAME = "dottedCircle"
EXPECTED_WIDTH = 570
EXPECTED_COMPONENTS = 16
EXPECTED_ANCHORS = {
    "bottom": (285, 0),
    "center": (285, 285),
    "ogonek": (532, 38),
    "top": (285, 532),
    "topright": (532, 532),
}
EXPECTED_POSITION_DIGEST = (
    "786c9a59a898307a3204f3d26e915726164683e32ef41504b9326a946baac525"
)
STYLES = ("Circle", "Grid", "Line", "Square", "Triangle")
REQUIRED_MARKS = (0x0301, 0x0302, 0x030C, 0x0304, 0x0303, 0x0300)
OPTIONAL_MARKS = (0x030B, 0x0307, 0x0306, 0x0308, 0x0312, 0x030A)
EXPECTED_OUTLINE_DIGESTS = {
    ("cff", "Circle"): "4be72a7030f23f0a2a7ba18ae3e0e60c42eff71fa4b54e14e33d1ac75f5deaad",
    ("cff", "Grid"): "316fade55c4740f66af814c429f11d0f3e93ac06236659324dba1e4fc401545d",
    ("cff", "Line"): "01952a47ff9972f26831582c0d3a34046969cbf4d185d3d900bfb26526063f6b",
    ("cff", "Square"): "c094dbda0bd56de319f17d7ebd235b667e086ed34afadf07a70a5edb9660dc2c",
    ("cff", "Triangle"): "5b059152cd19d4d72e83ce710442c152b1d40e17b4da4290683b4e878f71332c",
    ("truetype", "Circle"): "7ba7e52538d023c67671393f66bb5ede9b00a4d81b10d8ccdbabb71f1a3771bf",
    ("truetype", "Grid"): "600a6c8d0d5381d8c4e51de085c9bfb55f5ef80e38a592d592bd3366de71ea7b",
    ("truetype", "Line"): "d1094575320a5b4d3afcc0f19a6ee5163a787a88c157361a09ca5425e395059a",
    ("truetype", "Square"): "92b2ca04f104ce8be67b8a24d60a89f89e5a6e8bd6a711d4f0b15914a85fd973",
    ("truetype", "Triangle"): "ab97002bfaa6a9ede2b553dad69e69e490aac143579db5f572aa2b9c22ea72f6",
}
EXPECTED_VARIABLE_INSTANCES = {
    "Regular": (0.0, "2d5540e47495ffde07989bfd064602afe326b294f0c6287a74c493d70346c4f4"),
    "Square": (1.0, "2d5540e47495ffde07989bfd064602afe326b294f0c6287a74c493d70346c4f4"),
    "Circle": (20.0, "c96f6df0c7d76bb8d057e001df89c38bc465a761e9e6d87e47f80d0362659027"),
    "Grid": (40.0, "4fd27337262db88912a0dedfc3ca8774ab9b0fc5a58a5d4c1d1f1ee4b1a1e8af"),
    "Triangle": (60.0, "0b40cb519418195bce79a4f9ecf65f2bc3183d530597f9373609e3ce2d5b52ef"),
    "Line": (80.0, "06f280122be37804b548eaa51c45b26ae19d7ba529f73c8f3135040b01f2b75a"),
}


def digest(value: object) -> str:
    return sha256(repr(value).encode()).hexdigest()


def normalize(value: object) -> object:
    if isinstance(value, (int, float)):
        rounded = round(value)
        return int(rounded) if abs(value - rounded) < 1e-6 else round(value, 6)
    if isinstance(value, (list, tuple)):
        return tuple(normalize(item) for item in value)
    return value


def outline_digest(font: TTFont, glyph_name: str) -> str:
    recording = RecordingPen()
    font.getGlyphSet()[glyph_name].draw(recording)
    contours: list[tuple] = []
    current: list[tuple] = []
    for operation, arguments in recording.value:
        if operation == "moveTo" and current:
            contours.append(tuple(current))
            current = []
        current.append((operation, normalize(arguments)))
        if operation in {"closePath", "endPath"}:
            contours.append(tuple(current))
            current = []
    if current:
        contours.append(tuple(current))
    return digest(tuple(sorted(contours, key=repr)))


@lru_cache(maxsize=None)
def sfnt_bytes(path: Path) -> bytes:
    if path.suffix.lower() != ".woff2":
        return path.read_bytes()
    font = TTFont(path, recalcTimestamp=False)
    try:
        font.flavor = None
        output = BytesIO()
        font.save(output, reorderTables=False)
        return output.getvalue()
    finally:
        font.close()


def shape(path: Path, text: str, variations: dict[str, float] | None = None):
    face = hb.Face(sfnt_bytes(path))
    font = hb.Font(face)
    hb.ot_font_set_funcs(font)
    if variations:
        font.set_variations(variations)
    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(font, buffer)
    return list(buffer.glyph_infos), list(buffer.glyph_positions)


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
        errors.append(f"{path}: {GLYPH_NAME} width is {layer.width}, expected {EXPECTED_WIDTH}")
    anchors = {anchor.name: tuple(map(round, anchor.position)) for anchor in layer.anchors}
    if anchors != EXPECTED_ANCHORS:
        errors.append(f"{path}: {GLYPH_NAME} anchors are {anchors!r}")
    components = list(layer.components)
    if len(components) != EXPECTED_COMPONENTS or len(components) != len(layer.shapes):
        errors.append(f"{path}: {GLYPH_NAME} must contain {EXPECTED_COMPONENTS} pixel components")
    positions = []
    for component in components:
        positions.append(tuple(map(round, component.position)))
        if component.name != "pixel":
            errors.append(f"{path}: unexpected component {component.name!r}")
    if digest(tuple(sorted(positions))) != EXPECTED_POSITION_DIGEST:
        errors.append(f"{path}: {GLYPH_NAME} component positions changed")
    fontinfo = (path / "fontinfo.plist").read_text()
    rule = "sub iogonek' @CombiningTopAccents by idotless ogonekcomb;"
    if rule not in fontinfo:
        errors.append(f"{path}: missing reviewed iogonek ccmp rule")
    return errors


def validate_shaping(path: Path, font: TTFont, variations=None) -> list[str]:
    errors: list[str] = []
    order = font.getGlyphOrder()
    cmap = font.getBestCmap() or {}
    dotted_gid = order.index(cmap[CODEPOINT])
    idotless_gid = order.index(cmap[0x0131])
    ogonek_gid = order.index(cmap[0x0328])

    exported_marks = sorted(
        codepoint for codepoint in cmap if 0x0300 <= codepoint <= 0x036F
    )
    for mark in exported_marks:
        infos, positions = shape(path, chr(CODEPOINT) + chr(mark), variations)
        if len(infos) != 2 or infos[0].codepoint != dotted_gid:
            errors.append(f"{path}: U+25CC failed to retain U+{mark:04X}")
            continue
        if positions[1].x_advance != 0 or (
            positions[1].x_offset == 0 and positions[1].y_offset == 0
        ):
            errors.append(f"{path}: U+{mark:04X} did not attach to U+25CC")

    for mark in REQUIRED_MARKS + OPTIONAL_MARKS:
        infos, _ = shape(path, "į" + chr(mark), variations)
        gids = [info.codepoint for info in infos]
        expected = [idotless_gid, ogonek_gid, order.index(cmap[mark])]
        if gids != expected:
            errors.append(
                f"{path}: į + U+{mark:04X} shaped to {gids}, expected {expected}"
            )
    return errors


def validate_font(path: Path, *, expect_static: bool = True) -> list[str]:
    errors: list[str] = []
    font = TTFont(path, recalcTimestamp=False)
    try:
        glyph_name = (font.getBestCmap() or {}).get(CODEPOINT)
        if glyph_name is None:
            return [f"{path}: missing U+25CC ◌"]
        width, _ = font["hmtx"].metrics[glyph_name]
        if width != EXPECTED_WIDTH:
            errors.append(f"{path}: U+25CC width is {width}, expected {EXPECTED_WIDTH}")
        pen = BoundsPen(font.getGlyphSet())
        font.getGlyphSet()[glyph_name].draw(pen)
        if pen.bounds is None:
            errors.append(f"{path}: U+25CC must contain ink")
        elif pen.bounds[0] < 0 or pen.bounds[2] > width:
            errors.append(f"{path}: U+25CC bounds {pen.bounds} exceed its cell")
        if expect_static:
            style = next((name for name in STYLES if f"-{name}." in path.name), None)
            if style is None:
                errors.append(f"{path}: cannot identify Pixel style from filename")
            else:
                outline_kind = "cff" if "CFF " in font else "truetype"
                expected = EXPECTED_OUTLINE_DIGESTS[(outline_kind, style)]
                if outline_digest(font, glyph_name) != expected:
                    errors.append(f"{path}: U+25CC {style} {outline_kind} outline changed")
            errors.extend(validate_shaping(path, font))
        else:
            instances = {
                font["name"].getDebugName(instance.subfamilyNameID): instance
                for instance in font["fvar"].instances
            }
            if set(instances) != set(EXPECTED_VARIABLE_INSTANCES):
                errors.append(f"{path}: unexpected Pixel variable instances")
            else:
                for name, (location, expected_digest) in EXPECTED_VARIABLE_INSTANCES.items():
                    instance = instances[name]
                    if instance.coordinates.get("ELSH") != location:
                        errors.append(f"{path}: {name} ELSH location changed")
                        continue
                    instance_font = instantiateVariableFont(
                        font, dict(instance.coordinates), inplace=False, optimize=True
                    )
                    try:
                        instance_glyph = (instance_font.getBestCmap() or {})[CODEPOINT]
                        if outline_digest(instance_font, instance_glyph) != expected_digest:
                            errors.append(f"{path}: U+25CC {name} variable outline changed")
                    finally:
                        instance_font.close()
                    errors.extend(validate_shaping(path, font, dict(instance.coordinates)))
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


def validate_fontspector(path: Path) -> list[str]:
    data = json.loads(path.read_text())
    statuses: dict[tuple[str, str], str] = {}
    for font_path, sections in data.get("results", {}).items():
        style = next((name for name in STYLES if f"-{name}." in font_path), None)
        if style is None:
            continue
        for section in sections.values():
            for check in section:
                if check.get("check_id") in {"dotted_circle", "soft_dotted"}:
                    statuses[(style, check["check_id"])] = check.get("worst_status", "")
    errors = []
    for style in STYLES:
        for check_id in ("dotted_circle", "soft_dotted"):
            status = statuses.get((style, check_id))
            if status != "PASS":
                errors.append(f"{path}: {style} {check_id} is {status!r}, expected 'PASS'")
    return errors


def validate_release(root: Path) -> list[str]:
    errors = validate_source(root / "sources" / "NamcheShadowPixel.glyphspackage")
    for path in expected_fonts(root):
        if path.is_file():
            errors.extend(validate_font(path))
        else:
            errors.append(f"missing expected Pixel release font: {path}")
    variable = root / "fonts" / "NamcheShadowPixel" / "variable" / "NamcheShadowPixel[ELSH].ttf"
    if variable.is_file():
        errors.extend(validate_font(variable, expect_static=False))
    else:
        errors.append(f"missing expected Pixel variable font: {variable}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--fontspector-report", type=Path)
    args = parser.parse_args()
    errors = validate_release(args.root.resolve())
    if args.fontspector_report:
        errors.extend(validate_fontspector(args.fontspector_report))
    if errors:
        print("Pixel shaping validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Verified ◌ and required/optional į mark shaping in Pixel release/npm fonts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
