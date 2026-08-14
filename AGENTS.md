# Namche Shadow Font development rules

This repository is the source, build, review, and release home for
`NamcheAI/namche-shadow-font`. It follows the Vercel Geist repository layout,
but Namche-specific source and release decisions take precedence over upstream
conventions.

## Sources and ownership

- `sources/` contains the working Glyphs packages and builder configuration.
- `fonts/` contains generated release binaries. Commit regenerated binaries
  together with the source change that produced them.
- `originals/geist/` is an immutable copy of the upstream Geist source. Never
  edit, rename, or regenerate files there.
- Preserve the SIL Open Font License, the original Geist/Vercel copyright and
  author credits, and the Namche attribution already present in source and
  binary metadata.
- Credit Michael Marte as the designer of Namche Shadow Sans and link both his
  GitHub account (`fizzybubbele`) and Ruhm etc. (`https://ruhmetc.com/`) in
  user-facing credits. AI tools are tooling assistants, not designers or
  copyright authors.

## Namche Shadow Sans production rules

- The corrected `Namche-Shadow-Edited.glyphspackage` received from Michael on
  2026-08-13 is the visual source of truth for upright statics.
- Import a replacement package with
  `python3 scripts/import_edited_sans.py /path/to/package`. The importer keeps
  repository naming and attribution; do not copy an incoming `fontinfo.plist`
  over the maintained one by hand.
- Ship static Thin through Black instances. RoundCorner filters must run in
  Glyphs 4 during export; `glyphs-cli` and a plain variable-font build do not
  reproduce this treatment reliably.
- Finalize the native Glyphs OTF/TTF exports with
  `make finalize-sans-statics GLYPHS_SANS_EXPORT=/path/to/export`: it keeps
  Glyphs' rounded outlines while preserving the current release's OpenType
  layout and metadata, flattens nested TrueType components, produces WOFF2,
  and refreshes the npm font directory. The export path must contain `otf/`
  and `ttf/` subdirectories.
- Keep the complete ordered seven-filter stack. The final tier is
  `RoundCorner;-10;include:Yusbig-cy,yusbig-cy,mu,baht,peso` (Glyphs may
  serialize spaces after commas).
- `Yusbig-cy`, `yusbig-cy`, `mu`, `baht`, and `peso` must export in every
  static. Do not add `Remove Glyphs` to static instances.
- Build the upright variable font only from native Glyphs OTF exports whose
  seven RoundCorner filters use the `compatible` option. Run
  `make build-sans-variable GLYPHS_SANS_EXPORT=/path/to/export`; the builder
  preserves the post-rounding curves, makes the remaining segmentation
  compatible, converts all masters to TrueType curves together, and verifies
  every named instance against its rounded master. Never enable the sharp
  gftools/Glyphs VF as a substitute.
- Keep `Yusbig-cy`, `yusbig-cy`, `mu`, `baht`, and `peso` parked from the
  variable build until their rounded masters match. They must remain in every
  static.
- Namche Shadow Mono and Namche Shadow Pixel remain outline-identical renamed
  Geist derivatives until a separately reviewed design change says otherwise.
- Every release and npm binary uses OS/2 version 4 or later, sets `fsSelection`
  WWS bit 8, and omits name IDs 21/22. Preserve the public family/style names;
  `scripts/rename_font_metadata.py` is the maintained normalization and check.
- For an OpenType-layout-only source change, build a temporary matching family
  with gftools and run `scripts/refresh_shaping_tables.py` against the approved
  release family. The script may replace only `GDEF`, `GSUB`, and `GPOS`; it
  verifies that outlines, variation data, and metrics remain byte-identical.

## Required workflow

1. Start with a GitHub issue for a font bug or design correction. Record the
   expected visual result and tag Michael when his review or source is relevant.
2. Create a focused `codex/<topic>` or `jodok/<topic>` branch. Never push
   directly to protected `main` and never force-push `main`.
3. Keep changes single-topic. Do not mix a font correction with unrelated
   cleanup.
4. Use Conventional Commit messages and PR titles (`fix:`, `feat:`,
   `refactor:`, `docs:`, and so on). Commits made through the maintainer's agent
   environment are authored as `Jodok Batlogg <jodok@batlogg.com>`; the agent
   may add its own `Co-Authored-By:` trailer but must never replace the human
   author. Credit designer-provided source drops in the issue, PR, and project
   history.
5. Add a Changesets file under `packages/next/.changeset/` for every
   user-visible npm change. Use patch/minor/major according to SemVer.
6. Open a PR, let GitHub Actions build and test it, request `@codex review`, and
   address and resolve every actionable review thread. Merge only when required
   checks are green and GitHub reports a clean merge state.
7. Squash-merge and delete the branch. Releases are prepared by the Changesets
   PR and published through npm Trusted Publishing; do not publish manually
   with a local npm token.

## Validation before a PR

Run the checks relevant to the change, preferably all of these for a font
source update:

```sh
make build
make test
make proof
make check-source-copies
venv/bin/python scripts/rename_font_metadata.py --check fonts
cd packages/next && npm pack --dry-run
```

Additionally, inspect representative inner corners (`H`, `E`, `a`, diagonals,
and figures) in every changed weight. Confirm the family names and credits in
the built name tables, verify that the Sans statics contain no `fvar` table,
and verify that the five temporarily parked variable glyphs are present in all
Sans statics.

Do not dismiss Fontspector output merely because CI currently marks the step as
non-blocking. Summarize new warnings in the PR, distinguish upstream/pre-existing
warnings from regressions, and fix regressions before merge. See
`documentation/FONTSPECTOR.md` for the maintained baseline.
`scripts/check_language_shaping.py` is the blocking exception: every Sans and
Mono TTF/VF must pass `soft_dotted`, and language-shaping warnings may contain
only documented auxiliary omissions.
