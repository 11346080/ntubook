'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from '../style/Navbar.module.css';

interface NavbarProps {
  initialAuth?: boolean;
  unreadNotifications?: number;
}

export default function Navbar({ initialAuth = false, unreadNotifications = 0 }: NavbarProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(initialAuth);
  const [logoError, setLogoError] = useState(false);
  const pathname = usePathname();
  const isHomePage = pathname === '/';
  const [scrolled, setScrolled] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      setScrolled(scrollTop > 50);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (isMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMenuOpen]);

  const handleLinkClick = () => {
    closeMenu();
  };

  const toggleMenu = () => {
    if (isMenuOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  };

  const openMenu = () => {
    setIsMenuOpen(true);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  const navLinks = [
    { name: '首頁', href: '/', enName: 'Home', icon: 'fa-home' },
    { name: '所有書籍', href: '/listings', enName: 'Books', icon: 'fa-book' },
    { name: '我要賣書', href: '/listings/create', enName: 'Sell', icon: 'fa-plus-circle' },
    { name: '會員中心', href: '/dashboard', enName: 'Account', icon: 'fa-user-circle' },
  ];

  return (
    <>
      <nav 
        className={`${styles.navbar}`}
        style={{
          transform: isHomePage && !scrolled ? 'translateY(-100%)' : 'translateY(0)',
          opacity: isHomePage && !scrolled ? 0 : 1,
          backgroundColor: isHomePage && !scrolled 
            ? 'transparent'
            : isHomePage && scrolled
            ? 'rgba(255, 255, 255, 0.95)'
            : 'rgba(255, 255, 255, 0.95)',
          backdropFilter: (isHomePage && scrolled) || !isHomePage ? 'blur(10px)' : 'none',
          borderBottom: (isHomePage && scrolled) || !isHomePage ? `1px solid var(--color-border)` : 'none',
          boxShadow: (isHomePage && scrolled) || !isHomePage ? '0 2px 8px rgba(30, 20, 10, 0.12)' : 'none',
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          zIndex: 999,
          pointerEvents: isHomePage && !scrolled ? 'none' : 'auto',
        }}
      >
        <div className={`${styles.navContainer}`}>
          {/* Logo */}
          <Link
            className={`${styles.logo}`}
            href="/"
            onClick={handleLinkClick}
          >
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
                  width: 'auto',
                  marginLeft: '-10px',
                  marginRight: '-5px'
                }}
              />
            ) : (
              <span style={{
                fontFamily: "'Noto Serif TC', serif",
                fontSize: '18px',
                fontWeight: 'bold',
                color: 'var(--color-seal)',
              }}>
                NTUBook
              </span>
            )}
          </Link>

          {/* Desktop Navigation - Center */}
          <ul className={`${styles.desktopNav}`}>
            {navLinks.slice(0, 2).map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  onClick={handleLinkClick}
                  className={`${styles.navLink} ${pathname === link.href ? styles.active : ''}`}
                >
                  {link.name}
                </Link>
              </li>
            ))}
          </ul>

          {/* Desktop Search */}
          <form className={`${styles.desktopSearch}`}>
            <input 
              className={`${styles.searchInput}`}
              type="search"
              placeholder="搜尋書名、作者..."
            />
            <button type="submit" className={`${styles.searchBtn}`}>
              <i className="fas fa-search"></i>
            </button>
          </form>

          {/* Desktop Right Section */}
          <div className={`${styles.desktopRight}`}>
            {/* 我要賣書 */}
            <Link 
              href="/listings/create"
              onClick={handleLinkClick}
              className={`${styles.actionLink}`}
              title="刊登書籍"
            >
              <i className="fas fa-plus-circle"></i>
              <span>我要賣書</span>
            </Link>

            {/* 會員中心 */}
            <Link 
              href="/dashboard"
              onClick={handleLinkClick}
              className={`${styles.actionLink}`}
              title="會員中心"
            >
              <i className="fas fa-user-circle"></i>
              <span>會員中心</span>
            </Link>

            {/* 通知 */}
            <Link 
              href="/notifications"
              onClick={handleLinkClick}
              className={`${styles.notificationBell}`}
              title="通知"
            >
              <i className="fas fa-bell"></i>
              {unreadNotifications > 0 && (
                <span className={`${styles.badge}`}>
                  {unreadNotifications}
                </span>
              )}
            </Link>

            {/* 登入/註冊 */}
            <div className={`${styles.authButtons}`}>
              {isAuthenticated ? (
                <button
                  onClick={() => {
                    setIsAuthenticated(false);
                    handleLinkClick();
                  }}
                  className={styles.logoutBtn}
                >
                  登出
                </button>
              ) : (
                <>
                  <Link
                    href="/login"
                    onClick={handleLinkClick}
                    className={styles.loginBtn}
                  >
                    登入
                  </Link>
                  <Link
                    href="/register"
                    onClick={handleLinkClick}
                    className={styles.registerBtn}
                  >
                    註冊
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Book Menu Button */}
          <button 
            className={`${styles.bookBtn} ${isMenuOpen ? styles.open : ''}`}
            onClick={toggleMenu}
            aria-label="選單"
            aria-expanded={isMenuOpen}
          >
            <svg viewBox="0 0 72 56" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="coverGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{stopColor:'#c23d52'}}/>
                  <stop offset="100%" style={{stopColor:'#6e1825'}}/>
                </linearGradient>
                <linearGradient id="pageGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{stopColor:'#ede8df'}}/>
                  <stop offset="100%" style={{stopColor:'#f8f5ef'}}/>
                </linearGradient>
                <linearGradient id="goldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{stopColor:'#e0c97a'}}/>
                  <stop offset="100%" style={{stopColor:'#a07c2a'}}/>
                </linearGradient>
                <linearGradient id="spineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style={{stopColor:'#4a0f1a'}}/>
                  <stop offset="50%" style={{stopColor:'#9b2335'}}/>
                  <stop offset="100%" style={{stopColor:'#4a0f1a'}}/>
                </linearGradient>
                <linearGradient id="leftCoverGrad" x1="100%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style={{stopColor:'#6e1825'}}/>
                  <stop offset="100%" style={{stopColor:'#3d0d12'}}/>
                </linearGradient>
                <linearGradient id="rightCoverGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style={{stopColor:'#c23d52'}}/>
                  <stop offset="100%" style={{stopColor:'#6e1825'}}/>
                </linearGradient>
                <filter id="shadow">
                  <feDropShadow dx="2" dy="3" stdDeviation="3" floodColor="#6e1825" floodOpacity="0.35"/>
                </filter>
                <filter id="softShadow">
                  <feDropShadow dx="1" dy="2" stdDeviation="2" floodColor="#9b2335" floodOpacity="0.25"/>
                </filter>
              </defs>

              {/* CLOSED BOOK */}
              <g className={styles.bookClosed} filter="url(#shadow)">
                <rect x="10" y="5" width="52" height="46" rx="1" fill="url(#pageGrad)" stroke="#d4cfc5" strokeWidth="0.5"/>
                <line x1="11" y1="9" x2="61" y2="9" stroke="#e0dbd0" strokeWidth="0.6"/>
                <line x1="11" y1="12" x2="61" y2="12" stroke="#e8e3d8" strokeWidth="0.5"/>
                <rect x="10" y="47" width="52" height="4" rx="0" fill="#c9c4ba" opacity="0.5"/>
                <rect x="8" y="3" width="54" height="50" rx="2" fill="url(#coverGrad)" stroke="#7a1a28" strokeWidth="0.8"/>
                <rect x="11" y="6" width="48" height="44" rx="1" fill="none" stroke="url(#goldGrad)" strokeWidth="1"/>
                <path d="M11 6 L18 6 L11 13 Z" fill="#c9a84c" opacity="0.6"/>
                <path d="M59 6 L52 6 L59 13 Z" fill="#c9a84c" opacity="0.6"/>
                <path d="M11 50 L18 50 L11 43 Z" fill="#c9a84c" opacity="0.6"/>
                <path d="M59 50 L52 50 L59 43 Z" fill="#c9a84c" opacity="0.6"/>
                <line x1="20" y1="22" x2="52" y2="22" stroke="url(#goldGrad)" strokeWidth="2.5" strokeLinecap="round"/>
                <line x1="20" y1="30" x2="52" y2="30" stroke="url(#goldGrad)" strokeWidth="2.5" strokeLinecap="round"/>
                <line x1="20" y1="38" x2="52" y2="38" stroke="url(#goldGrad)" strokeWidth="2.5" strokeLinecap="round"/>
                <rect x="8" y="3" width="7" height="50" rx="2" fill="url(#spineGrad)" stroke="#4a0f1a" strokeWidth="0.6"/>
                <line x1="10.5" y1="10" x2="10.5" y2="46" stroke="#c9a84c" strokeWidth="0.6" opacity="0.5"/>
              </g>

              {/* OPEN BOOK */}
              <g className={styles.bookOpen} filter="url(#softShadow)">
                <path d="M4 4 Q4 2 6 2 L36 2 L36 54 L6 54 Q4 54 4 52 Z" fill="url(#pageGrad)" stroke="#d4cfc5" strokeWidth="0.5"/>
                <path d="M2 5 Q2 3 4 3 L36 3 L36 53 L4 53 Q2 53 2 51 Z" fill="url(#leftCoverGrad)" stroke="#3d0d12" strokeWidth="0.7"/>
                <line className={styles.textLine} x1="10" y1="16" x2="32" y2="16" stroke="#9b2335" strokeWidth="1.8" strokeLinecap="round" strokeDasharray="40"/>
                <line className={styles.textLine} x1="10" y1="27" x2="32" y2="27" stroke="#9b2335" strokeWidth="1.8" strokeLinecap="round" strokeDasharray="40"/>
                <line className={styles.textLine} x1="10" y1="38" x2="32" y2="38" stroke="#9b2335" strokeWidth="1.8" strokeLinecap="round" strokeDasharray="40"/>
                <path d="M36 2 L66 2 Q68 2 68 4 L68 52 Q68 54 66 54 L36 54 Z" fill="url(#pageGrad)" stroke="#d4cfc5" strokeWidth="0.5"/>
                <path d="M36 3 L68 3 Q70 3 70 5 L70 51 Q70 53 68 53 L36 53 Z" fill="url(#rightCoverGrad)" stroke="#7a1a28" strokeWidth="0.7"/>
                <path d="M39 6 L67 6 L67 50 L39 50 Z" fill="none" stroke="url(#goldGrad)" strokeWidth="0.8" opacity="0.7"/>
                <circle cx="53" cy="20" r="1.5" fill="#c9a84c" opacity="0.7"/>
                <circle cx="53" cy="28" r="1.5" fill="#c9a84c" opacity="0.7"/>
                <circle cx="53" cy="36" r="1.5" fill="#c9a84c" opacity="0.7"/>
                <rect x="33.5" y="2" width="5" height="52" fill="url(#spineGrad)" className={styles.spineLine}/>
                <line x1="36" y1="4" x2="36" y2="52" stroke="#c9a84c" strokeWidth="0.7" opacity="0.6"/>
              </g>
            </svg>
          </button>
        </div>
      </nav>

      {/* FULL-SCREEN MENU OVERLAY */}
      <div 
        className={`${styles.menuOverlay} ${isMenuOpen ? styles.menuOpen : ''}`}
        role="dialog"
        aria-modal="true"
        aria-label="導覽選單"
      >
        <div className={styles.curtain2}></div>
        <div className={styles.curtain}></div>

        {/* Top bar */}
        <div className={styles.overlayTopbar}>
          <span className={styles.overlayLogo}>北商傳書</span>
          <button 
            className={styles.overlayClose}
            onClick={closeMenu}
            aria-label="關閉選單"
          >
            ✕
          </button>
        </div>

        {/* Nav content */}
        <div className={styles.menuInner}>
          <div className={styles.overlayRule}></div>
          <nav>
            <ul className={styles.navList}>
              {navLinks.map((link, idx) => (
                <li key={link.href} className={styles.navItem} style={{ '--delay': `${0.35 + idx * 0.07}s` } as any}>
                  <Link
                    href={link.href}
                    className={styles.navLink}
                    onClick={closeMenu}
                  >
                    <span className={styles.navIndex}>{String(idx + 1).padStart(2, '0')}</span>
                    <span className={styles.navText}>
                      <span className={styles.navEn}>{link.enName}</span>
                      <span className={styles.navZh}>{link.name}</span>
                    </span>
                    <span className={styles.navArrow}>→</span>
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* Footer */}
        <div className={styles.overlayFooter}>
          <span className={styles.overlayQuote}>「書中自有千鍾粟，書中自有黃金屋。」</span>
          <div className={styles.overlayLineDeco}></div>
          <span className={styles.overlayQuote}>© 北商傳書</span>
        </div>
      </div>
    </>
  );
}