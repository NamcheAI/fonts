# Fontspector baseline

Run `make test` after `make build`. The command writes machine-readable JSON
reports to `out/fontspector/`. CI uploads that directory with the other proof
artifacts. JSON is used because the crates.io build of Fontspector 1.7.4 does
not include the optional Jinja templates required by its HTML/Markdown
reporters.

The test currently reports existing Google Fonts profile findings. The step is
non-blocking while the baseline is being reduced, but new findings are not
automatically acceptable: compare the report before and after every font
change.

## Current failures

| Family | Finding | Interpretation |
| --- | --- | --- |
| Sans and Mono statics | `repo/dirname_matches_nameid_1` | The Google Fonts profile interprets the distribution folder `ttf/` as a Google Fonts family directory. This repository deliberately uses the Geist-style `fonts/<Family>/ttf/` layout, so this is a profile/layout mismatch. |
| Mono variable | `name/family_and_style_max_length` | Some generated instance or PostScript names exceed the legacy 63-character limit. This is real metadata debt inherited from the renamed family and should be fixed before a Google Fonts submission. |
| Pixel statics | `font_names/unsupported-style` | Circle, Grid, Line, Square, and Triangle are custom Pixel styles; the Google Fonts profile expects conventional weight/style names. This is expected for the current product model but would block a Google Fonts submission. |
| Pixel statics | `meta/script_lang_tags` | The `meta` table does not declare `slng`. This is actionable metadata debt, but it predates the corrected Sans static drop. |

## Warning groups

- Outline heuristics (`alignment_miss`, `colinear_vectors`, `jaggy_segments`,
  `short_segments`, `contour_count`) identify shapes for visual inspection;
  they are not proof of a broken outline. Much of this baseline comes from
  upstream Geist and the intentional Pixel geometry.
- Glyph reachability and naming warnings flag encoded or substitution access,
  long legacy glyph names, soft-dotted behavior, dotted-circle behavior, and
  language-shaping coverage. Treat any increase as a possible regression.
- Metadata warnings cover WWS/STAT setup, vendor ID, name length, and family
  metadata. These are suitable for focused cleanup PRs rather than being mixed
  into a design-source update.
- Design-consistency warnings such as math-sign widths and ligature carets need
  a designer/type-engineer decision before changing outlines or metrics.

For the corrected Sans statics, the release-specific acceptance checks are
stronger than the generic profile: every weight must contain the complete
seven-tier RoundCorner result, `H` must retain the expected four rounded inner
segments, the five tier-7 glyphs must be present, and no static may contain an
`fvar` table.
