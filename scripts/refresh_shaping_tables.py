#!/usr/bin/env python3
"""Refresh OpenType shaping tables without changing approved font outlines."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.ttLib.woff2 import compress


SHAPING_TABLES = ("GDEF", "GSUB", "GPOS")
OUTLINE_TABLES = ("glyf", "loca", "gvar", "CFF ", "CFF2", "hmtx")


def table_bytes(font: TTFont, tags: tuple[str, ...]) -> dict[str, bytes]:
    return {tag: font.getTableData(tag) for tag in tags if tag in font}


def prepare_source(source: TTFont, target: TTFont, source_path: Path) -> None:
    target_order = target.getGlyphOrder()
    source_names = set(source.getGlyphOrder())
    target_names = set(target_order)
    missing = target_names - source_names
    if missing:
        raise ValueError(
            f"{source_path}: compiled font is missing target glyphs: {sorted(missing)}"
        )

    # The rounded Sans VF deliberately parks five glyphs that remain in statics.
    # Subset a sharp build to the target's glyph set before copying name-based
    # layout objects; the approved target glyph order itself is never changed.
    if source_names != target_names:
        options = subset.Options()
        options.layout_features = ["*"]
        options.retain_gids = False
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(glyphs=target_order)
        subsetter.subset(source)

    if set(source.getGlyphOrder()) != target_names:
        raise ValueError(f"{source_path}: could not align compiled glyph set")


def refresh_font(source_path: Path, target_path: Path) -> None:
    source = TTFont(source_path, recalcTimestamp=False)
    target = TTFont(target_path, recalcTimestamp=False)
    before = table_bytes(target, OUTLINE_TABLES)

    prepare_source(source, target, source_path)
    for tag in SHAPING_TABLES:
        if tag not in source:
            raise ValueError(f"{source_path}: missing required {tag} table")
        source[tag].ensureDecompiled()
        target[tag] = deepcopy(source[tag])

    with NamedTemporaryFile(
        prefix=f".{target_path.name}.", suffix=".tmp", dir=target_path.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
    try:
        target.save(temporary_path, reorderTables=False)
        target.close()
        source.close()

        result = TTFont(temporary_path, recalcTimestamp=False)
        after = table_bytes(result, OUTLINE_TABLES)
        result.close()
        if after != before:
            changed = sorted(set(before) | set(after))
            raise ValueError(
                f"{target_path}: shaping refresh changed protected tables: {changed}"
            )
        temporary_path.replace(target_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def refresh_webfonts(output: Path) -> int:
    count = 0
    for webfont in sorted((output / "webfonts").glob("*.woff2")):
        stem = webfont.stem
        if "[wght]" in stem:
            source = output / "variable" / f"{stem}.ttf"
        else:
            source = output / "ttf" / f"{stem}.ttf"
        if not source.is_file():
            raise FileNotFoundError(f"no TrueType source for {webfont}: {source}")
        compress(source, webfont)
        count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--compiled",
        required=True,
        type=Path,
        help="fresh gftools output containing the updated shaping tables",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="approved release family whose outlines must be preserved",
    )
    args = parser.parse_args()

    targets = sorted((args.output / "otf").glob("*.otf"))
    targets += sorted((args.output / "ttf").glob("*.ttf"))
    targets += sorted((args.output / "variable").glob("*.ttf"))
    if not targets:
        parser.error(f"no OTF or TTF files found below {args.output}")

    for target in targets:
        relative = target.relative_to(args.output)
        compiled = args.compiled / relative
        if not compiled.is_file():
            raise FileNotFoundError(f"missing compiled counterpart: {compiled}")
        refresh_font(compiled, target)

    webfont_count = refresh_webfonts(args.output)
    print(
        f"Refreshed shaping in {len(targets)} fonts and regenerated "
        f"{webfont_count} webfonts; outlines and metrics are unchanged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
