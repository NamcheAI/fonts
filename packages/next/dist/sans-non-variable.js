import localFont from "next/font/local";

export const NamcheShadowSansNonVariable = localFont({
  src: [
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Thin.woff2",
      weight: "100",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-UltraLight.woff2",
      weight: "200",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Light.woff2",
      weight: "300",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Regular.woff2",
      weight: "400",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Medium.woff2",
      weight: "500",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-SemiBold.woff2",
      weight: "600",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Bold.woff2",
      weight: "700",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Black.woff2",
      weight: "800",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-UltraBlack.woff2",
      weight: "900",
      style: "normal",
    },
  ],
  variable: "--font-namche-shadow-sans-non-variable",
});
