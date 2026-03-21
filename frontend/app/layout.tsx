import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";

declare global {
  interface Window {
    __BASEURL__?: string;
  }
}

export const metadata: Metadata = {
  title: "NTUB 二手書平台",
  description: "國立台北商業大學二手書交易平台 - 買賣教科書，輕鬆省錢",
};

const baseUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW">
      <head>
        {/* Bootstrap CDN 備援 */}
        <link
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <Navbar />
        <main className="container-fluid">
          <div className="container">{children}</div>
        </main>
        <Footer />
        <script
          dangerouslySetInnerHTML={{
            __html: `window.__BASEURL__ = "${baseUrl}";`,
          }}
        />
      </body>
    </html>
  );
}
