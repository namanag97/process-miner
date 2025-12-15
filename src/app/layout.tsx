import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { LogPanel } from "@/components/features/LogPanel";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "ProcessMiner - Process Mining Made Simple",
  description: "Discover, analyze, and optimize your business processes with powerful process mining capabilities.",
  keywords: ["process mining", "business analytics", "workflow optimization"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans antialiased`}>
        <Providers>
          {children}
          <LogPanel />
        </Providers>
      </body>
    </html>
  );
}
