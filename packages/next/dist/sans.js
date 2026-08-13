import localFont from "next/font/local";

export const NamcheShadowSans = localFont({
  src: [
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-Variable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "./fonts/namche-shadow-sans/NamcheShadowSans-ItalicVariable.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-namche-shadow-sans",
});
