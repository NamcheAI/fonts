import localFont from "next/font/local";

export const NamcheShadowMonoNonVariable = localFont({
  src: [
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-UltraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-Black.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-mono/NamcheShadowMono-UltraBlack.woff2",
      weight: "900",
      style: "normal",
    },
  ],
  variable: "--font-namche-shadow-mono-non-variable",
  adjustFontFallback: false,
  fallback: [
    "ui-monospace",
    "SFMono-Regular",
    "Roboto Mono",
    "Menlo",
    "Monaco",
    "Liberation Mono",
    "DejaVu Sans Mono",
    "Courier New",
    "monospace",
  ],
});
