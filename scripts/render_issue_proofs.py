#!/usr/bin/env python3
"""Render visual proof panels for the open Fontspector maintenance issues."""

from __future__ import annotations

from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont, features


WIDTH = 1600
BACKGROUND = "#f0f2f5"
TEXT = "#262626"
MUTED = "#66666e"
LINE = "#bdb5a1"
YELLOW = "#ffd433"
BLUE = "#94c7e6"
PURPLE = "#b88cd1"
RED = "#e03847"
GREEN = "#0e7a5f"

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "documentation" / "issues"
SANS_DIR = ROOT / "fonts" / "NamcheShadowSans" / "ttf"
MONO_DIR = ROOT / "fonts" / "NamcheShadowMono" / "ttf"
PIXEL_DIR = ROOT / "fonts" / "NamcheShadowPixel" / "ttf"
SANS_VF = ROOT / "fonts" / "NamcheShadowSans" / "variable" / "NamcheShadowSans[wght].ttf"
MONO_ITALIC_VF = (
    ROOT
    / "fonts"
    / "NamcheShadowMono"
    / "variable"
    / "NamcheShadowMono-Italic[wght].ttf"
)


def font(path: Path, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    kwargs = {}
    if features.check_feature("raqm"):
        kwargs["layout_engine"] = ImageFont.Layout.RAQM
    result = ImageFont.truetype(path, size, **kwargs)
    if weight is not None:
        result.set_variation_by_axes([weight])
    return result


def fit(path: Path, text: str, max_width: int, size: int) -> ImageFont.FreeTypeFont:
    while size > 22:
        candidate = font(path, size)
        if candidate.getlength(text) <= max_width:
            return candidate
        size -= 2
    return font(path, size)


def canvas(issue: int, title: str, subtitle: str, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, height), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1060, 235), fill=YELLOW)
    draw.rectangle((1060, 0, WIDTH, 118), fill=BLUE)
    draw.rectangle((1060, 118, WIDTH, 235), fill=PURPLE)
    label = font(MONO_DIR / "NamcheShadowMono-Medium.ttf", 28)
    draw.text((72, 42), f"NAMCHE SHADOW / ISSUE #{issue}", font=label, fill=TEXT)
    draw.text(
        (68, 102),
        title,
        font=fit(SANS_DIR / "NamcheShadowSans-Black.ttf", title, 920, 76),
        fill=TEXT,
    )
    subtitle_font = fit(
        MONO_DIR / "NamcheShadowMono-Regular.ttf", subtitle, WIDTH - 144, 28
    )
    draw.text((72, 267), subtitle, font=subtitle_font, fill=MUTED)
    return image, draw


def section(draw: ImageDraw.ImageDraw, y: int, title: str, color: str = TEXT) -> None:
    label = font(MONO_DIR / "NamcheShadowMono-Medium.ttf", 25)
    draw.text((72, y), title.upper(), font=label, fill=color)
    draw.line((72, y + 42, WIDTH - 72, y + 42), fill=LINE, width=2)


def footer(draw: ImageDraw.ImageDraw, height: int, source: str) -> None:
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 20)
    draw.line((72, height - 72, WIDTH - 72, height - 72), fill=LINE, width=2)
    draw.text((72, height - 52), f"SOURCE  {source}", font=label, fill=MUTED)


def name(font_file: Path, name_id: int) -> str:
    ttfont = TTFont(font_file, lazy=True)
    value = ttfont["name"].getDebugName(name_id) or ""
    ttfont.close()
    return value


def render_issue_20() -> None:
    image, draw = canvas(
        20,
        "LEGACY NAME LENGTH",
        "Variable aliases now fit; public family and STAT names stay complete.",
        1250,
    )
    section(draw, 340, "Variable italic aliases · family + style ≤ 32")
    ttfont = TTFont(MONO_ITALIC_VF, lazy=True)
    family = ttfont["name"].getBestFamilyName() or "Namche Shadow Mono"
    variable_names = []
    for instance in ttfont["fvar"].instances:
        style = ttfont["name"].getDebugName(instance.subfamilyNameID) or ""
        if style in {"XLight Italic", "SemiBd Italic", "XBold Italic"}:
            variable_names.append(f"{family} {style}")
    ttfont.close()
    specimen = MONO_DIR / "NamcheShadowMono-Italic.ttf"
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 22)
    for index, value in enumerate(variable_names):
        y = 410 + index * 105
        draw.text((72, y), value, font=fit(specimen, value, 1220, 52), fill=TEXT)
        draw.text((1325, y + 15), f"{len(value)} / 32", font=label, fill=GREEN)

    section(draw, 750, "Static PostScript names · legal ≤ 63; guidance ≤ 27")
    samples = []
    for directory in (SANS_DIR, MONO_DIR):
        for path in sorted(directory.glob("*Italic.ttf")):
            value = name(path, 6)
            if len(value) > 27:
                samples.append(value)
    for index, value in enumerate(samples[:4]):
        y = 820 + index * 72
        draw.text((72, y), value, font=fit(specimen, value, 1190, 42), fill=TEXT)
        draw.text((1325, y + 8), f"{len(value)} / 63", font=label, fill=GREEN)
    draw.text(
        (72, 1120),
        "Kept canonical: shortening only name ID 6 creates hard Google-profile failures.",
        font=label,
        fill=MUTED,
    )
    footer(draw, image.height, "Mono italic VF and Sans/Mono italic statics")
    image.save(OUTPUT / "issue-20-name-length.png", optimize=True)


def draw_shaping_row(
    draw: ImageDraw.ImageDraw,
    y: int,
    title: str,
    sample: str,
    path: Path,
) -> None:
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 22)
    draw.text((72, y), title, font=label, fill=MUTED)
    draw.text((72, y + 42), sample, font=fit(path, sample, 1440, 82), fill=TEXT)


def render_issue_21() -> None:
    image, draw = canvas(
        21,
        "LANGUAGE SHAPING",
        "Exact characters and combining-mark sequences reported by Fontspector.",
        1300,
    )
    sans = SANS_DIR / "NamcheShadowSans-Regular.ttf"
    section(draw, 340, "Missing auxiliary characters")
    draw_shaping_row(draw, 405, "Danish · Catalan · Finnish · German / French", "Ǿ ǿ   Ĕ Ĭ Ŀ Ŏ   Ȟ Ʒ Ǯ   ſ ʻ", sans)
    section(draw, 575, "Cyrillic mark attachment")
    draw_shaping_row(draw, 640, "Serbian circumflex · Bulgarian grave", "а̂ е̂ и̂ о̂ у̂    а̀ о̀ у̀ ъ̀ ю̀ я̀", sans)
    draw_shaping_row(draw, 790, "Ukrainian / Belarusian / Russian acute", "а́ е́ є́ и́ і́ ї́ о́ у́ ы́ э́ ю́ я́", sans)
    section(draw, 965, "Soft-dotted behavior")
    draw_shaping_row(draw, 1030, "The base dot should disappear under these marks", "і́   į̄ į̌ į̂ į̀ į̃ į́   ị̄ ị̂", sans)
    footer(draw, image.height, "NamcheShadowSans-Regular.ttf · Unicode combining sequences")
    image.save(OUTPUT / "issue-21-language-shaping.png", optimize=True)


def render_issue_22() -> None:
    image, draw = canvas(
        22,
        "VARIABLE INTERPOLATION",
        "Reported glyphs rendered across the full Namche Shadow Sans weight axis.",
        1450,
    )
    glyphs = [("ţ", "uni0163"), ("ª", "ordfeminine"), ("Ѳ", "uni0472"), ("ө", "uni04E9"), ("&", "ampersand")]
    weights = [100, 200, 400, 700, 900]
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 20)
    for column, weight in enumerate(weights):
        x = 245 + column * 260
        draw.text((x + 55, 345), str(weight), font=label, fill=MUTED)
    for row, (character, glyph_name) in enumerate(glyphs):
        y = 405 + row * 185
        draw.text((72, y + 68), glyph_name, font=label, fill=MUTED)
        for column, weight in enumerate(weights):
            x = 245 + column * 260
            variable = font(SANS_VF, 148, weight)
            box = draw.textbbox((0, 0), character, font=variable)
            glyph_width = box[2] - box[0]
            draw.text((x + (190 - glyph_width) / 2, y), character, font=variable, fill=TEXT)
    footer(draw, image.height, "NamcheShadowSans[wght].ttf · weights 100, 200, 400, 700, 900")
    image.save(OUTPUT / "issue-22-variable-interpolation.png", optimize=True)


def render_issue_23() -> None:
    image, draw = canvas(
        23,
        "OUTLINE & METRICS TRIAGE",
        "Representative warning groups; this panel is for visual classification, not an automatic fix.",
        1280,
    )
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 22)
    section(draw, 340, "Math-sign widths")
    draw.text((72, 410), "SANS", font=label, fill=MUTED)
    draw.text((250, 385), "− + × ÷ = ≠ ± ≈ < >", font=font(SANS_DIR / "NamcheShadowSans-Regular.ttf", 82), fill=TEXT)
    draw.text((72, 520), "MONO", font=label, fill=MUTED)
    draw.text((250, 495), "− + × ÷ = ≠ ± ≈ < >", font=font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 82), fill=TEXT)
    section(draw, 650, "Pixel coverage / feature warnings")
    pixel_samples = [
        ("CIRCLE", PIXEL_DIR / "NamcheShadowPixel-Circle.ttf"),
        ("GRID", PIXEL_DIR / "NamcheShadowPixel-Grid.ttf"),
        ("LINE", PIXEL_DIR / "NamcheShadowPixel-Line.ttf"),
    ]
    for index, (style, path) in enumerate(pixel_samples):
        y = 720 + index * 120
        draw.text((72, y + 22), style, font=label, fill=MUTED)
        draw.text((300, y), "◌ · ₹ ﬁ ﬂ ‐", font=font(path, 72), fill=TEXT)
    draw.text((72, 1110), "A box or fallback shape makes a missing glyph immediately visible.", font=label, fill=MUTED)
    footer(draw, image.height, "Sans/Mono Regular and Pixel Circle/Grid/Line statics")
    image.save(OUTPUT / "issue-23-outline-metrics.png", optimize=True)


def render_issue_24() -> None:
    image, draw = canvas(
        24,
        "OPENTYPE VENDOR ID",
        "The four-byte OS/2 identifier is consistent in the current Namche binaries.",
        950,
    )
    rows = [
        ("SANS", SANS_DIR / "NamcheShadowSans-Regular.ttf"),
        ("MONO", MONO_DIR / "NamcheShadowMono-Regular.ttf"),
        ("PIXEL", PIXEL_DIR / "NamcheShadowPixel-Circle.ttf"),
    ]
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 24)
    for index, (family, path) in enumerate(rows):
        ttfont = TTFont(path, lazy=True)
        vendor = ttfont["OS/2"].achVendID
        ttfont.close()
        y = 365 + index * 155
        draw.text((72, y + 46), family, font=label, fill=MUTED)
        draw.text((310, y), vendor, font=fit(path, vendor, 700, 112), fill=TEXT)
        draw.text((1080, y + 46), "UNREGISTERED", font=label, fill=RED)
    footer(draw, image.height, "OS/2.achVendID · registration remains an administrative follow-up")
    image.save(OUTPUT / "issue-24-vendor-id.png", optimize=True)


def render_issue_25() -> None:
    image, draw = canvas(
        25,
        "PIXEL METADATA",
        "Every product style now carries the same Namche vendor and Latin language declarations.",
        1170,
    )
    label = font(MONO_DIR / "NamcheShadowMono-Regular.ttf", 21)
    styles = ["Circle", "Grid", "Line", "Square", "Triangle"]
    for index, style in enumerate(styles):
        path = PIXEL_DIR / f"NamcheShadowPixel-{style}.ttf"
        ttfont = TTFont(path, lazy=True)
        vendor = ttfont["OS/2"].achVendID
        language = ttfont["meta"].data
        ttfont.close()
        y = 350 + index * 145
        draw.text((72, y + 38), style.upper(), font=label, fill=MUTED)
        draw.text((320, y), "Aa 0123", font=font(path, 72), fill=TEXT)
        draw.rounded_rectangle((835, y + 10, 1005, y + 72), 14, fill=BLUE)
        draw.rounded_rectangle((1025, y + 10, 1205, y + 72), 14, fill=YELLOW)
        draw.rounded_rectangle((1225, y + 10, 1485, y + 72), 14, fill=PURPLE)
        draw.text((875, y + 27), vendor, font=label, fill=TEXT)
        draw.text((1060, y + 27), f"dlng {language.get('dlng')}", font=label, fill=TEXT)
        draw.text((1265, y + 27), f"slng {language.get('slng')}", font=label, fill=TEXT)
    footer(draw, image.height, "Pixel TTF statics · OS/2 and meta tables")
    image.save(OUTPUT / "issue-25-pixel-metadata.png", optimize=True)


def main() -> None:
    if not features.check_feature("raqm"):
        raise SystemExit(
            "Pillow must be built with RAQM support to render reliable shaping proofs."
        )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    render_issue_20()
    render_issue_21()
    render_issue_22()
    render_issue_23()
    render_issue_24()
    render_issue_25()
    for path in sorted(OUTPUT.glob("issue-*.png")):
        print(f"Wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
