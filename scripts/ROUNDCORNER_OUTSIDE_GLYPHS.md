# RoundCorner outside Glyphs (research notes)

Can Namche soft-inners be driven without Glyphs.app — via Cursor raw data, CLI, RoboFont, FontLab, or an interactive local app?

Related ops docs: [`NAMCHE_SHADOW.md`](NAMCHE_SHADOW.md) · [`LEARNINGS.md`](../../LEARNINGS.md)

**Families (2026-08-11):** **Namche-Shadow** = multi-tier stack · **Namche-Shadow-Simple** = −40/−25. Temporary name *Namche-Darth* is retired.

## Short answer

| Question | Answer |
|----------|--------|
| Edit radii / include–exclude lists in git (Cursor)? | **Yes** — paste files, `fontinfo.plist`, `apply_roundcorner_filters.py` |
| Apply Glyphs RoundCorner (actually round outlines)? | **Only reliably in Glyphs.app** static export |
| Drop-in via RoboFont / FontLab / `glyphs-cli` / `fontmake`? | **No** — different model or proven non-application |
| Interactive local app? | **Yes, with trade-offs** — see [Interactive app](#interactive-app) |

## Glyphs model (what we ship)

- RoundCorner is a **Glyphs export Filter** on static instances, not baked into master outlines.
- Negative radius → **inner** (concave) corners; positive → outer. Stacks + `include:` / `exclude:` control per-glyph recipes.
- Official form: `RoundCorner; Radius; Visual Corrections` ([handbook](https://handbook.glyphsapp.com/filters/round-corners/)); we use GUI-native strings like `RoundCorner;-40;include:…` (see [`LEARNINGS.md`](../../LEARNINGS.md)).
- VF instance: RoundCorner **off** (outline compatibility).

Cursor can change the **recipe**. Glyphs must still **run** it on export.

## Why CLI / Cursor export failed

[`glyphs-cli`](https://pypi.org/project/glyphs-cli/) and `fontmake` do **not** reliably apply Glyphs RoundCorner instance filters. Evidence (Regular `H`):

| Export | `curveTo` on `H` |
|--------|------------------|
| Glyphs GUI (good) | **4** (inners rounded) |
| `glyphs-cli` (with/without native Filter string) | **0** (sharp) |

`ufo2ft` has its own filter mechanism; it is **not** Glyphs RoundCorner. Prefer **File → Export…** in Glyphs (or a Macro calling `font.export`). Details: [`LEARNINGS.md`](../../LEARNINGS.md).

## RoboFont

RoboFont can round corners (e.g. **CornerTools**, **RoundingUFO** — black/white corners, batch presets), but:

- It does **not** execute Glyphs `Filter` custom parameters.
- Sources here are **`.glyphspackage`**, not UFO — conversion (`glyphspkg` → `.glyphs` → UFO) is a separate pipeline.
- Optics and multi-tier include/exclude stacks are **not 1:1** with Glyphs RoundCorner.

Useful as a different design tool; **not** a drop-in for the shipping recipe.

## FontLab (brief)

**Smart Corners** are a live per-node effect (radius / ink trap), expanded on export. Powerful, but another format/product — does not read our Glyphs Filter strings.

## Repo alternative (legacy fillet)

[`round_inner_corners.py`](round_inner_corners.py) — experimental Python/pathops fillet that **bakes** inner rounds into `.glyphspackage` outlines. Deprecated; not the shipping path. Limits: global radius (not multi-tier), proof-subset defaults, VF point-count issues.

Current [`inner_round_app.py`](inner_round_app.py) is a **static specimen** only (serves already-exported OTFs/WOFFs). It does not run RoundCorner or the fillet engine live.

## Interactive app

An interactive UI **is possible**. The browser cannot run Glyphs RoundCorner. Realistic options:

| Approach | What the UI does | Matches Glyphs shipping optics? |
|----------|------------------|----------------------------------|
| **A. Pack switcher** | Sliders/buttons swap **pre-exported** static packs (e.g. several radii / Shadow vs Simple) | **Yes**, if packs came from Glyphs GUI |
| **B. Live fillet** | Re-attach `round_inner_corners.py` (or similar) → live SVG / on-demand TTF | **Approximate** — not identical to multi-tier RoundCorner |
| **C. Recipe UI** | Edit Filter strings / paste files / plist; user still exports in Glyphs | **Yes** after Glyphs export |

Recommendation if we build one: start with **A** for proofing shipping fonts; consider **B** only if we explicitly want a Glyphs-free experiment; use **C** to make Cursor/recipe edits less error-prone.

## Decision matrix

| Goal | Best option |
|------|-------------|
| Ship Namche-Shadow / Shadow-Simple | Glyphs GUI export + recipe files in git |
| Tweak radii/lists quickly | Cursor → paste / plist / `apply_roundcorner_filters.py`, then Glyphs re-export |
| Interactive comparison without waiting on Glyphs each click | Pack switcher (A) of GUI-exported builds |
| Fully Glyphs-free live rounding | Legacy/modern fillet (B) — new calibration, not production default |
| RoboFont as main editor | New UFO workflow + new rounding model — high cost |

## Recommendation

1. Keep **Glyphs RoundCorner** as the production path.
2. Do **not** treat RoboFont / `glyphs-cli` / `fontmake` as RoundCorner substitutes.
3. An **interactive specimen** is worthwhile as a pack switcher (and optional recipe editor); live fillet only as a documented experiment.

## External references

- [Glyphs — Round Corners](https://handbook.glyphsapp.com/filters/round-corners/)
- [Glyphs — Applying filters](https://handbook.glyphsapp.com/filters/applying/)
- [RoboFont — RoundingUFO](https://extensionstore.robofont.com/extensions/roundingUFO/)
- [glyphsLib `.glyphspackage` support discussion](https://github.com/googlefonts/glyphsLib/issues/801)
