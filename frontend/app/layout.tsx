import type { Metadata } from "next";
import "./globals.css";
import AuthProvider from "./components/AuthProvider";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Script from "next/script";
import { auth } from "../auth";

export const metadata: Metadata = {
  title: "北商傳書 | NTUB 二手書平台",
  description: "國立台北商業大學二手書交易平台 - 快速找書，輕鬆上架",
  icons: {
    icon: "/vercel.svg",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const session = await auth();
  return (
    <html lang="zh-TW" className="h-100">
      <head>
        {/* Bootstrap CSS */}
        <link
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
          rel="stylesheet"
        />
        {/* FontAwesome 圖示 */}
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
        />
        {/* Google Fonts - 思源黑體和思源宋體 */}
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="d-flex flex-column min-vh-100 antialiased">
        {/* Auth */}
        <AuthProvider session={session}>
        {/* Navbar */}
        <Navbar unreadNotifications={0} />

        {/* 主內容區 */}
        <main className="flex-shrink-0" style={{ marginTop: '80px', paddingBottom: '2rem' }}>
          <div className="container-lg">
            {children}
          </div>
        </main>

        {/* Footer */}
        <Footer />

        </AuthProvider>
        {/* Bootstrap JS */}
        <Script
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
          strategy="lazyOnload"
        />
      </body>
    </html>
  );
}