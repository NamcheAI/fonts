# Versioning

This repository versions **released font builds** and the **inner-round tooling** that produces them.

## Scheme

We use **Semantic Versioning 2.0.0**: `MAJOR.MINOR.PATCH`

| Part | Bump when |
|------|-----------|
| **MAJOR** | Incompatible glyph / metric / name-table changes; breaking tool CLI or export layout |
| **MINOR** | New features that stay compatible (new radius presets, new masters, new scripts, non-breaking glyph additions) |
| **PATCH** | Bug fixes, proofing fixes, docs, and export polish that do not change public API / intended outlines in a breaking way |

Examples:

- `0.1.0` → `0.2.0` — new fillet algorithm option, new weight, or new documented radius line
- `0.2.0` → `0.2.1` — fix counter fill / preview bug; regenerate proofs
- `0.2.1` → `1.0.0` — first production brand delivery; metrics locked for clients

Pre-`1.0.0` versions may still change outlines aggressively; treat `0.x` as design iteration.

## What a version refers to

A released version is the combination of:

1. **Sources of truth**
   - `geist-font-original/` — immutable pristine Geist upright package (never edit)
   - `geist-font-main/scripts/` — fillet engine + UI used to generate variants
2. **Documented radius / style line** for that release (e.g. inner-round `r40`, `r80`)
3. **Exported binaries** attached to the GitHub Release (TTF / OTF / variable if available)

Git tags mark the **repo state** that produced those binaries. Binaries themselves live on the Release assets (not necessarily in git — `exports/` is gitignored and regenerated).

## Naming

| Artifact | Pattern | Example |
|----------|---------|---------|
| Git tag | `vMAJOR.MINOR.PATCH` | `v0.1.0` |
| Release title | `vMAJOR.MINOR.PATCH — short label` | `v0.1.0 — inner-round preview` |
| Export folder (local) | `Geist-inner-r{N}` | `exports/Geist-inner-r40/` |
| Font family (design) | Keep OFL / Geist attribution; document any renamed delivery name in the release notes | |

Radius `N` is **not** the semver. The same repo version can ship multiple radii; list them in the release notes.

## Single source of version number

- Canonical file: [`VERSION`](VERSION) (plain text, one line, no `v` prefix)
- [`CHANGELOG.md`](CHANGELOG.md) must gain a section for every released tag
- Git tag must match `VERSION` with a `v` prefix (`0.1.0` → `v0.1.0`)

Do not invent a second version string in font name tables until the brand delivery name is finalized; then record the mapping in the release notes.

## Release checklist

1. Confirm `geist-font-original/` is untouched.
2. Bump `VERSION`.
3. Update `CHANGELOG.md` (`Unreleased` → dated section).
4. Regenerate proofs / exports for the radii in this release:
   ```bash
   cd geist-font-main
   .venv-inner-round/bin/python scripts/inner_round_app.py
   # Export from UI, or use scripts/round_inner_corners.py
   ```
5. Commit on `main` with a message that states the version intent.
6. Tag and push:
   ```bash
   git tag -a "v$(cat VERSION)" -m "Release v$(cat VERSION)"
   git push origin main --tags
   ```
7. Create a GitHub Release for the tag; upload TTF (and glyphspackage if sharing sources) as assets.
8. In the release body, list:
   - radii shipped (`r40`, `r80`, …)
   - masters (`Thin` / `Regular` / `Black`, …)
   - known limitations (e.g. variable font skipped when masters are incompatible after filleting)

## Branching

- `main` — stable line; tagged releases only from here
- optional `release/x.y` — freeze line while finishing a delivery
- feature work — short-lived branches; merge via PR when collaborators are involved

## Compatibility notes for this project

- **Never edit** files under `geist-font-original/`. Reset working sources with:
  ```bash
  cd geist-font-main
  python3 scripts/round_inner_corners.py --reset-sources
  ```
- Filleting can change point counts across masters → variable font export may be skipped; that is a known limitation, not necessarily a version bump by itself.
- Preview server (`scripts/inner_round_app.py`, port `8765`) is a local tool and is not versioned as a service.

## Upstream attribution

Based on [Vercel Geist Font](https://github.com/vercel/geist-font) (OFL). Keep `OFL.txt` / `AUTHORS.txt` with distributed fonts. Custom inner-round work is additive; release notes should say which upstream Geist revision the safecopy came from when known.
