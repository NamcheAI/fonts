# Geist Inner Round tool

Interactive preview + export for rounded **inner** corners (sharp outer corners).

## Paths

| Path | Role |
|------|------|
| `../geist-font-original/` | **Immutable** pristine Geist Sans upright sources |
| `scripts/inner_round_app.py` | Local web UI |
| `scripts/round_inner_corners.py` | Fillet engine + CLI |
| `exports/Geist-inner-r{N}/` | Export output (glyphspackage + TTF) |

`geist-font-main.zip` is **not** used as the original (it already contained filleted outlines).

## Run the UI

```bash
cd geist-font-main
python3 scripts/inner_round_app.py
# → http://127.0.0.1:8765
```

Uses `.venv-inner-round` automatically when present (created for `fontmake`).

## Export

In the UI: set radius → **Export font**.

Writes:

- `exports/Geist-inner-r{N}/Geist.glyphspackage` (open in Glyphs)
- `exports/Geist-inner-r{N}/ttf/Geist-{Thin,Regular,Black}.ttf` (installable masters)

Variable / intermediate instances are skipped when fillet radii change point counts across masters (open the `.glyphspackage` in Glyphs for full VF export after cleanup).

## CLI

```bash
# Reset working sources from the immutable original
python3 scripts/round_inner_corners.py --reset-sources

# Batch fillet into a package (reads --package; prefer exporting via the UI from original)
python3 scripts/round_inner_corners.py --package ../geist-font-original/sources/Geist.glyphspackage \
  --write --radius 40
```

**Never edit files under `geist-font-original/`.**
