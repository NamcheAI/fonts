# Namche Shadow Sans: statics with multi-tier RoundCorner

**Status (2026-08-13):** in scope for design and packaging.  
**Audience:** Jodok (build / npm / VF) and anyone exporting or consuming Namche Shadow Sans.

Please use the **static** Namche-Shadow weights that Michael exports from Glyphs with the **multi-tier RoundCorner** stack. A source-built **variable font does not get those filters** and is **out of scope** for the designed family.

---

## In scope

| Item | What to use |
|------|-------------|
| Look | Glyphs **File → Export…** of **static** instances (Thin → Black) |
| Recipe | Multi-tier RoundCorner on those statics — paste [`scripts/roundcorner_shadow_filters.txt`](../scripts/roundcorner_shadow_filters.txt) |
| Last known-good binaries | `exports/Namche-Shadow/_received/2026-08-11d-*` (6-filter GUI OTFs) |
| npm / Next | Static path: `@namche/namche-shadow/font/sans-non-variable` (or the default package statics) |
| Proof | After export, check inner corners on `H` / `E` / `a` (Regular `H` should have **4** `curveTo`s) |

Details and paste order: [`scripts/NAMCHE_SHADOW.md`](../scripts/NAMCHE_SHADOW.md). Why GUI export, not CLI: [`LEARNINGS.md`](../LEARNINGS.md).

---

## Out of scope

Do **not** spend time on these for Namche Shadow Sans:

1. **RoundCorner (or any outline-rewriting Filter) on the variable instance.** Glyphs cannot apply the multi-tier stack to a VF. Rounding changes node counts per weight → incompatible masters.
2. **A “rounded VF” from interpolating masters** (`fontmake` / `gftools` / `make build` on `sources/NamcheShadowSans.glyphspackage`). That pipeline does not run Glyphs RoundCorner. The result is Geist-like interpolation, not the designed inner-corner treatment.
3. **Serving that VF as the Sans face** (`@namche/namche-shadow/font/sans` → `NamcheShadowSans-Variable.woff2`). That is not the shipping look.
4. **Continuing the 2026-08-13 experiments** in `Namche-Shadow-Edited.glyphspackage` (Remove Glyphs, parked ѫ μ ฿ ₱, class edits, `export = 0`). That session mixed VF export, feature-class errors, and filter tests. It is **messy and not production**.

Mono and Pixel may keep variable fonts: they are still upstream outlines, not Michael’s RoundCorner treatment.

---

## Why filters do not apply on variable export

RoundCorner runs **per static instance at Glyphs export**, after interpolation to that weight. Each static file is a finished outline.

A variable font needs **one compatible outline per master**. If you round at export, Thin and Black no longer share point counts. Glyphs reports incompatible masters. That is a platform limit, not a missing checkbox.

So for Namche Shadow Sans:

- **Statics** = designed product (multi-tier inner rounds).
- **VF** = optional later research, not current delivery.

---

## Current mess (do not build on it)

| Attempt | What happened |
|---------|----------------|
| `cc03f97` — “build the Namche Shadow Sans variable font” | Wired npm `font/sans` to a source-built VF and treated interpolated masters as the rounded family. Closes the wrong problem. |
| `Namche-Shadow-Edited.glyphspackage` | Local Glyphs copy used to test Remove Glyphs / VF export. Saving from Glyphs overwrote disk edits; feature classes still named removed glyphs (`AllLetters`, `AllLetters_Symbols_etc`). |
| Parked glyphs ѫ μ ฿ ₱ (`yusbig-cy`, `mu`, `baht`, `peso`) | Need manual compatibility work. Not a reason to ship a VF. |

Until Michael drops a new GUI static set, packaging should track **2026-08-11d static OTFs**, not the Edited package and not `make build` VF output.

---

## What to do in the repo / npm

1. Point the **designed Sans** at **static** RoundCorner OTFs (Glyphs GUI), not `NamcheShadowSans-Variable.woff2`.
2. Leave RoundCorner **off** on the variable instance if a VF is built at all (Mono/Pixel, or a non-shipping Sans VF).
3. Do not merge further “make Sans VF interpolation-compatible so filters apply” work — they will not apply.
4. Ignore the Edited-package / parked-glyph session for releases.

Questions about the multi-tier recipe go to Michael. Packaging questions can stay on the PR/issue that lands this note.
