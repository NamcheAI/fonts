#!/usr/bin/env python3
"""Restore the inkless Unicode separators in Namche Shadow Pixel statics.

The maintained Glyphs source and the Pixel variable font contain U+2028 and
U+2029, both at 600 units. The approved native static exports predate that
source correction, so this narrowly scoped finalizer restores the two empty
glyphs without changing any existing outline or layout table.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


SEPARATORS = {0x2028: "uni2028", 0x2029: "uni2029"}
SEPARATOR_WIDTH = 600
STATIC_DIRECTORIES = ("otf", "ttf", "webfonts")
FONT_SUFFIXES = {".otf", ".ttf", ".woff2"}


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
