import type { Metadata } from "next";
import { Lilita_One, Nunito } from "next/font/google";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

const lilita = Lilita_One({
  subsets: ["latin"],
  variable: "--font-lilita",
  weight: "400",
  display: "swap",
});

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-nunito",
  weight: ["400", "600", "700", "800", "900"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Meeseeks Box — I'm Mr. Meeseeks! Look at me!",
  description:
    "Press the box, summon a Meeseeks, and it finishes one task by any means necessary. Intentionally vulnerable AI agent lab.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${lilita.variable} ${nunito.variable} ${GeistMono.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
