#!/usr/bin/env python3
"""Fail CI on real language-shaping regressions in Fontspector reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SHAPE_CHECK = "googlefonts/glyphsets/shape_languages"
SOFT_DOTTED_CHECK = "soft_dotted"
FORBIDDEN_SHAPE_MESSAGES = (
    "Shaper ",
    "Mandatory orthography codepoints",
    "Primary orthography codepoints",
)


def checks_for(result: dict) -> dict[str, dict]:
    return {
        check["check_id"]: check
        for section in result.values()
        for check in section
        if "check_id" in check
    }


def validate_report(path: Path) -> tuple[int, list[str]]:
    data = json.loads(path.read_text())
    errors: list[str] = []
    checked = 0
    for font_path, result in data.get("results", {}).items():
        if Path(font_path).suffix.lower() not in {".ttf", ".otf", ".woff2"}:
            continue
        if "NamcheShadowSans" not in font_path and "NamcheShadowMono" not in font_path:
            continue
        checked += 1
        checks = checks_for(result)

        soft_dotted = checks.get(SOFT_DOTTED_CHECK)
        if soft_dotted is None:
            errors.append(f"{font_path}: missing {SOFT_DOTTED_CHECK} result")
        elif soft_dotted.get("worst_status") != "PASS":
            errors.append(
                f"{font_path}: {SOFT_DOTTED_CHECK} is "
                f"{soft_dotted.get('worst_status')} instead of PASS"
            )

        shape = checks.get(SHAPE_CHECK)
        if shape is None:
            errors.append(f"{font_path}: missing {SHAPE_CHECK} result")
            continue
        messages = "\n".join(
            subresult.get("message", "") for subresult in shape.get("subresults", [])
        )
        for forbidden in FORBIDDEN_SHAPE_MESSAGES:
            if forbidden in messages:
                errors.append(f"{font_path}: retained real shaping warning: {forbidden}")

    return checked, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reports", nargs="+", type=Path)
    args = parser.parse_args()

    checked = 0
    errors: list[str] = []
    for report in args.reports:
        if not report.is_file():
            errors.append(f"missing Fontspector report: {report}")
            continue
        report_checked, report_errors = validate_report(report)
        checked += report_checked
        errors.extend(report_errors)

    if errors:
        print("\n".join(errors))
        return 1
    if not checked:
        print("No Namche Shadow Sans or Mono Fontspector results found")
        return 1
    print(
        f"Validated language shaping in {checked} font files; "
        "retained warnings are auxiliary omissions only"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
