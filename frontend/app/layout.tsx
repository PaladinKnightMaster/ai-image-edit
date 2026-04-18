import "./globals.css";
import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "AI Image Edit Studio",
  description: "Offline-first AI image generator and editor for local studio workflows."
};

export default function RootLayout({
  children
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="grid-glow min-h-screen">
          {children}
        </div>
      </body>
    </html>
  );
}
