# Changelog

All notable releases of this font family are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/). Version numbers follow [VERSIONING.md](VERSIONING.md).

## [Unreleased]

### Changed
- Fixed leftover **Namche-Darth** VF `fileName` and trailing commas in RoundCorner glyph lists (2026-08-11d package hygiene)
- Production path pivoted to **Glyphs RoundCorner** export filters; VF filters disabled
- **Family rename (2026-08-11):** multi-tier stack is **Namche-Shadow**; prior −40/−25 recipe is **Namche-Shadow-Simple** (retired temporary name **Namche-Darth**)
- **Namche-Shadow** multi-tier stack updated (**2026-08-11d**, 6 filters): −60 exclude → −80 include → −60 (`A,V,Z,X,Germandbls`) → −50 (`k,x,v,w`) → −40 (`M,N,W,two,four,seven,six`) → −50 (`nine`); VF RoundCorner off
- Specimen `PREVIEW_FAMILIES` = Shadow + Shadow-Simple; installs under `~/Library/Fonts/Namche-Shadow{,-Simple}/`
- Local preview app serves static `woff2` / `woff` / `otf` with a family switcher
- Docs rewritten for RoundCorner delivery (`README.md`, `scripts/NAMCHE_SHADOW.md`, `VERSIONING.md`, `LEARNINGS.md`)
- Scope clarified as Namche-only; attribution added for designer Michael Marte and tooling assistance

### Added
- [`scripts/ROUNDCORNER_OUTSIDE_GLYPHS.md`](scripts/ROUNDCORNER_OUTSIDE_GLYPHS.md): research on RoundCorner outside Glyphs (CLI, RoboFont, FontLab) and interactive-app options
- **Namche-Shadow-Simple** recipe: caps/figures **−40**, rest **−25**
- Multi-tier paste file `scripts/roundcorner_shadow_filters.txt` + Glyphs export macro `glyphs_export_namche_shadow.py`
- `scripts/apply_roundcorner_filters.py` with `--strong` / `--mild` radius args (Glyphs-native Filter string; Simple pairs)
- Archive paths for manual Glyphs drops: `exports/Namche-*/_received/` (avoids clobbering identically named `Geist.glyphspackage` / `Geist-*.otf`)
- [`LEARNINGS.md`](LEARNINGS.md): `glyphs-cli` RoundCorner failure, Downloads naming collisions, verification checklist
- Web formats in local delivery folders (`woff/`, `woff2/`)
- Immutable Geist Sans upright safecopy (`originals/geist/`)

### Deprecated
- Python inner-fillet engine (`scripts/round_inner_corners.py`) — legacy experiment, not the shipping pipeline

## [0.1.0] — 2026-08-10

### Added
- Initial public repository layout for Namche type work
- Versioning policy and release checklist
- Attribution for Michael Marte as designer; Cursor is credited only for tooling assistance
