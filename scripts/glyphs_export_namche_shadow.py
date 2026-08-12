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

OUT = os.path.expanduser("~/Desktop/NamcheShadowSans/otf")

font = Glyphs.font
if font is None:
    raise Exception("Open NamcheShadowSans.glyphspackage first")

if not os.path.isdir(OUT):
    os.makedirs(OUT)

# Prefer active font; export instances (RoundCorner runs here in Glyphs GUI)
result = font.export(
    Format=OTF,
    FontPath=OUT,
    AutoHint=False,
    RemoveOverlap=True,
    UseProductionNames=True,
)
print("Exported to", OUT, "→", result)
# Quick proof: list files
print("Files:", sorted(os.listdir(OUT)))
