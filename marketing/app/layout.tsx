import type { Metadata } from "next";
import "./globals.css";

const GITHUB_URL = "https://github.com/dclawstack/dclaw-med";
const DESCRIPTION =
  "Clinical intelligence for clinicians, not billing software. Ambient documentation, evidence-cited differentials, FHIR R4 drop-in, and longitudinal AI over the patient's chart — open source.";

export const metadata: Metadata = {
  title: "DClaw Med — Clinical intelligence, not billing software",
  description: DESCRIPTION,
  metadataBase: new URL("https://dclaw-med.vercel.app"),
  openGraph: {
    title: "DClaw Med",
    description: DESCRIPTION,
    url: "/",
    siteName: "DClaw Med",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "DClaw Med",
    description: DESCRIPTION,
  },
  icons: {
    icon: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          rel="preconnect"
          href="https://fonts.googleapis.com"
        />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans" data-github-url={GITHUB_URL}>
        {children}
      </body>
    </html>
  );
}
