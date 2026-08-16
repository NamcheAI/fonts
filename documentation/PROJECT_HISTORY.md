# Project history

Namche Shadow began as a set of experiments applying rounded inner corners to
Geist Sans while keeping its outer silhouette crisp. An early two-radius
experiment was called **Namche Shadow Simple**. The production direction became
a seven-tier Glyphs RoundCorner stack and was briefly called **Namche Darth**
before the final **Namche Shadow Sans** name was chosen.

On 2026-08-13, the repository was reorganized around the Geist font-project
layout. The immutable upstream source moved to [`originals/geist/`](../originals/geist/),
working sources moved to [`sources/`](../sources/), and generated release
binaries moved to [`fonts/`](../fonts/). Earlier path layouts and experimental
instructions remain available in Git history but are not maintained.

The corrected `Namche-Shadow-Edited.glyphspackage` supplied by
[Michael Marte](https://github.com/fizzybubbele) on 2026-08-13 became the visual
source of truth for upright Sans statics. Its seven-tier RoundCorner stack is
preserved. The five final-tier glyphs—`Yusbig-cy`, `yusbig-cy`, `mu`, `baht`,
and `peso`—ship in every static and remain parked only from the upright variable
font until their rounded masters match.

The upright Sans variable font was subsequently rebuilt from compatible native
Glyphs OTF exports so it could retain the reviewed rounded outlines. Namche
Shadow Mono remains an outline-identical renamed Geist derivative. Namche
Shadow Pixel began the same way and now accepts only focused, reviewed glyph
additions and shaping corrections.

Current production instructions live in [`AGENTS.md`](../AGENTS.md),
[`scripts/NAMCHE_SHADOW.md`](../scripts/NAMCHE_SHADOW.md), and
[`LEARNINGS.md`](../LEARNINGS.md). Release history lives in
[`CHANGELOG.md`](../CHANGELOG.md) and the package changelog.

Namche Shadow Sans was designed by Michael Marte for
[Ruhm etc.](https://ruhmetc.com/). The suite is derived from
[Geist](https://github.com/vercel/geist-font) and retains its authorship and SIL
Open Font License notices. AI tools are recorded only as tooling assistants,
not as designers or copyright authors.
