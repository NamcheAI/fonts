# Namche Fonts

Custom type for Namche, based on Geist Sans with **Glyphs RoundCorner** export filters (softer inner corners; sharp outers stay crisp).

## Families

| Family | Recipe | Notes |
|--------|--------|-------|
| **Namche-Shadow** | multi-tier 6-filter (see docs) | Primary — specimen + `~/Library/Fonts` |
| **Namche-Shadow-Simple** | caps/figures **−40**, rest **−25** | Prior two-radius recipe — specimen + `~/Library/Fonts` |

Variable instance filters stay **disabled** (VF export incompatible after rounding). Upstream sources stay named Geist; delivery names are set at export.

> The multi-tier family was briefly called **Namche-Darth**; that name is retired.

## Layout

| Path | Role |
|------|------|
| [`geist-font-original/`](geist-font-original/) | Immutable pristine Geist upright sources — **do not edit** |
| [`geist-font-main/sources/`](geist-font-main/sources/) | Working Glyphs package (Simple −40/−25 filters) |
| [`geist-font-main/scripts/apply_roundcorner_filters.py`](geist-font-main/scripts/apply_roundcorner_filters.py) | Writes two-radius RoundCorner filters (`--strong` / `--mild`) |
| [`geist-font-main/scripts/inner_round_app.py`](geist-font-main/scripts/inner_round_app.py) | Local static specimen (woff2 / woff / otf) |
| `geist-font-main/exports/Namche-Shadow/` | Primary Shadow delivery + package + `_received` — gitignored |
| `geist-font-main/exports/Namche-Shadow-Simple/` | Simple delivery + package + `_received` — gitignored |
| [`VERSION`](VERSION) / [`VERSIONING.md`](VERSIONING.md) / [`CHANGELOG.md`](CHANGELOG.md) | Releases |
| [`AUTHORS.txt`](AUTHORS.txt) / [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt) | Attribution |

Details: [`geist-font-main/scripts/NAMCHE_SHADOW.md`](geist-font-main/scripts/NAMCHE_SHADOW.md) · operational findings: [`LEARNINGS.md`](LEARNINGS.md) · RoundCorner outside Glyphs / interactive app: [`ROUNDCORNER_OUTSIDE_GLYPHS.md`](geist-font-main/scripts/ROUNDCORNER_OUTSIDE_GLYPHS.md)

## Quick start (specimen)

```bash
cd geist-font-main
python3 scripts/inner_round_app.py
# → http://127.0.0.1:8765  (Namche-Shadow + Namche-Shadow-Simple)
```

## Build notes

**Namche-Shadow-Simple** (recipe −40 / −25):

```bash
cd geist-font-main
python3 scripts/apply_roundcorner_filters.py --strong -40 --mild -25
# Open sources in Glyphs → export statics → rename to Namche-Shadow-Simple → woff/woff2
```

**Namche-Shadow** (multi-tier) — package under `exports/Namche-Shadow/` and paste file `scripts/roundcorner_shadow_filters.txt`. Export statics in Glyphs (VF RoundCorner off). See [`NAMCHE_SHADOW.md`](geist-font-main/scripts/NAMCHE_SHADOW.md).

Ship binaries on GitHub Releases — see **[VERSIONING.md](VERSIONING.md)**.

> Legacy: `scripts/round_inner_corners.py` is an experimental Python fillet engine, not the production pipeline.

## Versioning

See **[VERSIONING.md](VERSIONING.md)**. Short version: SemVer in `VERSION`, tags as `vMAJOR.MINOR.PATCH`, changelog required for every release, binaries attached to GitHub Releases.

## Credits

- **Michael Marte** — Namche design direction and contribution
- **Cursor AI** — co-author, tooling and repository setup
- Based on [Geist](https://github.com/vercel/geist-font) (SIL Open Font License 1.1)
