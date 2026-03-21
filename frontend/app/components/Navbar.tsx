'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavbarProps {
  initialAuth: boolean;
  unreadNotifications?: number;
}

export default function Navbar({ initialAuth, unreadNotifications = 0 }: NavbarProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(initialAuth);
  const pathname = usePathname();

  // 定義選單項目，方便管理
  const navLinks = [
    { name: '我要賣書', href: '/sell', icon: 'fa-plus-circle' },
    { name: '會員中心', href: '/member', icon: 'fa-user-circle' },
  ];

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-white border-bottom fixed-top py-2 shadow-sm">
      <div className="container">
        {/* Logo */}
        <Link className="navbar-brand d-flex align-items-center fw-bold text-primary" href="/">
          <i className="fas fa-book-open me-2"></i>
          北商傳書
        </Link>

        {/* 漢堡選單 (手機版) */}
        <button 
          className="navbar-toggler border-0" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navContent"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navContent">
          {/* 中間搜尋框 - 提高響應式體驗 */}
          <form className="mx-auto my-3 my-lg-0 d-flex w-100" style={{ maxWidth: '500px' }}>
            <div className="input-group">
              <input
                className="form-control border-end-0 bg-light rounded-start-pill border-0"
                type="search"
                placeholder="搜尋書名、作者、ISBN..."
                style={{ paddingLeft: '1.2rem' }}
              />
              <button className="btn btn-light border-start-0 rounded-end-pill px-3" type="submit">
                <i className="fas fa-search text-muted"></i>
              </button>
            </div>
          </form>

          {/* 右側按鈕區 */}
          <ul className="navbar-nav align-items-center gap-1">
            {navLinks.map((link) => (
              <li key={link.href} className="nav-item">
                <Link 
                  className={`nav-link fw-medium px-3 ${pathname === link.href ? 'text-primary' : 'text-dark'}`} 
                  href={link.href}
                >
                  <i className={`fas ${link.icon} me-1`}></i> {link.name}
                </Link>
              </li>
            ))}
            
            {/* 通知中心 */}
            <li className="nav-item px-2 position-relative d-none d-lg-block">
              <Link href="/notifications" className="text-dark">
                <i className="fas fa-bell fs-5 cursor-pointer"></i>
                {unreadNotifications > 0 && (
                  <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger border border-light">
                    {unreadNotifications}
                  </span>
                )}
              </Link>
            </li>

            {/* 登入/登出切換 */}
            <li className="nav-item ms-lg-3">
              {isAuthenticated ? (
                <button 
                  onClick={() => setIsAuthenticated(false)}
                  className="btn btn-outline-danger btn-sm rounded-pill px-4 shadow-sm"
                >
                  登出
                </button>
              ) : (
                <Link href="/login" className="btn btn-primary btn-sm rounded-pill px-4 shadow-sm text-white">
                  登入
                </Link>
              )}
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}