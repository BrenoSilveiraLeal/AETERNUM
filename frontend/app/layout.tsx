import type { Metadata } from "next";
import "./globals.css";
import "./avatar-overrides.css";

export const metadata: Metadata = {
  title: "AETERNUM · Command Center",
  description: "Centro de comando da Aurion: inteligência financeira, sinais e carteiras em modo PAPER.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
