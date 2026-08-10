#!/usr/bin/env python3
"""
Apply Glyphs RoundCorner export filters:

  -40  Caps + figures + cap/figure-like glyphs  (include)
  -25  everything else                          (exclude same set)

Usage:
  python3 scripts/apply_roundcorner_filters.py
  python3 scripts/apply_roundcorner_filters.py --package sources/Geist.glyphspackage
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PACKAGE = SCRIPT_DIR.parent / "sources" / "Geist.glyphspackage"

# Cap-/ziffern-ähnliche Sonderzeichen (nur wenn im Font vorhanden)
LIKE_GLYPHS = (
    # Währung
    "euro",
    "dollar",
    "sterling",
    "yen",
    "cent",
    "currency",
    "peso",
    "hryvnia",
    "ruble",
    "rupeeIndian",
    "sheqel",
    "baht",
    "florin",
    # Prozent & Co.
    "percent",
    "perthousand",
    "numbersign",
    # Brüche
    "fraction",
    "onehalf",
    "onethird",
    "twothirds",
    "onequarter",
    "threequarters",
    "onefifth",
    "oneeighth",
    "threeeighths",
    "fiveeighths",
    "seveneighths",
    # Superior / Inferior Ziffern
    "zerosuperior",
    "onesuperior",
    "twosuperior",
    "threesuperior",
    "foursuperior",
    "fivesuperior",
    "sixsuperior",
    "sevensuperior",
    "eightsuperior",
    "ninesuperior",
    "zeroinferior",
    "oneinferior",
    "twoinferior",
    "threeinferior",
    "fourinferior",
    "fiveinferior",
    "sixinferior",
    "seveninferior",
    "eightinferior",
    "nineinferior",
    # Cap-artige Sonderformen
    "ampersand",
    "at",
    "numero",
    "ordmasculine",
    "ordfeminine",
)

DIGIT_BASE = {
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
}

# Minuskel-Eszett nie in -40; Cap-Eszett schon (über Uppercase-Klasse)
EXCLUDE_FROM_STRONG = frozenset({"germandbls", "ß"})


def _parse_glyphnames(glyphs_dir: Path) -> set[str]:
    names: set[str] = set()
    for path in glyphs_dir.glob("*.glyph"):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"glyphname\s*=\s*(\"[^\"]+\"|[^\s;]+)\s*;", text)
        if not match:
            continue
        raw = match.group(1)
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]
        names.add(raw)
    return names


def _uppercase_class_names(fontinfo: str) -> list[str]:
    match = re.search(
        r"automatic\s*=\s*1;\s*code\s*=\s*\"([^\"]+)\";\s*name\s*=\s*Uppercase;",
        fontinfo,
        re.S,
    )
    if not match:
        match = re.search(
            r"code\s*=\s*\"([^\"]+)\";\s*name\s*=\s*Uppercase;",
            fontinfo,
            re.S,
        )
    if not match:
        raise SystemExit("Could not find Uppercase class in fontinfo.plist")
    return match.group(1).split()


def build_strong_set(package: Path) -> list[str]:
    fontinfo = (package / "fontinfo.plist").read_text(encoding="utf-8")
    names = _parse_glyphnames(package / "glyphs")
    uppercase = [n for n in _uppercase_class_names(fontinfo) if n in names]
    digit_related = [
        n for n in names if n in DIGIT_BASE or n.split(".", 1)[0] in DIGIT_BASE
    ]
    like = [n for n in LIKE_GLYPHS if n in names]
    strong = set(uppercase) | set(digit_related) | set(like)
    strong -= EXCLUDE_FROM_STRONG
    if "Germandbls" in names:
        strong.add("Germandbls")
    return sorted(strong, key=lambda s: (s.lower(), s))


def filter_value(radius: int, mode: str, glyph_list: list[str]) -> str:
    joined = ", ".join(glyph_list)
    return f"RoundCorner;{radius};1;{mode}: {joined}"


def filter_plist_block(radius: int, mode: str, glyph_list: list[str]) -> str:
    value = filter_value(radius, mode, glyph_list)
    # Escape is unnecessary: glyph names have no quotes/backslashes
    return '{\nname = Filter;\nvalue = "' + value + '";\n}'


def _strip_existing_roundcorner_filters(custom_params_body: str) -> str:
    """Remove existing RoundCorner Filter entries from a customParameters body."""
    pattern = re.compile(
        r"\{\s*name\s*=\s*Filter;\s*value\s*=\s*\"RoundCorner[^\"]*\";\s*\},?\s*",
        re.S,
    )
    cleaned = pattern.sub("", custom_params_body)
    cleaned = re.sub(r"^\s*,\s*", "", cleaned)
    cleaned = re.sub(r",\s*,", ",", cleaned)
    cleaned = cleaned.lstrip("\n")
    if cleaned and not cleaned.startswith("\n"):
        cleaned = "\n" + cleaned
    return cleaned


def apply_to_fontinfo(fontinfo: str, glyph_list: list[str]) -> tuple[str, int]:
    """
    Insert RoundCorner filters into every static instance customParameters.
    Skips variable instances (type = variable).
    Returns (new_fontinfo, instances_updated).
    """
    include_block = filter_plist_block(-40, "include", glyph_list)
    exclude_block = filter_plist_block(-25, "exclude", glyph_list)
    injection = "\n" + include_block + ",\n" + exclude_block + ",\n"

    instances_match = re.search(r"instances\s*=\s*\(", fontinfo)
    if not instances_match:
        raise SystemExit("No instances block found in fontinfo.plist")

    head = fontinfo[: instances_match.end()]
    rest = fontinfo[instances_match.end() :]

    # Split instances by top-level `{` ... `},` — walk braces
    updated = 0
    out_parts: list[str] = [head]
    i = 0
    n = len(rest)
    while i < n:
        if rest[i] != "{":
            out_parts.append(rest[i])
            i += 1
            continue
        # parse one dict
        depth = 0
        start = i
        while i < n:
            ch = rest[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            i += 1
        block = rest[start:i]
        # consume trailing comma/whitespace
        j = i
        while j < n and rest[j] in " \t\n\r":
            j += 1
        trailing = ""
        if j < n and rest[j] == ",":
            trailing = rest[i:j] + ","
            i = j + 1
        else:
            trailing = rest[i:j]
            i = j

        if re.search(r"\btype\s*=\s*variable\s*;", block):
            out_parts.append(block + trailing)
            continue

        cp = re.search(r"customParameters\s*=\s*\(", block)
        if not cp:
            out_parts.append(block + trailing)
            continue

        cp_start = cp.end()
        depth = 1
        k = cp_start
        while k < len(block):
            if block[k] == "(":
                depth += 1
            elif block[k] == ")":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        if depth != 0:
            out_parts.append(block + trailing)
            continue

        body = block[cp_start:k]
        body = _strip_existing_roundcorner_filters(body)
        body = injection + body
        new_block = block[:cp_start] + body + block[k:]
        out_parts.append(new_block + trailing)
        updated += 1

    return "".join(out_parts), updated


def write_paste_file(path: Path, glyph_list: list[str]) -> None:
    include = filter_value(-40, "include", glyph_list)
    exclude = filter_value(-25, "exclude", glyph_list)
    path.write_text(
        "# Paste into Font Info → Exports → Custom Parameters (Filter)\n"
        "# Strong set: Uppercase + Decimal Digits (+ variants) + cap/figure-like\n"
        f"# Glyph count: {len(glyph_list)}\n\n"
        f"{include}\n\n"
        f"{exclude}\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package",
        type=Path,
        action="append",
        help="Path to .glyphspackage (repeatable). Default: sources/Geist.glyphspackage",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build set and paste file only; do not rewrite fontinfo.plist",
    )
    args = parser.parse_args()
    packages = args.package or [DEFAULT_PACKAGE]

    primary = packages[0]
    strong = build_strong_set(primary)
    paste_path = SCRIPT_DIR / "roundcorner_caps_figs_filters.txt"
    write_paste_file(paste_path, strong)
    print(f"Strong set: {len(strong)} glyphs")
    print(f"Wrote {paste_path}")

    if args.dry_run:
        return

    for package in packages:
        fontinfo_path = package / "fontinfo.plist"
        # Rebuild per package so lists match that package's glyph coverage
        strong_pkg = build_strong_set(package)
        text = fontinfo_path.read_text(encoding="utf-8")
        new_text, count = apply_to_fontinfo(text, strong_pkg)
        fontinfo_path.write_text(new_text, encoding="utf-8")
        print(f"Updated {count} static instances in {fontinfo_path}")


if __name__ == "__main__":
    main()
