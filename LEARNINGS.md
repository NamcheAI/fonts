# Learnings & findings (Namche RoundCorner)

Operational notes from shipping **Namche-Shadow** (multi-tier) and **Namche-Shadow-Simple** (−40/−25) via Glyphs RoundCorner. Recipe details live in [`geist-font-main/scripts/NAMCHE_SHADOW.md`](geist-font-main/scripts/NAMCHE_SHADOW.md). Research on CLI / RoboFont / interactive apps: [`geist-font-main/scripts/ROUNDCORNER_OUTSIDE_GLYPHS.md`](geist-font-main/scripts/ROUNDCORNER_OUTSIDE_GLYPHS.md).

## Production path

- **Ship with Glyphs RoundCorner export filters**, not the experimental Python inner-fillet engine (`scripts/round_inner_corners.py`).
- Filters live on **static instances** only. Keep RoundCorner **off** on the variable instance — otherwise Glyphs reports incompatible masters after contours diverge per weight.
- Upstream/`geist-font-original/` stays **Geist** and immutable. Delivery family names (`Namche-Shadow`, `Namche-Shadow-Simple`) are set at export / name-table rewrite.

## Family naming (resolved 2026-08-11)

| Family | Role | Recipe |
|--------|------|--------|
| **Namche-Shadow** | Primary | Multi-tier (2026-08-11d): −60 exclude → −80 include → −60 (`A,V,Z,X,Germandbls`) → −50 (`k,x,v,w`) → −40 (`M,N,W,two,four,seven,six`) → −50 (`nine`) |
| **Namche-Shadow-Simple** | Prior recipe | Two-radius: caps/figures −40 include, rest −25 exclude |

The temporary name **Namche-Darth** for the multi-tier stack is **retired**. Older docs/commits may still mention it.

## `glyphs-cli` / Cursor cannot replace Glyphs GUI export

Automated export with [`glyphs-cli`](https://pypi.org/project/glyphs-cli/) (`glyphs export --app 4 --plugins …`) **does not reliably apply RoundCorner instance filters**.

| Evidence (Regular `H`) | `curveTo` count |
|------------------------|-----------------|
| Glyphs GUI export (good) | **4** (inners rounded) |
| `glyphs-cli` (Filter with `;1;` slot) | **0** (sharp) |
| `glyphs-cli` (GUI-native Filter string + explicit RoundCorner plugin) | **0** (still sharp) |

Also: bad CLI Regular OTFs were ~71 KB vs ~92 KB for correctly rounded GUI exports.

**Rule:** For shipping binaries, use **File → Export… in Glyphs.app** (or a Glyphs Macro that calls `font.export`). After any automated export, proof an inner-corner glyph (`H`, `E`, `a`).

Filter **string format** still matters for packages that open correctly in Glyphs:

- Prefer GUI-native: `RoundCorner;-60;include:A,…` (no `;1;` visual-correctness slot, no space after `:`).
- Order for multi-tier stacks is significant — paste / apply in the documented order (see paste file).

Accessibility / AppleScript automation of Glyphs UI from Cursor may be blocked; do not rely on it.

## Downloads naming collisions

Glyphs often exports as `Geist.glyphspackage` / `Geist-*.otf` regardless of intended Namche family.

- **Always archive** under dated `exports/<Family>/_received/…` before overwriting delivery.
- Never drop Downloads onto `geist-font-original/` or blindly onto `exports/Namche-Shadow/otf/`.
- Confirm recipe with outline fingerprints (or known-good hash) before renaming — multi-tier and −40/−25 can both arrive as `Geist-*.otf`.

## Verification checklist (after every GUI export)

1. File size in the rounded ballpark (~90 KB+ Regular), not the sharp CLI size (~71 KB).
2. Regular `H` has inner `curveTo`s (expect **4** for these recipes).
3. Name tables: family **Namche-Shadow** or **Namche-Shadow-Simple** (not Geist).
4. Compare a few diagonals (`A`, `V`, `M`) if both families exist — multi-tier and Simple must differ.
5. Rebuild `woff` / `woff2`; refresh `~/Library/Fonts/<Family>/` and the `:8765` specimen.

## Tooling split

| Tool | Use for |
|------|---------|
| `apply_roundcorner_filters.py` | Two-radius pairs (**Shadow-Simple** / experiments) |
| `roundcorner_shadow_filters.txt` | Multi-tier **Namche-Shadow** paste into Glyphs statics |
| `glyphs_export_namche_shadow.py` | Glyphs Macro → export OTFs into `exports/Namche-Shadow/otf/` |
| `inner_round_app.py` | Local specimen (`PREVIEW_FAMILIES`) |

Multi-tier is maintained in Glyphs / the paste file; the two-radius Python helper is not a substitute for that stack.

## Local delivery layout

```
geist-font-main/exports/
  Namche-Shadow/           # primary multi-tier + package + _received
  Namche-Shadow-Simple/    # −40/−25 + package + _received
```

`exports/` is gitignored; binaries ship on GitHub Releases. Docs and scripts in git are the reproducible recipe.

## Package hygiene after renames

When renaming families (e.g. temporary **Namche-Darth** → **Namche-Shadow**), rewrite not only `familyName` and OTF name tables but also instance `fileName` custom parameters (VF often keeps `Namche-Darth[wght]`). Strip trailing commas in RoundCorner `include:` / `exclude:` glyph lists — Glyphs paste can leave `six, ` which should be `six`.

