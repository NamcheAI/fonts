# -*- coding: utf-8 -*-
"""
Glyphs Macro / Script: export Namche-Shadow static OTFs with RoundCorner filters.

Usage in Glyphs 4:
  1. Open exports/Namche-Shadow/Namche-Shadow.glyphspackage
  2. Window → Macro Panel (or Scripts menu if installed)
  3. Paste/run this file
"""
from __future__ import print_function
import os

OUT = "/Users/mitch/Library/CloudStorage/GoogleDrive-michael@ruhmetc.com/Geteilte Ablagen/Projekte/Hagen & Partner/P297 Hagen Partner Branding/03_Entwurf/Schrift/Entwurf/geist-font-main/exports/Namche-Shadow/otf"

font = Glyphs.font
if font is None:
    raise Exception("Open Namche-Shadow.glyphspackage first")

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
