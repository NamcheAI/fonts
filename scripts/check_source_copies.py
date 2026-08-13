#!/usr/bin/env python3
"""Verify renamed Geist source copies without hiding anchor-only fixes."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PAIRS = (
    (
        ROOT / "originals/geist/sources/GeistMono.glyphspackage",
        ROOT / "sources/NamcheShadowMono.glyphspackage",
        {"glyphs/ereversed-cy.glyph", "glyphs/yeru-cy.glyph"},
    ),
    (
        ROOT / "originals/geist/sources/GeistMono-Italic.glyphspackage",
        ROOT / "sources/NamcheShadowMono-Italic.glyphspackage",
        {
            "glyphs/hardsign-cy.glyph",
            "glyphs/yeru-cy.glyph",
            "glyphs/yu-cy.glyph",
        },
    ),
    (
        ROOT / "originals/geist/sources/GeistPixel.glyphspackage",
        ROOT / "sources/NamcheShadowPixel.glyphspackage",
        set(),
    ),
)


def strip_anchor_blocks(text: str) -> str:
    marker = "anchors = ("
    while marker in text:
        start = text.index(marker)
        opening = start + len(marker) - 1
        depth = 0
        end = opening
        for end in range(opening, len(text)):
            if text[end] == "(":
                depth += 1
            elif text[end] == ")":
                depth -= 1
                if depth == 0:
                    break
        else:
            raise ValueError("unterminated anchors block")
        if text[end + 1 : end + 2] == ";":
            end += 1
        if text[end + 1 : end + 2] == "\n":
            end += 1
        text = text[:start] + text[end + 1 :]
    return text


def relative_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "fontinfo.plist"
    }


def check_pair(original: Path, maintained: Path, anchor_only: set[str]) -> list[str]:
    errors: list[str] = []
    original_files = relative_files(original)
    maintained_files = relative_files(maintained)
    if original_files != maintained_files:
        missing = sorted(original_files - maintained_files)
        extra = sorted(maintained_files - original_files)
        errors.append(f"{maintained.name}: source tree differs; missing={missing}, extra={extra}")

    for relative in sorted(original_files & maintained_files):
        original_text = (original / relative).read_text()
        maintained_text = (maintained / relative).read_text()
        if relative in anchor_only:
            original_text = strip_anchor_blocks(original_text)
            maintained_text = strip_anchor_blocks(maintained_text)
        if original_text != maintained_text:
            errors.append(f"{maintained.name}/{relative}: differs from immutable Geist copy")
    return errors


def main() -> int:
    errors = [
        error
        for original, maintained, anchor_only in SOURCE_PAIRS
        for error in check_pair(original, maintained, anchor_only)
    ]
    if errors:
        print("\n".join(errors))
        return 1
    print("Verified Mono/Pixel source copies; approved Mono differences are anchor-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
