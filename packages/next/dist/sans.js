import localFont from "next/font/local";

export const NamcheShadowSans = localFont({
  // The rounded Shadow masters are not variable-compatible yet. Keep the
  // primary API on the real static outlines instead of serving the preserved
  // upstream-outline variable fallback.
  src: [
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Thin.woff2", weight: "100" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-UltraLight.woff2", weight: "200" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Light.woff2", weight: "300" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Regular.woff2", weight: "400" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Medium.woff2", weight: "500" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-SemiBold.woff2", weight: "600" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Bold.woff2", weight: "700" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-Black.woff2", weight: "800" },
    { path: "./fonts/namche-shadow-sans/NamcheShadowSans-UltraBlack.woff2", weight: "900" },
  ],
  variable: "--font-namche-shadow-sans",
});
