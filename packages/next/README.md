# Namche Shadow Sans for Next.js

The package exposes Namche Shadow Sans, Namche Shadow Mono, and the five Namche
Shadow Pixel variants through `next/font/local`.

## Installation

```sh
pnpm add @namche/namche-shadow
```

## Usage

```tsx
import { NamcheShadowSans } from "@namche/namche-shadow/font/sans";
import { NamcheShadowMono } from "@namche/namche-shadow/font/mono";

export default function Layout({ children }) {
  return (
    <html className={`${NamcheShadowSans.variable} ${NamcheShadowMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

**Namche Shadow Sans** should be loaded from static weights
(`@namche/namche-shadow/font` or `sans-non-variable`). The designed inner
corners come from Glyphs RoundCorner on statics; they are not in the Sans
variable font. See
[`documentation/NAMCHE_SHADOW_STATICS.md`](../../documentation/NAMCHE_SHADOW_STATICS.md).

Namche Shadow Mono may use its variable font. Static Mono weights remain on
`mono-non-variable`.

Pixel variants are exported from `@namche/namche-shadow/font/pixel`:

- `NamcheShadowPixelSquare`
- `NamcheShadowPixelGrid`
- `NamcheShadowPixelCircle`
- `NamcheShadowPixelTriangle`
- `NamcheShadowPixelLine`

This package is adapted from Vercel's
[`geist`](https://www.npmjs.com/package/geist) package. The fonts remain
licensed under the [SIL Open Font License 1.1](../../OFL.txt); see the root
[`AUTHORS.txt`](../../AUTHORS.txt) and [`CONTRIBUTORS.txt`](../../CONTRIBUTORS.txt)
for full credit.
