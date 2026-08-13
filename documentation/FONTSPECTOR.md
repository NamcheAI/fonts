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
| Mono italic variable | `googlefonts/fvar_instances` | The three Word-compatible named-instance aliases intentionally differ from the full STAT weight labels. This satisfies the universal 32-character family-and-style limit while preserving the public typographic names, but it would block a Google Fonts submission. |
| Pixel statics | `font_names/unsupported-style` | Circle, Grid, Line, Square, and Triangle are custom Pixel styles; the Google Fonts profile expects conventional weight/style names. This is expected for the current product model but would block a Google Fonts submission. |

Namche Shadow Sans VF currently has **no Fontspector failures**. Its 27 warning
results are the existing outline, glyph-reachability, language-shaping, WWS,
vendor-ID, and sidebearing groups described below, plus:

- `file_size`: the unsubsetted 970-glyph TTF is 1.2 MB (the shipped WOFF2 is
  substantially smaller).
- `mandatory_avar_table`: the `wght` axis intentionally uses a linear mapping.
- `interpolation_issues`: heuristic kink/start-point findings in a small set of
  inherited rounded glyphs. The builder's structural and named-master checks
  plus explicit visual inspection remain the release gate for these shapes.

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

For Sans, the release-specific acceptance checks are stronger than the generic
profile: every static weight must contain the complete seven-tier RoundCorner
result, `H` must retain the expected four rounded inner segments, the five
tier-7 glyphs must remain in all statics and stay parked from the VF, and no
static may contain an `fvar` table. Run `scripts/check_sans_variable.py` and
review `documentation/proof-rounded-sans-variable.png` for the VF.

## Naming compatibility

The Mono italic variable font uses the legacy named-instance aliases `XLight
Italic`, `SemiBd Italic`, and `XBold Italic`. Together with the unchanged
public family name `Namche Shadow Mono`, each stays within the 32-character
Windows/Word limit. The full weight labels remain available in the STAT table.
Google Fonts requires `fvar` instance names to match those STAT labels exactly,
so its distributor-specific `googlefonts/fvar_instances` check necessarily
fails for this compatibility choice. The universal name-length check and the
Google Fonts family-name consistency check both pass.

Some Sans and Mono italic static PostScript names exceed Fontspector's
recommended 27-character legacy guidance. They remain below the OpenType
PostScript-name limit and deliberately keep the canonical
`NamcheShadowSans`/`NamcheShadowMono` prefix: shortening only name ID 6 would
make the binaries internally inconsistent and fail the Google Fonts naming
check. Treat these warnings as an intentional compatibility tradeoff unless a
separate legacy-named distribution is introduced.
