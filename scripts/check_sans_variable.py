#!/usr/bin/env python3
"""Validate the committed Namche Shadow Sans variable release files."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from fontPens.flattenPen import FlattenPen
from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from build_sans_variable import FAMILY, PARKED_GLYPHS, WEIGHTS


INTERPOLATION_REVIEW_GLYPHS = (
    "uni0163",
    "ordfeminine",
    "uni0472",
    "uni04E9",
    "ampersand",
)
REPRESENTATIVE_GLYPHS = (
    "H",
    "E",
    "a",
    "A",
    "V",
    "M",
    "Z",
    "zero",
    "one",
    "two",
    "nine",
    "Scedilla",
    "Uogonek",
    *INTERPOLATION_REVIEW_GLYPHS,
)
OUTLINE_SAMPLE_LENGTH = 4
STATIC_OUTLINE_TOLERANCE = 7
NPM_ENTRYPOINTS = ("font.js", "sans.js")
NPM_UPRIGHT_STYLES = (
    "Thin",
    "UltraLight",
    "Light",
    "Regular",
    "Medium",
    "SemiBold",
    "Bold",
    "Black",
    "UltraBlack",
)


def _glyph_area(font: TTFont, glyph_name: str) -> float:
    glyph_set = font.getGlyphSet()
    pen = AreaPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return pen.value


def _outline_points(font: TTFont, glyph_name: str) -> np.ndarray:
    """Flatten an outline so visually equivalent, differently segmented curves compare."""

    recording = RecordingPen()
    flattening = FlattenPen(
        recording,
        approximateSegmentLength=OUTLINE_SAMPLE_LENGTH,
        segmentLines=True,
    )
    font.getGlyphSet()[glyph_name].draw(flattening)
    return np.asarray(
        [
            arguments[0]
            for command, arguments in recording.value
            if command in {"moveTo", "lineTo"}
        ],
        dtype=float,
    )


def _directed_outline_distance(source: np.ndarray, target: np.ndarray) -> float:
    maximum = 0.0
    for start in range(0, len(source), 1024):
        batch = source[start : start + 1024]
        distances = np.linalg.norm(batch[:, None, :] - target[None, :, :], axis=2)
        maximum = max(maximum, float(distances.min(axis=1).max()))
    return maximum


def _outline_distance(first: np.ndarray, second: np.ndarray) -> float:
    """Return the symmetric sampled-outline distance in font units."""

    return max(
        _directed_outline_distance(first, second),
        _directed_outline_distance(second, first),
    )


def check(root: Path) -> None:
    variable_path = root / "variable" / "NamcheShadowSans[wght].ttf"
    webfont_path = root / "webfonts" / "NamcheShadowSans[wght].woff2"
    variable = TTFont(variable_path, recalcTimestamp=False)
    webfont = TTFont(webfont_path, recalcTimestamp=False)

    glyphs = set(variable.getGlyphOrder())
    if glyphs & PARKED_GLYPHS:
        raise ValueError(f"parked glyphs present in VF: {sorted(glyphs & PARKED_GLYPHS)}")
    if variable.getGlyphOrder() != webfont.getGlyphOrder() or "fvar" not in webfont:
        raise ValueError("TTF and WOFF2 variable releases do not match")

    axis = variable["fvar"].axes
    if len(axis) != 1 or (axis[0].axisTag, axis[0].minValue, axis[0].defaultValue, axis[0].maxValue) != (
        "wght",
        100,
        400,
        900,
    ):
        raise ValueError("unexpected variable axes")
    instance_weights = [instance.coordinates["wght"] for instance in variable["fvar"].instances]
    if instance_weights != [weight for _, weight in WEIGHTS]:
        raise ValueError(f"unexpected named instances: {instance_weights}")

    family_name = variable["name"].getDebugName(1)
    credits = "\n".join(
        name.toUnicode()
        for name in variable["name"].names
        if name.nameID in {0, 8, 9}
    )
    if family_name != FAMILY:
        raise ValueError(f"unexpected family name: {family_name}")
    for credit in ("The Geist Project Authors", "Vercel", "BTLG Holding GmbH", "Michael Marte", "Ruhm"):
        if credit not in credits:
            raise ValueError(f"missing binary credit: {credit}")

    for style, weight in WEIGHTS:
        static = TTFont(root / "ttf" / f"NamcheShadowSans-{style}.ttf", recalcTimestamp=False)
        if "fvar" in static:
            raise ValueError(f"static unexpectedly contains fvar: {style}")
        missing = PARKED_GLYPHS - set(static.getGlyphOrder())
        if missing:
            raise ValueError(f"{style} static is missing parked VF glyphs: {sorted(missing)}")
        instance = instantiateVariableFont(variable, {"wght": weight}, inplace=False, optimize=False)
        variable_area = _glyph_area(instance, "O")
        static_area = _glyph_area(static, "O")
        if not variable_area or not static_area or variable_area * static_area <= 0:
            raise ValueError(f"VF contour direction does not match the {style} static")
        for glyph_name in INTERPOLATION_REVIEW_GLYPHS:
            distance = _outline_distance(
                _outline_points(instance, glyph_name),
                _outline_points(static, glyph_name),
            )
            if distance > STATIC_OUTLINE_TOLERANCE:
                raise ValueError(
                    f"VF {glyph_name} at wght={weight} differs from the {style} static "
                    f"by {distance:.2f} units (limit {STATIC_OUTLINE_TOLERANCE})"
                )

    for weight in range(150, 900, 100):
        instance = instantiateVariableFont(variable, {"wght": weight}, inplace=False, optimize=False)
        for glyph_name in REPRESENTATIVE_GLYPHS:
            glyph = instance["glyf"][glyph_name]
            coordinates, ends, _ = glyph.getCoordinates(instance["glyf"])
            if not coordinates or not ends:
                raise ValueError(f"empty representative glyph {glyph_name} at wght={weight}")

    npm_dist = Path(__file__).resolve().parent.parent / "packages" / "next" / "dist"
    required_uprights = {
        "NamcheShadowSans-Variable.woff2",
        *(f"NamcheShadowSans-{style}.woff2" for style in NPM_UPRIGHT_STYLES),
    }
    for entrypoint in NPM_ENTRYPOINTS:
        source = (npm_dist / entrypoint).read_text()
        missing = sorted(name for name in required_uprights if name not in source)
        if missing:
            raise ValueError(
                f"{entrypoint} is missing the VF/static fallback coverage: {missing}"
            )

    print(f"Validated rounded Sans VF: {variable_path} and {webfont_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path("fonts/NamcheShadowSans"))
    args = parser.parse_args()
    check(args.root)


if __name__ == "__main__":
    main()
