# Namche Shadow

<picture>
  <source media="(prefers-color-scheme: dark)" srcset=".docs/img/namche-shadow-banner--dark.png">
  <source media="(prefers-color-scheme: light)" srcset=".docs/img/namche-shadow-banner--light.png">
  <img alt="Namche Shadow Sans type specimen" src=".docs/img/namche-shadow-banner--light.png">
</picture>

Namche Shadow is a three-family type suite based on
[Vercel's Geist](https://github.com/vercel/geist-font):

| Family | Source | Status |
| --- | --- | --- |
| **Namche Shadow Sans** | Geist Sans | Custom inner-corner treatment designed by Michael Marte |
| **Namche Shadow Mono** | Geist Mono | Identical outlines and metrics; renamed for future Namche-specific work |
| **Namche Shadow Pixel** | Geist Pixel | Identical outlines and metrics; renamed for future Namche-specific work |

The repository follows the upstream Geist font-project layout: buildable
sources are in `sources/`, generated releases are in `fonts/`, automation is
in `.github/workflows/`, and the Next.js package is in `packages/next/`.

## Building

Fonts are built and tested by GitHub Actions. To run the same workflow
locally:

```sh
make build
make test
make proof
```

The current Fontspector baseline and triage guidance are documented in
[`documentation/FONTSPECTOR.md`](documentation/FONTSPECTOR.md).
The supported-script contract and intentional auxiliary omissions are listed in
[`documentation/LANGUAGE_SUPPORT.md`](documentation/LANGUAGE_SUPPORT.md).

The Namche Shadow Sans RoundCorner workflow still requires Glyphs for final design
exports. See [`scripts/NAMCHE_SHADOW.md`](scripts/NAMCHE_SHADOW.md) and
[`LEARNINGS.md`](LEARNINGS.md) before producing a release.

## Repository layout

| Path | Purpose |
| --- | --- |
| `sources/` | Namche-named Glyphs sources and gftools builder configs |
| `fonts/` | OTF, TTF, and WOFF2 distributions; variable builds where release-ready |
| `originals/geist/` | Immutable safecopy of the original Geist sources |
| `scripts/` | Upstream build helpers and Namche Shadow Sans design tooling |
| `packages/next/` | Next.js package, adapted from the upstream package |
| `documentation/` | Specimens, proofs, and project history |

The original archive must not be edited. Its provenance is documented in
[`originals/geist/UPSTREAM.md`](originals/geist/UPSTREAM.md).

The npm release workflow is prepared for token-free OIDC publishing. Its
one-time registry bootstrap is documented in
[`documentation/TRUSTED_PUBLISHING.md`](documentation/TRUSTED_PUBLISHING.md).

### CDN

Published releases are mirrored to `https://cdn.namche.ai` through the
infrastructure repository. Use an immutable version in production:

```css
@import url("https://cdn.namche.ai/fonts/namche-shadow/v0.2.1/fonts.css");
```

The short-lived
[`current` alias](https://cdn.namche.ai/fonts/namche-shadow/current/fonts.css)
is intended for previews. Release files, their SHA-256 manifest, and the
available-version index share the
`https://cdn.namche.ai/fonts/namche-shadow/` prefix. A successful tagged GitHub
release dispatches the approved archive to the CDN origin automatically; the
font repository never holds origin or SSH credentials.

### Static and variable fonts

Namche Shadow Sans ships static Thin through Black weights plus an upright
`wght` variable font. The approved static exports remain the visual source of
truth. The default and `font/sans` npm entry points use the rounded upright VF
with static italics; `font/sans-non-variable` uses statics throughout. Five
glyphs whose rounded masters still differ are parked only from the VF and
remain present in every static.

Namche Shadow Mono and Namche Shadow Pixel retain their upstream-derived
variable builds.

## Credits

The Namche Shadow Sans design direction and implementation is done by
[Michael Marte](https://github.com/fizzybubbele) for
[Ruhm etc.](https://ruhmetc.com/).

The suite is derived from Geist, created by Vercel in collaboration with
Basement Studio, Andrés Briganti, Mateo Zaragoza, and the other contributors
listed in [`AUTHORS.txt`](AUTHORS.txt) and [`CONTRIBUTORS.txt`](CONTRIBUTORS.txt).
Namche Shadow Mono and Namche Shadow Pixel currently preserve their upstream
outlines exactly; their new names do not imply an original redesign.

## License

The fonts, sources, and derivative font work are licensed under the
[SIL Open Font License 1.1](OFL.txt). Original Geist copyright notices and
author credits are retained in the sources and binary font metadata.
