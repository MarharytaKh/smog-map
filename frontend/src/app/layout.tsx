import type { Metadata } from "next";
import Link from "next/link";
import { Patrick_Hand, Permanent_Marker } from "next/font/google";
import "./globals.css";

const hand = Patrick_Hand({ weight: "400", subsets: ["latin", "latin-ext"], variable: "--font-hand" });
const marker = Permanent_Marker({ weight: "400", subsets: ["latin"], variable: "--font-marker" });

export const metadata: Metadata = {
  title: "Smog Map",
  description: "Air quality in Poland, from GIOŚ stations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${hand.variable} ${marker.variable}`}>
      <body>
        <header className="top">
          <Link href="/" className="logo">
            smog map
          </Link>
          <nav>
            <Link href="/">map</Link>
            <Link href="/compare">compare</Link>
            <Link href="/alerts">alerts</Link>
          </nav>
        </header>
        <main>{children}</main>
        <footer className="foot">
          data: <a href="https://powietrze.gios.gov.pl" target="_blank" rel="noreferrer">GIOŚ</a>, updated every hour
        </footer>
      </body>
    </html>
  );
}
