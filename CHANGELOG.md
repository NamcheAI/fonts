# Changelog

All notable releases of this font family are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/). Version numbers follow [VERSIONING.md](VERSIONING.md).

## [Unreleased]

### Changed
- Production path pivoted to **Glyphs RoundCorner** export filters (caps/figures **−40**, rest **−25**; VF filters disabled)
- Local preview app serves static **Namche-Shadow** `woff2` / `woff` / `otf` from `exports/Namche-Shadow/`
- Docs rewritten for RoundCorner delivery (`README.md`, `scripts/NAMCHE_SHADOW.md`, `VERSIONING.md`)
- Delivery family name set to **Namche-Shadow** (export folders, Glyphs `familyName`, filenames)
- Scope clarified as Namche-only; attribution added for Michael Marte and Cursor AI

### Added
- `scripts/apply_roundcorner_filters.py` + paste file for RoundCorner filter strings
- Web formats in local delivery folder (`woff/`, `woff2/`)
- Immutable Geist Sans upright safecopy (`geist-font-original/`)

### Deprecated
- Python inner-fillet engine (`scripts/round_inner_corners.py`) — legacy experiment, not the shipping pipeline

## [0.1.0] — 2026-08-10

### Added
- Initial public repository layout for Namche type work
- Versioning policy and release checklist
- Attribution for Michael Marte and Cursor AI as Namche-Shadow authors
