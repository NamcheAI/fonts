"""Render zoomed side-by-side proofs of one glyph across several radii.

Usage: zoom_proof.py <glyph> [x0 y0 x1 y1] [--radii 0,20,40,80]
Writes exports/_preview_proofs/zoomstrip_<glyph>.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import cairosvg

sys.path.insert(0, str(Path(__file__).resolve().parent))
import round_inner_corners as ric  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "exports" / "_preview_proofs"


def glyph_box(pkg, name: str, pad: float = 30.0):
    paths, _ = ric.load_filleted_layer(pkg, name, "Regular", 0)
    xs, ys = [], []
    for p in paths:
        for x, y, _t in p:
            xs.append(x)
            ys.append(y)
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def strip(name: str, box=None, radii=(0, 20, 40, 80), scale: float = 3.0, tag=None) -> Path:
    pkg = ric.default_original_package()
    x0, y0, x1, y1 = box or glyph_box(pkg, name)
    w, h, gap = x1 - x0, y1 - y0, 30.0
    parts = []
    for i, r in enumerate(radii):
        paths, _ = ric.load_filleted_layer(pkg, name, "Regular", r)
        d = ric.node_paths_to_evenodd_svg_d(paths)
        ox = i * (w + gap)
        parts.append(
            f'<g transform="translate({ox},0)">'
            f'<clipPath id="c{i}"><rect x="{x0}" y="{-y1}" width="{w}" height="{h}"/></clipPath>'
            f'<g clip-path="url(#c{i})">'
            f'<rect x="{x0}" y="{-y1}" width="{w}" height="{h}" fill="#111318"/>'
            f'<g transform="scale(1,-1)">'
            f'<path d="{d}" fill="#e9ebe7" fill-rule="evenodd"/></g></g>'
            f'<text x="{x0 + 12}" y="{-y1 + 40}" fill="#5cc8ff" font-size="34" '
            f'font-family="monospace">r={r}</text></g>'
        )
    tot = len(radii) * w + (len(radii) - 1) * gap
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {-y1} {tot} {h}">'
        + "".join(parts)
        + "</svg>"
    )
    OUT.mkdir(parents=True, exist_ok=True)
    # The working tree lives on a case-insensitive volume, so "m" and "M" would
    # otherwise overwrite each other.
    label = tag or (f"{name}_uc" if name.isupper() else name)
    png = OUT / f"zoomstrip_{label}.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(png), output_width=int(tot * scale))
    return png


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    radii = (0, 20, 40, 80)
    for a in sys.argv[1:]:
        if a.startswith("--radii"):
            radii = tuple(int(v) for v in a.split("=", 1)[1].split(","))
    glyph = args[0]
    box = tuple(float(v) for v in args[1:5]) if len(args) >= 5 else None
    print(strip(glyph, box, radii))
