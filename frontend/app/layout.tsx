import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "AETERNUM · Command Intelligence", description: "Financial intelligence ecosystem operating in paper mode." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
