#!/usr/bin/env python3
"""Validate the minimum safe Mono hmtx encoding for the approved glyph order."""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


EXPECTED_COUNTS = {"upright": 1139, "italic": 1128}
EXPECTED_ZERO_WIDTH_GLYPHS = {
    "acutecomb",
    "dotbelowcomb",
    "dotbelowcomb.ss08",
    "gravecomb",
    "hookabovecomb",
    "tildecomb",
    "uni0302",
    "uni03020300",
    "uni03020301",
    "uni03020303",
    "uni03020309",
    "uni0304",
    "uni0306",
    "uni03060300",
    "uni03060301",
    "uni03060303",
    "uni03060309",
    "uni0306.cy",
    "uni0307",
    "uni0307.ss08",
    "uni0308",
    "uni0308.ss08",
    "uni030A",
    "uni030B",
    "uni030C",
    "uni030C.alt",
    "uni0312",
    "uni031B",
    "uni0326",
    "uni0326.loclMAH",
    "uni0327",
    "uni0328",
    "uni0335",
    "uni0335.case",
    "uni0336",
    "uni0337",
    "uni0337.case",
    "uni0338",
    "uni0338.case",
}
EXPECTED_EXCEPTIONAL_ADVANCES = {".notdef": 500} | {
    name: 0 for name in EXPECTED_ZERO_WIDTH_GLYPHS
}
EXPECTED_FILE_COUNT = 80


def minimum_metric_count(widths: list[int]) -> int:
    if not widths:
        raise ValueError("font has no horizontal metrics")
    last_advance = widths[-1]
    count = len(widths)
    while count > 1 and widths[count - 2] == last_advance:
        count -= 1
    return count


def validate_font(path: Path) -> list[str]:
    errors: list[str] = []
    font = TTFont(path, recalcTimestamp=False)
    try:
        order = font.getGlyphOrder()
        widths = [font["hmtx"][name][0] for name in order]
        actual = font["hhea"].numberOfHMetrics
        minimum = minimum_metric_count(widths)
        orientation = "italic" if "Italic" in path.name else "upright"
        expected = EXPECTED_COUNTS[orientation]
        if actual != minimum:
            errors.append(
                f"{path}: numberOfHMetrics {actual} is not the safe minimum {minimum}"
            )
        if actual != expected:
            errors.append(
                f"{path}: numberOfHMetrics {actual} differs from the reviewed "
                f"{orientation} baseline {expected}"
            )
        exceptional_advances = {
            name: width
            for name, width in zip(order, widths, strict=True)
            if width != 600
        }
        if exceptional_advances != EXPECTED_EXCEPTIONAL_ADVANCES:
            errors.append(
                f"{path}: glyph-specific non-600 advances differ from the "
                "reviewed baseline"
            )
    finally:
        font.close()
    return errors


def mono_fonts(root: Path) -> list[Path]:
    release = root / "fonts" / "NamcheShadowMono"
    package = (
        root
        / "packages"
        / "next"
        / "dist"
        / "fonts"
        / "namche-shadow-mono"
    )
    paths = [
        path
        for directory in (release / "ttf", release / "variable", release / "webfonts", package)
        for path in directory.glob("*")
        if path.suffix.lower() in {".ttf", ".woff2"}
    ]
    return sorted(paths)


def validate_release(root: Path) -> list[str]:
    paths = mono_fonts(root)
    errors: list[str] = []
    if len(paths) != EXPECTED_FILE_COUNT:
        errors.append(
            f"expected {EXPECTED_FILE_COUNT} Mono TrueType release/npm fonts; "
            f"found {len(paths)}"
        )
    for path in paths:
        errors.extend(validate_font(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    errors = validate_release(args.root.resolve())
    if errors:
        print("Mono horizontal-metric validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Verified minimum safe numberOfHMetrics in 80 Mono release/npm fonts "
        "(upright 1139, italic 1128)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
