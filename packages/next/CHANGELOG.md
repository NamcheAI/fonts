# @namche/namche-shadow

## 0.1.1

### Patch Changes

- b33e7d9: Restore the intended weight-specific `0` outlines in Namche Shadow Sans.
- e0d5ce6: Apply the Namche Shadow inner-corner treatment to the Sans italic static and
  variable fonts.

## 0.1.0

### Initial Namche release

- Renamed the three families and package API to Namche Shadow Sans.
- Added Michael Marte and ruhm design credit while preserving all original
  Geist copyright and contributor notices.
- Retained the upstream Geist package history below for provenance.

## Upstream Geist package history

## 1.7.2

### Patch Changes

- a4195ae: Update Geist Pixel webfonts with Google Fonts validation fixes.

  Resyncs the published Geist Pixel static webfonts (`Circle`, `Grid`, `Line`, `Square`, `Triangle`) with the source build, picking up the non-visual fixes made for the Google Fonts release (#229): ligature caret anchors (`fi`, `fl`, `f_i`, `A_I`, `U_I`), a `meta` table with ScriptLangTags, line/paragraph separator glyphs and removal of the visible soft hyphen, and 1-unit on-curve point alignment fixes on `e`, `eogonek`, and `hungarumlautcomb`. No visible letterforms change.

## 1.7.1

### Patch Changes

- c8ed578: Fix Geist Mono rendering source-code text with unintended programming ligatures.

  v1.7.0 unintentionally activated programming-ligature substitutions (`-->`, `==`, `!=`, `...`, `--`, etc.) under the `liga` (Standard Ligatures) OpenType feature, which is on by default in every renderer. As a result, text like `--debug-prerender`, `[id...]`, `[...id]`, or `NODE_OPTIONS='--debug-prerender' node` rendered with ligated glyphs and broke monospace alignment in code.

  The source-level fix is in #217; this release ships the rebuilt binaries.

## 1.7.0

### Minor Changes

- d7ef63c: We're excited to announce a new member to our font family: Geist Pixel

  It's a display typeface family featuring five unique pixel-based variants, each with a distinct visual style. It is designed for decorative use in headlines, logos, and other display contexts where a pixelated aesthetic is desired.

  It includes five distinct variants, each exported separately:

  | Export               | CSS Variable                  | Description              |
  | -------------------- | ----------------------------- | ------------------------ |
  | `GeistPixelSquare`   | `--font-geist-pixel-square`   | Square pixel shapes      |
  | `GeistPixelGrid`     | `--font-geist-pixel-grid`     | Grid-based pixel pattern |
  | `GeistPixelCircle`   | `--font-geist-pixel-circle`   | Circular pixel shapes    |
  | `GeistPixelTriangle` | `--font-geist-pixel-triangle` | Triangular pixel shapes  |
  | `GeistPixelLine`     | `--font-geist-pixel-line`     | Line-based pixel pattern |

  ```jsx
  import {
    GeistPixelSquare,
    GeistPixelGrid,
    GeistPixelCircle,
    GeistPixelTriangle,
    GeistPixelLine,
  } from "geist/font/pixel";
  ```
