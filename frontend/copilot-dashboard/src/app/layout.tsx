import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Tableau de Bord DevOps | Gologic",
  description: "Suivez les performances et métriques DevOps de votre organisation",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <header className="bg-white border-b border-neutral-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center">
              <div className="text-2xl font-bold text-neutral-900">
                Tableau de Bord
              </div>
              <nav className="flex space-x-4">
                <Link href="/" className="text-neutral-800 hover:text-primary">Tableau de Bord</Link>
                <Link href="/teams" className="text-neutral-800 hover:text-primary">Équipes</Link>
                <Link href="#" className="text-neutral-800 hover:text-primary">Paramètres</Link>
              </nav>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
