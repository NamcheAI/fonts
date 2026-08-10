# Namche Fonts

**Namche-Shadow** — custom type for Namche, based on Geist Sans with **Glyphs RoundCorner** export filters (softer inner corners; sharp outers stay crisp).

## Filter recipe

| Target | RoundCorner |
|--------|-------------|
| Caps, figures, and cap/figure-like glyphs | **−40** (`include`) |
| Everything else | **−25** (`exclude` same set) |
| Variable instance | Filters **disabled** (VF export incompatible after rounding) |

Delivery family name is **Namche-Shadow**. Upstream sources stay named Geist.

## Layout

| Path | Role |
|------|------|
| [`geist-font-original/`](geist-font-original/) | Immutable pristine Geist upright sources — **do not edit** |
| [`geist-font-main/sources/`](geist-font-main/sources/) | Working Glyphs package (filters in `fontinfo.plist`) |
| [`geist-font-main/scripts/apply_roundcorner_filters.py`](geist-font-main/scripts/apply_roundcorner_filters.py) | Writes RoundCorner filters into static instances |
| [`geist-font-main/scripts/inner_round_app.py`](geist-font-main/scripts/inner_round_app.py) | Local static specimen (woff2 / woff / otf) |
| [`geist-font-main/exports/Namche-Shadow/`](geist-font-main/exports/Namche-Shadow/) | Local delivery folder (`otf/`, `woff/`, `woff2/`, `ttf/`, glyphspackage) — gitignored |
| [`VERSION`](VERSION) | Current release version |
| [`VERSIONING.md`](VERSIONING.md) | How we version, tag, and ship releases |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history |
| [`AUTHORS.txt`](AUTHORS.txt) / [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt) | Attribution |

Details: [`geist-font-main/scripts/NAMCHE_SHADOW.md`](geist-font-main/scripts/NAMCHE_SHADOW.md)

## Quick start (specimen)

```bash
cd geist-font-main
python3 scripts/inner_round_app.py
# → http://127.0.0.1:8765  (serves static woff2 / woff / otf)
```

Requires exported fonts under `exports/Namche-Shadow/` (see build notes below).

## Build notes

1. Keep `geist-font-original/` untouched. Work in `geist-font-main/sources/Geist.glyphspackage`.
2. Apply or refresh RoundCorner filters:
   ```bash
   cd geist-font-main
   python3 scripts/apply_roundcorner_filters.py
   ```
3. Open the package in **Glyphs** → export **static** instances (filters on). Leave the variable instance filters disabled.
4. Rename the family to **Namche-Shadow** (name tables / filenames) and package web formats into `exports/Namche-Shadow/` (`otf/`, `woff/`, `woff2/`, optional `ttf/` VF).

Ship binaries on GitHub Releases — see **[VERSIONING.md](VERSIONING.md)**.

> Legacy: `scripts/round_inner_corners.py` is an experimental Python fillet engine, not the production pipeline.

## Versioning

See **[VERSIONING.md](VERSIONING.md)**. Short version: SemVer in `VERSION`, tags as `vMAJOR.MINOR.PATCH`, changelog required for every release, binaries attached to GitHub Releases.

## Credits

- **Michael Marte** — Namche-Shadow design direction and contribution
- **Cursor AI** — co-author, tooling and repository setup
- Upstream **Geist** by Vercel / Basement Studio / Andrés Briganti (OFL) — see `AUTHORS.txt`

## License

Upstream Geist is licensed under the SIL Open Font License (`OFL.txt` in the Geist trees). Keep attribution with any redistributed font files.
