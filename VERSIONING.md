# Versioning

This repository versions **released Namche-Shadow font builds** and the tooling that prepares Glyphs RoundCorner filters / local proofs.

## Scheme

We use **Semantic Versioning 2.0.0**: `MAJOR.MINOR.PATCH`

| Part | Bump when |
|------|-----------|
| **MAJOR** | Incompatible glyph / metric / name-table changes; breaking tool CLI or export layout |
| **MINOR** | New features that stay compatible (new filter recipe, new weights, new scripts, non-breaking glyph additions) |
| **PATCH** | Bug fixes, proofing fixes, docs, and export polish that do not change public API / intended outlines in a breaking way |

Examples:

- `0.1.0` → `0.2.0` — new RoundCorner recipe (e.g. −40/−25 → different pair), new weight, or documented delivery format
- `0.2.0` → `0.2.1` — fix rename/packaging script; regenerate woff2; docs
- `0.2.1` → `1.0.0` — first production delivery; metrics locked

Pre-`1.0.0` versions may still change outlines aggressively; treat `0.x` as design iteration.

## What a version refers to

A released version is the combination of:

1. **Sources of truth**
   - `geist-font-original/` — immutable pristine Geist upright package (never edit)
   - `geist-font-main/sources/` — working Glyphs package with RoundCorner filters in `fontinfo.plist`
   - `geist-font-main/scripts/` — filter applicator + static specimen UI
2. **Documented filter recipe** for that release (e.g. caps/figures **−40**, rest **−25**; VF filters off)
3. **Exported binaries** attached to the GitHub Release (`otf` / `woff` / `woff2`, plus `ttf` VF if shipped)

Git tags mark the **repo state** that produced those binaries. Binaries themselves live on the Release assets (not necessarily in git — `exports/` is gitignored and regenerated).

## Naming

| Artifact | Pattern | Example |
|----------|---------|---------|
| Git tag | `vMAJOR.MINOR.PATCH` | `v0.1.0` |
| Release title | `vMAJOR.MINOR.PATCH — short label` | `v0.2.0 — RoundCorner −40/−25` |
| Export folder (local) | `Namche-Shadow` / `Namche-Shadow-Simple` | `exports/Namche-Shadow/` |
| Font family (name tables / Glyphs) | `Namche-Shadow` / `Namche-Shadow-Simple` | `Namche-Shadow-Regular.woff2` |

The RoundCorner radii are **not** the semver. Record each family’s filter recipe in the release notes (Shadow multi-tier; Shadow-Simple −40/−25).

## Single source of version number

- Canonical file: [`VERSION`](VERSION) (plain text, one line, no `v` prefix)
- [`CHANGELOG.md`](CHANGELOG.md) must gain a section for every released tag
- Git tag must match `VERSION` with a `v` prefix (`0.1.0` → `v0.1.0`)

Delivery family name is **Namche-Shadow** (set at export; `geist-font-original` stays Geist). Record filter recipe and masters in each release.

## Release checklist

1. Confirm `geist-font-original/` is untouched.
2. Bump `VERSION`.
3. Update `CHANGELOG.md` (`Unreleased` → dated section).
4. Refresh filters and regenerate delivery binaries:
   ```bash
   cd geist-font-main
   # Shadow-Simple (two-radius):
   python3 scripts/apply_roundcorner_filters.py --strong -40 --mild -25
   # Shadow (multi-tier): paste scripts/roundcorner_shadow_filters.txt in Glyphs
   # Export statics in Glyphs (VF RoundCorner off) → rename → woff/woff2
   python3 scripts/inner_round_app.py   # optional local proof
   ```
   See [`LEARNINGS.md`](LEARNINGS.md) before trusting any `glyphs-cli` export.
5. Commit on `main` with a message that states the version intent.
6. Tag and push:
   ```bash
   git tag -a "v$(cat VERSION)" -m "Release v$(cat VERSION)"
   git push origin main --tags
   ```
7. Create a GitHub Release for the tag; upload `otf` / `woff` / `woff2` (and glyphspackage if sharing sources) as assets.
8. In the release body, list:
   - RoundCorner recipe per family (Shadow multi-tier vs Shadow-Simple −40/−25)
   - masters shipped (Thin → Black, …)
   - whether a VF is included (unfiltered)
   - known limitations (VF incompatible with RoundCorner filters; GUI export required)

## Branching

- `main` — stable line; tagged releases only from here
- optional `release/x.y` — freeze line while finishing a delivery
- feature work — short-lived branches; merge via PR when collaborators are involved

## Compatibility notes for this project

- **Never edit** files under `geist-font-original/`.
- RoundCorner runs only inside **Glyphs at export**; `fontmake` does not apply Glyphs Filter custom parameters.
- Applying RoundCorner to the variable instance breaks VF compatibility — keep those filters disabled.
- Preview server (`scripts/inner_round_app.py`, port `8765`) serves static files only and is not versioned as a service.
- `scripts/round_inner_corners.py` is legacy experimental tooling, not the release pipeline.

## Upstream attribution

Based on [Vercel Geist Font](https://github.com/vercel/geist-font) (OFL). Keep `OFL.txt` with distributed fonts. Namche-Shadow authors and contributors are listed in root [`AUTHORS.txt`](AUTHORS.txt) / [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt) (Michael Marte; Cursor AI co-author). Release notes should say which upstream Geist revision the safecopy came from when known.
