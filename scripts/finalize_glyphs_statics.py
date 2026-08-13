#!/usr/bin/env python3
"""Combine Glyphs-rendered Sans outlines with the reproducible build tables.

Glyphs 4 is the visual source of truth because it runs the seven RoundCorner
instance filters. The gftools build remains the source of truth for naming,
OpenType layout, and other release metadata. This script replaces only the
outline and metric tables, flattens nested TrueType components, and derives
WOFF2 files from the finalized TTFs.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import os
from pathlib import Path
import tempfile

from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont


WEIGHTS = (
    "Thin",
    "ExtraLight",
    "Light",
    "Regular",
    "Medium",
    "SemiBold",
    "Bold",
    "ExtraBold",
    "Black",
)
REQUIRED_CODEPOINTS = (0x046A, 0x046B, 0x03BC, 0x0E3F, 0x20B1)


def font_path(root: Path, extension: str, weight: str) -> Path:
    folder = "webfonts" if extension == "woff2" else extension
    return root / folder / f"NamcheShadowSans-{weight}.{extension}"


def assert_matching_fonts(base: TTFont, rendered: TTFont, path: Path) -> None:
    if set(base.getGlyphOrder()) != set(rendered.getGlyphOrder()):
        raise ValueError(f"glyph sets differ in {path}")
    cmap = rendered.getBestCmap()
    missing = [f"U+{codepoint:04X}" for codepoint in REQUIRED_CODEPOINTS if codepoint not in cmap]
    if missing:
        raise ValueError(f"required static glyphs missing in {path}: {missing}")
    if "fvar" in rendered:
        raise ValueError(f"unexpected variable table in static font {path}")


def flatten_nested_components(font: TTFont) -> int:
    glyf = font["glyf"]
    nested = []
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.isComposite() and any(glyf[component.glyphName].isComposite() for component in glyph.components):
            nested.append(name)

    glyph_set = font.getGlyphSet()
    for name in nested:
        recording = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(recording)
        pen = TTGlyphPen(None)
        recording.replay(pen)
        glyf[name] = pen.glyph()
    return len(nested)


def assert_roundcorner_output(font: TTFont, path: Path) -> None:
    pen = RecordingPen()
    font.getGlyphSet()["H"].draw(pen)
    curves = sum(operation in {"curveTo", "qCurveTo"} for operation, _ in pen.value)
    if curves != 4:
        raise ValueError(f"{path} has {curves} H curves; expected Glyphs RoundCorner output with 4")


def finalize_font(base_path: Path, rendered_path: Path, output_path: Path) -> int:
    base = TTFont(base_path, recalcTimestamp=False)
    rendered = TTFont(rendered_path, recalcTimestamp=False)
    assert_matching_fonts(base, rendered, rendered_path)
    assert_roundcorner_output(rendered, rendered_path)
    # Glyphs and gftools serialize the same glyph set in different orders. The
    # outline table and font-level glyph order must agree; layout tables compile
    # by glyph name and are safely remapped when the font is saved. Force every
    # table to decompile before changing the order; otherwise an untouched raw
    # cmap/GPOS table would still contain the old numeric glyph IDs.
    for table_tag in base.keys():
        base[table_tag]
    base.setGlyphOrder(rendered.getGlyphOrder())

    extension = output_path.suffix
    if extension == ".ttf":
        base["glyf"] = deepcopy(rendered["glyf"])
        base["hmtx"] = deepcopy(rendered["hmtx"])
        flattened = flatten_nested_components(base)
    elif extension == ".otf":
        base["CFF "] = deepcopy(rendered["CFF "])
        base["hmtx"] = deepcopy(rendered["hmtx"])
        flattened = 0
    else:
        raise ValueError(f"unsupported output format: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(output_path, reorderTables=False)
    assert_roundcorner_output(TTFont(output_path), output_path)
    return flattened


def write_woff2(ttf_path: Path, output_path: Path) -> None:
    font = TTFont(ttf_path, recalcTimestamp=False)
    font.flavor = "woff2"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(output_path, reorderTables=False)


def validate_inputs(gftools_root: Path, glyphs_root: Path) -> None:
    """Reject an incomplete export before any release file can be replaced."""
    for weight in WEIGHTS:
        for extension in ("otf", "ttf"):
            base_path = font_path(gftools_root, extension, weight)
            rendered_path = font_path(glyphs_root, extension, weight)
            if not base_path.is_file():
                raise FileNotFoundError(f"missing release base: {base_path}")
            if not rendered_path.is_file():
                raise FileNotFoundError(f"missing Glyphs export: {rendered_path}")
            base = TTFont(base_path, recalcTimestamp=False)
            rendered = TTFont(rendered_path, recalcTimestamp=False)
            assert_matching_fonts(base, rendered, rendered_path)
            assert_roundcorner_output(rendered, rendered_path)
            base.close()
            rendered.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gftools", type=Path, required=True, help="gftools NamcheShadowSans root")
    parser.add_argument("--glyphs", type=Path, required=True, help="Glyphs-export NamcheShadowSans root")
    parser.add_argument("--output", type=Path, required=True, help="final NamcheShadowSans root")
    args = parser.parse_args()

    validate_inputs(args.gftools, args.glyphs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="namche-sans-statics-", dir=args.output.parent) as directory:
        staging = Path(directory)
        flattened_total = 0
        for weight in WEIGHTS:
            for extension in ("otf", "ttf"):
                flattened_total += finalize_font(
                    font_path(args.gftools, extension, weight),
                    font_path(args.glyphs, extension, weight),
                    font_path(staging, extension, weight),
                )
            write_woff2(
                font_path(staging, "ttf", weight),
                font_path(staging, "woff2", weight),
            )

        # Every input and staged output has succeeded. Replace only the approved
        # upright release files; existing italic files remain untouched.
        for weight in WEIGHTS:
            for extension in ("otf", "ttf", "woff2"):
                destination = font_path(args.output, extension, weight)
                destination.parent.mkdir(parents=True, exist_ok=True)
                os.replace(font_path(staging, extension, weight), destination)

    print(f"Finalized {len(WEIGHTS)} static weights; flattened {flattened_total} nested glyphs")


if __name__ == "__main__":
    main()
