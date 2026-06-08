import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NeuroCity Nexus",
  description: "City Brain AI command center for urban intelligence."
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
