# -*- coding: utf-8 -*-
"""
Glyphs Macro / Script: export Namche Shadow Sans static OTFs with RoundCorner filters.

Usage in Glyphs 4:
  1. Open sources/NamcheShadowSans.glyphspackage
  2. Window → Macro Panel (or Scripts menu if installed)
  3. Paste/run this file
"""
from __future__ import print_function
import os

OUT = os.path.expanduser("~/Desktop/NamcheShadowSans")

font = Glyphs.font
if font is None:
    raise Exception("Open NamcheShadowSans.glyphspackage first")

for directory in ("otf", "ttf"):
    path = os.path.join(OUT, directory)
    if not os.path.isdir(path):
        os.makedirs(path)

# Export every active static instance in both formats. RoundCorner runs inside
# Glyphs; do not substitute glyphs-cli for this step.
for format_name, format_value in (("otf", OTF), ("ttf", TTF)):
    path = os.path.join(OUT, format_name)
    result = font.export(
        Format=format_value,
        FontPath=path,
        AutoHint=False,
        RemoveOverlap=True,
        UseProductionNames=True,
    )
    print("Exported", format_name.upper(), "to", path, "→", result)
    print("Files:", sorted(os.listdir(path)))
