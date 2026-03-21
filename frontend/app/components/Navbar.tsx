'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Navbar.module.css';

interface NavbarProps {
  initialAuth?: boolean;
  unreadNotifications?: number;
}

export default function Navbar({ initialAuth = false, unreadNotifications = 0 }: NavbarProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(initialAuth);
  const [logoError, setLogoError] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  const handleLinkClick = () => {
    const navContent = document.getElementById('navContent');
    if (navContent?.classList.contains('show')) {
      navContent.classList.remove('show');
    }
  };

  const navLinks = [
    { name: '我要賣書', href: '/listings', icon: 'fa-plus-circle' },
    { name: '會員中心', href: '/dashboard', icon: 'fa-user-circle' },
  ];

  return (
    <nav 
      className={`navbar navbar-expand-lg fixed-top py-3 shadow-sm ${styles.navbar}`}
      style={{
        backgroundColor: isHomePage ? 'rgba(255, 255, 255, 0.95)' : 'var(--color-bg-primary)',
        backdropFilter: isHomePage ? 'blur(10px)' : 'none',
        borderBottom: `1px solid var(--color-border)`,
      }}
    >
      <div className="container-lg">
        {/* Logo */}
        <Link
          className={`navbar-brand fw-bold d-flex align-items-center gap-2 ${styles.logo}`}
          href="/"
          onClick={handleLinkClick}
          style={{ color: 'var(--color-seal)' }}
        >{/* Logo 圖片 - 支援文字回退 */}
          {!logoError ? (
            <Image
              src="/images/logo_word.png"
              alt="NTUB 二手書平台 Logo"
              width={100}         
              height={65}         
              priority
              quality={90}
              onError={() => setLogoError(true)}
              style={{ 
                objectFit: 'contain', 
                maxHeight: '65px', 
                width: 'auto' ,
                marginLeft: '-10px',
                marginRight: '-5px'
              }}
            />
          ) : (
            <span
              style={{
                fontFamily: "'Noto Serif TC', serif",
                fontSize: '18px',
                fontWeight: 'bold',
                color: 'var(--color-seal)',
              }}
            >
              NTUBook
            </span>
          )}
          <span className="d-none d-sm-inline"></span>
        </Link>

        {/* 漢堡選單按鈕 */}
        <button
          className={`navbar-toggler border-0 ${styles.toggler}`}
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navContent"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className="collapse navbar-collapse" id="navContent">
          {/* 中間搜尋框 */}
          <form className={`mx-auto my-3 my-lg-0 d-flex flex-grow-1 ${styles.searchForm}`}>
            <div className="input-group" style={{ maxWidth: '400px' }}>
              <input
                className={`form-control border-0 ${styles.searchInput}`}
                type="search"
                placeholder="搜尋書名、作者..."
                style={{
                  backgroundColor: 'var(--color-bg-light)',
                  borderRadius: 'var(--border-radius)',
                  paddingLeft: '1.2rem',
                }}
              />
              <button
                className={`btn ${styles.searchBtn}`}
                type="submit"
                style={{
                  backgroundColor: 'transparent',
                  border: 'none',
                  color: 'var(--color-muted)',
                }}
              >
                <i className="fas fa-search"></i>
              </button>
            </div>
          </form>

          {/* 右側按鈕區 */}
          <ul className="navbar-nav align-items-center gap-2 ms-lg-auto">
            {navLinks.map((link) => (
              <li key={link.href} className="nav-item">
                <Link
                  className={`nav-link fw-500 px-3 transition-all ${styles.navLink}`}
                  href={link.href}
                  onClick={handleLinkClick}
                  style={{
                    color: pathname === link.href ? 'var(--color-seal)' : 'var(--color-text-secondary)',
                  }}
                >
                  <i className={`fas ${link.icon} me-1`}></i> {link.name}
                </Link>
              </li>
            ))}

            {/* 通知中心 */}
            <li className="nav-item ps-2 position-relative d-none d-lg-block">
              <Link href="/notifications" className={styles.notificationBell} onClick={handleLinkClick}>
                <i className="fas fa-bell fs-5"></i>
                {unreadNotifications > 0 && (
                  <span
                    className="position-absolute top-0 start-100 translate-middle badge rounded-pill text-white"
                    style={{
                      backgroundColor: 'var(--color-seal)',
                      padding: '0.35rem 0.6rem',
                      fontSize: '0.7rem',
                    }}
                  >
                    {unreadNotifications}
                  </span>
                )}
              </Link>
            </li>

            {/* 登入/註冊按鈕 */}
            <li className="nav-item ms-lg-3">
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    setIsAuthenticated(false);
                    handleLinkClick();
                  }}
                  className="btn btn-sm rounded-pill px-4"
                  style={{
                    backgroundColor: 'var(--color-seal)',
                    color: 'white',
                    border: 'none',
                    fontWeight: '500',
                  }}
                >
                  登出
                </button>
              ) : (
                <div className="d-flex gap-2">
                  <Link
                    href="/login"
                    className="btn btn-sm rounded-pill px-4"
                    style={{
                      backgroundColor: 'transparent',
                      color: 'var(--color-text-primary)',
                      border: `1px solid var(--color-border)`,
                      fontWeight: '500',
                    }}
                    onClick={handleLinkClick}
                  >
                    登入
                  </Link>
                  <Link
                    href="/register"
                    className="btn btn-sm rounded-pill px-4"
                    style={{
                      backgroundColor: 'var(--color-cta)',
                      color: 'white',
                      border: 'none',
                      fontWeight: '500',
                    }}
                    onClick={handleLinkClick}
                  >
                    註冊
                  </Link>
                </div>
              )}
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}