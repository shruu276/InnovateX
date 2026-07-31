import type { Metadata } from "next";
import "./globals.css";
import WatsonAgent from "@/components/WatsonAgent";

export const metadata: Metadata = {
  title: "InnovateX AI — Where Ideas Meet Intelligence",
  description:
    "InnovateX AI bridges academia, industry, government, and startups through an AI-powered project collaboration platform. Build the future together.",
  keywords: [
    "AI collaboration",
    "research platform",
    "innovation",
    "academia",
    "industry partnerships",
    "startup",
    "grant discovery",
  ],
  openGraph: {
    title: "InnovateX AI — Where Ideas Meet Intelligence",
    description:
      "Bridge Academia, Industry, Government & Startups with AI-assisted project collaboration.",
    type: "website",
    url: "https://innovatex.ai",
  },
  twitter: {
    card: "summary_large_image",
    title: "InnovateX AI",
    description: "AI-powered innovation platform for cross-sector collaboration.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-white text-gray-900 antialiased font-sans dark:bg-[#0D0F14] dark:text-gray-100">
        {children}
        {/* IBM watsonx Orchestrate AI agent — renders no DOM, injects chat widget */}
        <WatsonAgent />
      </body>
    </html>
  );
}
