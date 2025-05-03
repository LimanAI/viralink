import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ThemeProvider } from "next-themes";

import QueryClientProvider from "@/providers/QueryClientProvider";

import "./globals.css";

// use "Inter", ui-sans-serif, system-ui, sans-serif
// landing titles "Poppins", ui-sans-serif, system-ui, sans-serif
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ViraLink AI",
  description: "AI SMM Agent",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <QueryClientProvider>
          <ThemeProvider defaultTheme="bumblebee">{children}</ThemeProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
