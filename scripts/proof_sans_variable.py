#!/usr/bin/env python3
"""Render named-weight static/VF comparison panels for review."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

from build_sans_variable import FAMILY_PS, WEIGHTS


SAMPLE = "HEAVY 0123 AVZ kvw"


def _font(path: Path, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(path, size)
    if weight is not None:
        font.set_variation_by_axes([weight])
    return font


def render(static_dir: Path, variable_path: Path, output: Path) -> None:
    panel_width, panel_height = 800, 330
    canvas = Image.new("RGB", (panel_width * 3, panel_height * 3), "#f4f4f4")
    labels = _font(Path("/System/Library/Fonts/SFNS.ttf"), 18) if Path("/System/Library/Fonts/SFNS.ttf").is_file() else None

    for index, (style, weight) in enumerate(WEIGHTS):
        x = (index % 3) * panel_width
        y = (index // 3) * panel_height
        static_font = _font(static_dir / f"{FAMILY_PS}-{style}.ttf", 64)
        variable_font = _font(variable_path, 64, weight)
        static = Image.new("L", (panel_width - 40, 120), 0)
        variable = Image.new("L", static.size, 0)
        ImageDraw.Draw(static).text((0, 0), SAMPLE, font=static_font, fill=255)
        ImageDraw.Draw(variable).text((0, 0), SAMPLE, font=variable_font, fill=255)
        difference = ImageChops.difference(static, variable)

        draw = ImageDraw.Draw(canvas)
        draw.text((x + 20, y + 10), f"{style} / {weight}", fill="#111111", font=labels)
        draw.text((x + 20, y + 43), "STATIC", fill="#555555", font=labels)
        canvas.paste(Image.merge("RGB", (static, static, static)), (x + 20, y + 65))
        draw.text((x + 20, y + 178), "VARIABLE", fill="#555555", font=labels)
        canvas.paste(Image.merge("RGB", (variable, variable, variable)), (x + 20, y + 200))

        histogram = difference.histogram()
        mean_error = sum(value * count for value, count in enumerate(histogram)) / (difference.width * difference.height * 255)
        draw.text((x + 605, y + 10), f"MAE {mean_error:.3%}", fill="#555555", font=labels)

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statics", type=Path, default=Path("fonts/NamcheShadowSans/ttf"))
    parser.add_argument(
        "--variable",
        type=Path,
        default=Path("fonts/NamcheShadowSans/variable/NamcheShadowSans[wght].ttf"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("documentation/proofs/sans-variable-named-instances.png"),
    )
    args = parser.parse_args()
    render(args.statics, args.variable, args.output)


if __name__ == "__main__":
    main()
