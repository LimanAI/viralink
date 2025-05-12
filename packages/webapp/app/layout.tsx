import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";

import "./globals.css";
import QueryClientProvider from "@/providers/QueryClientProvider";
import { WebAppProvider } from "@/providers/WebAppProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BoostIQ - Telegram Channel Manager",
  description: "Manage and boost your Telegram channels with BoostIQ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <WebAppProvider>
          <QueryClientProvider>
            <ThemeProvider defaultTheme="silk">{children}</ThemeProvider>
          </QueryClientProvider>
        </WebAppProvider>
      </body>
    </html>
  );
}
