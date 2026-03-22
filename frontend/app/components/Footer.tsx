'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useState } from 'react';
import styles from '../style/Footer.module.css';

export default function Footer() {
  const [logoError, setLogoError] = useState(false);
  const currentYear = new Date().getFullYear();

  const footerSections = [
    {
      title: '關於我們',
      links: [
        { name: '平台簡介', href: '#about' },
        { name: '聯絡我們', href: '#contact' },
        { name: '常見問題', href: '#faq' },
      ],
    },
    {
      title: '政策',
      links: [
        { name: '隱私政策', href: '#privacy' },
        { name: '使用條款', href: '#terms' },
        { name: '交易條款', href: '#transaction' },
      ],
    },
    {
      title: '社群',
      links: [
        { name: 'Facebook', href: '#facebook' },
        { name: 'Instagram', href: '#instagram' },
        { name: '聯絡方式', href: '#email' },
      ],
    },
  ];

  return (
    <footer
      className={`mt-auto py-5 ${styles.footer}`}
      style={{
        backgroundColor: 'var(--color-bg-light)',
        borderTop: '1px solid var(--color-border)',
      }}
    >
      <div className="container-lg">
        <div className="row mb-5">
          {/* 品牌信息 */}
          <div className="col-lg-3 mb-4 mb-lg-0">
            <div className={styles.brandSection}>
              <h5
                className="fw-bold mb-3 d-flex align-items-center gap-2"
                style={{
                  color: 'var(--color-seal)',
                  fontFamily: "'Noto Serif TC', serif",
                  fontSize: '20px',
                }}
              >
                {/* Logo 圖片 - 支援文字回退 */}
                {!logoError ? (
                  <Image
                  src="/images/Logo.png"
                  alt="NTUB 二手書平台 Logo"
                  width={100}         
                  height={65}         
                  priority
                  quality={90}
                  onError={() => setLogoError(true)}
                  style={{ 
                    objectFit: 'contain', 
                    maxHeight: '65px', 
                    width: 'auto' 
                  }}
                />
                ) : (
                  <span
                    style={{
                      fontFamily: "'Noto Serif TC', serif",
                      fontSize: '16px',
                      fontWeight: 'bold',
                      color: 'var(--color-seal)',
                    }}
                  >
                    NTUBooks
                  </span>
                )}
                北商傳書
              </h5>
              <p
                className="small"
                style={{
                  color: 'var(--color-text-secondary)',
                  lineHeight: '1.8',
                }}
              >
                國立台北商業大學學生二手書交易平台，讓知識流動，讓資源循環。
              </p>
            </div>
          </div>

          {/* 導航連結 */}
          {footerSections.map((section) => (
            <div key={section.title} className="col-lg-3 mb-4 mb-lg-0">
              <h6
                className="fw-bold mb-3"
                style={{
                  color: 'var(--color-text-primary)',
                  fontSize: '14px',
                  letterSpacing: '0.5px',
                }}
              >
                {section.title}
              </h6>
              <ul className={`list-unstyled gap-2 ${styles.linkList}`}>
                {section.links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className={styles.footerLink}
                      style={{
                        color: 'var(--color-text-secondary)',
                        textDecoration: 'none',
                        fontSize: '14px',
                        transition: 'all var(--transition-duration) ease',
                      }}
                    >
                      {link.name}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* 聯絡方式 */}
          <div className="col-lg-3">
            <h6
              className="fw-bold mb-3"
              style={{
                color: 'var(--color-text-primary)',
                fontSize: '14px',
                letterSpacing: '0.5px',
              }}
            >
              聯絡我們
            </h6>
            <div className="small" style={{ color: 'var(--color-text-secondary)' }}>
              <p className="mb-2">
                <i className="fas fa-envelope me-2" style={{ color: 'var(--color-seal)' }}></i>
                support@ntub-books.tw
              </p>
              <p>
                <i className="fas fa-phone me-2" style={{ color: 'var(--color-seal)' }}></i>
                (02) 2323-2456
              </p>
            </div>
          </div>
        </div>

        {/* 分隔線 */}
        <hr style={{ borderColor: 'var(--color-border)', opacity: '0.5' }} />

        {/* 版權宣告 */}
        <div
          className="row align-items-center"
          style={{
            color: 'var(--color-text-secondary)',
            fontSize: '13px',
          }}
        >
          <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
            <p className="mb-0">
              &copy; {currentYear} 國立台北商業大學 北商傳書。版權所有。
            </p>
          </div>
          <div className="col-md-6 text-center text-md-end">
            <div className={styles.footerBottom}>
              <span>設計體現東方美學</span>
              <span className="mx-2">·</span>
              <span>專為北商學生服務</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
