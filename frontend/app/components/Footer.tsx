'use client';

import Link from 'next/link';

export default function Footer() {
  return (
    <footer>
      <div className="container">
        <p>&copy; 2026 國立台北商業大學 二手書平台。版權所有。</p>
        <div>
          <Link href="#about">關於我們</Link>
          <Link href="#privacy">隱私政策</Link>
          <Link href="#terms">使用條款</Link>
          <Link href="#contact">聯絡我們</Link>
        </div>
      </div>
    </footer>
  );
}
