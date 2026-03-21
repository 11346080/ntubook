import type { Metadata } from "next";
import "./globals.css";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Script from "next/script";

export const metadata: Metadata = {
  title: "北商傳書 | NTUB 二手書平台",
  description: "國立台北商業大學二手書交易平台 - 快速找書，輕鬆上架",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-TW" className="h-100">
      <head>
        {/* Bootstrap CSS (也可以考慮用 npm 安裝) */}
        <link
          href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
          rel="stylesheet"
        />
        {/* FontAwesome 圖示 */}
        <link 
          rel="stylesheet" 
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" 
        />
      </head>
      <body className="d-flex flex-column min-vh-100 antialiased">
        {/* Navbar：這裡可以預留從後端抓取的登入狀態 */}
        <Navbar initialAuth={false} unreadNotifications={3} />
        
        {/* 主內容區：使用 mt-auto 與 pt-5 確保固定導覽列不遮擋 */}
        <main className="flex-shrink-0" style={{ marginTop: '72px' }}>
          <div className="container py-4">
            {children}
          </div>
        </main>

        <Footer />

        {/* JS 置於底部提升載入速度 */}
        <Script 
          src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"
          strategy="lazyOnload" 
        />
      </body>
    </html>
  );
}