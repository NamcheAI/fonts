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

The dedicated Namche Shadow Sans export includes its upright and italic
variable fonts. Static upright and italic Sans weights remain available from
`@namche/namche-shadow/font` and the `sans-non-variable` entry point. The Mono
exports currently provide upright styles.

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
