import type { Metadata } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "CareerOS — Multi-Agent Career Intelligence Platform",
  description: "Your AI-Powered Multi-Agent Career Intelligence Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}