#!/usr/bin/env python3
"""Finalize metadata omitted from Namche Shadow Pixel static exports.

The maintained Glyphs source and the Pixel variable font contain U+2028 and
U+2029, both at 600 units. The approved native static exports predate that
source correction. The source also carries ligature-caret anchors, including
the user-facing fi and fl positions, that are missing from the native statics.
This narrowly scoped finalizer restores both kinds of data without changing
existing outlines.
"""

from __future__ import annotations

import argparse
from functools import lru_cache
from pathlib import Path

import glyphsLib
from fontTools.misc.psCharStrings import T2CharString
from fontTools.otlLib.builder import buildCoverage, buildLigGlyph
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables


SEPARATORS = {0x2028: "uni2028", 0x2029: "uni2029"}
SEPARATOR_WIDTH = 600
STATIC_DIRECTORIES = ("otf", "ttf", "webfonts")
FONT_SUFFIXES = {".otf", ".ttf", ".woff2"}
ROOT = Path(__file__).resolve().parent.parent
PIXEL_SOURCE = ROOT / "sources" / "NamcheShadowPixel.glyphspackage"
REQUIRED_LIGATURES = ("fi", "fl")


@lru_cache(maxsize=1)
def source_ligature_carets() -> dict[str, tuple[int, ...]]:
    source = glyphsLib.load(PIXEL_SOURCE)
    result = {}
    for glyph in source.glyphs:
        layer_values = []
        for layer in glyph.layers:
            anchors = sorted(
                (
                    (int(anchor.name.removeprefix("caret_")), round(anchor.position.x))
                    for anchor in layer.anchors
                    if anchor.name.startswith("caret_")
                ),
                key=lambda item: item[0],
            )
            if anchors:
                layer_values.append(tuple(value for _, value in anchors))
        if not layer_values:
            continue
        if len(set(layer_values)) != 1:
            raise ValueError(
                f"{PIXEL_SOURCE}: {glyph.name} must have matching caret anchors "
                "in every exporting layer"
            )
        result[glyph.name] = layer_values[0]
    missing = sorted(set(REQUIRED_LIGATURES) - result.keys())
    if missing:
        raise ValueError(f"{PIXEL_SOURCE}: missing required caret anchors for {missing!r}")
    return result


def has_ink(font: TTFont, glyph_name: str) -> bool:
    pen = BoundsPen(font.getGlyphSet())
    font.getGlyphSet()[glyph_name].draw(pen)
    return pen.bounds is not None


def _add_truetype_glyph(font: TTFont, glyph_name: str) -> None:
    font["glyf"].glyphs[glyph_name] = TTGlyphPen(None).glyph()


def _add_cff_glyph(font: TTFont, glyph_name: str) -> None:
    top_dict = font["CFF "].cff.topDictIndex[0]
    charstrings = top_dict.CharStrings
    private = top_dict.Private
    width_delta = SEPARATOR_WIDTH - private.nominalWidthX
    program = ["endchar"] if SEPARATOR_WIDTH == private.defaultWidthX else [width_delta, "endchar"]
    charstring = T2CharString(
        program=program,
        private=private,
        globalSubrs=font["CFF "].cff.GlobalSubrs,
    )

    if charstrings.charStringsAreIndexed:
        index = len(charstrings.charStringsIndex)
        charstrings.charStringsIndex.append(charstring)
        charstrings.charStrings[glyph_name] = index
    else:
        charstrings.charStrings[glyph_name] = charstring


def _add_glyph(font: TTFont, glyph_name: str) -> None:
    order = font.getGlyphOrder()
    if glyph_name in order:
        return
    if "glyf" in font:
        _add_truetype_glyph(font, glyph_name)
    elif "CFF " in font:
        _add_cff_glyph(font, glyph_name)
    else:
        raise ValueError("font has neither TrueType nor CFF outlines")
    order.append(glyph_name)
    font.setGlyphOrder(order)
    font["hmtx"].metrics[glyph_name] = (SEPARATOR_WIDTH, 0)
    font["maxp"].numGlyphs = len(order)


def ligature_caret_coordinates(font: TTFont, glyph_name: str) -> tuple[int, ...]:
    if "GDEF" not in font or font["GDEF"].table.LigCaretList is None:
        return ()
    caret_list = font["GDEF"].table.LigCaretList
    if glyph_name not in caret_list.Coverage.glyphs:
        return ()
    index = caret_list.Coverage.glyphs.index(glyph_name)
    carets = caret_list.LigGlyph[index].CaretValue
    if any(caret.Format != 1 for caret in carets):
        return ()
    return tuple(caret.Coordinate for caret in carets)


def _restore_ligature_carets(font: TTFont) -> bool:
    expected = source_ligature_carets()
    if all(
        ligature_caret_coordinates(font, glyph) == coordinates
        for glyph, coordinates in expected.items()
    ):
        return False
    if "GDEF" not in font:
        raise ValueError("font is missing its GDEF table")

    table = font["GDEF"].table
    caret_list = table.LigCaretList
    lig_glyphs = {}
    if caret_list is not None:
        lig_glyphs.update(zip(caret_list.Coverage.glyphs, caret_list.LigGlyph))
    for glyph_name, coordinates in expected.items():
        lig_glyphs[glyph_name] = buildLigGlyph(coordinates, None)

    glyph_map = font.getReverseGlyphMap()
    glyphs = sorted(lig_glyphs, key=glyph_map.__getitem__)
    if caret_list is None:
        caret_list = otTables.LigCaretList()
        table.LigCaretList = caret_list
    caret_list.Coverage = buildCoverage(glyphs, glyph_map)
    caret_list.LigGlyph = [lig_glyphs[glyph] for glyph in caret_list.Coverage.glyphs]
    caret_list.LigGlyphCount = len(caret_list.LigGlyph)
    return True


def finalize_font(path: Path) -> bool:
    font = TTFont(path, recalcTimestamp=False)
    changed = False
    try:
        best_cmap = font.getBestCmap() or {}
        for codepoint, canonical_name in SEPARATORS.items():
            glyph_name = best_cmap.get(codepoint, canonical_name)
            if glyph_name not in font.getGlyphOrder():
                _add_glyph(font, glyph_name)
                changed = True

            if font["hmtx"].metrics[glyph_name] != (SEPARATOR_WIDTH, 0):
                font["hmtx"].metrics[glyph_name] = (SEPARATOR_WIDTH, 0)
                changed = True
            for table in font["cmap"].tables:
                if table.isUnicode() and table.cmap.get(codepoint) != glyph_name:
                    table.cmap[codepoint] = glyph_name
                    changed = True

            if has_ink(font, glyph_name):
                raise ValueError(f"{path}: {glyph_name} must remain inkless")

        changed = _restore_ligature_carets(font) or changed

        if changed:
            font.save(path, reorderTables=False)
        return changed
    finally:
        font.close()


def font_files(root: Path) -> list[Path]:
    return sorted(
        path
        for directory in STATIC_DIRECTORIES
        for path in (root / directory).glob("*")
        if path.suffix.lower() in FONT_SUFFIXES
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("fonts/NamcheShadowPixel"),
        help="Namche Shadow Pixel release-family directory",
    )
    args = parser.parse_args()

    paths = font_files(args.root)
    if not paths:
        parser.error(f"no Pixel static fonts found below {args.root}")
    changed = [path for path in paths if finalize_font(path)]
    print(f"Verified {len(paths)} Pixel statics; updated {len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
