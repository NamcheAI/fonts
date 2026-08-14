#!/usr/bin/env python3
"""Validate the minimum safe Mono hmtx encoding for the approved glyph order."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from fontTools.ttLib import TTFont


EXPECTED_COUNTS = {"upright": 1139, "italic": 1128}
EXPECTED_NONCOMMON_WIDTHS = Counter({0: 39, 500: 1})
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
        width_counts = Counter(widths)
        noncommon = Counter(
            {width: count for width, count in width_counts.items() if width != 600}
        )
        if noncommon != EXPECTED_NONCOMMON_WIDTHS:
            errors.append(
                f"{path}: non-600 advance inventory changed from "
                f"{dict(EXPECTED_NONCOMMON_WIDTHS)} to {dict(noncommon)}"
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
