'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Navbar() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 將搜尋邏輯連接至 API
    console.log('搜尋:', searchQuery);
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-light">
      <div className="container-fluid">
        {/* Logo */}
        <Link className="navbar-brand" href="/">
          NTUBook
        </Link>

        {/* Toggler for Mobile */}
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarContent"
          aria-controls="navbarContent"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Navbar Content */}
        <div className="collapse navbar-collapse" id="navbarContent">
          {/* Search Box (Center) */}
          <form className="search-box ms-auto me-auto" onSubmit={handleSearch}>
            <input
              type="text"
              placeholder="搜尋書籍、作者、ISBN..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="btn-search" type="submit">
              <i className="fas fa-search"></i>
            </button>
          </form>

          {/* Right Menu */}
          <ul className="navbar-nav ms-auto">
            <li className="nav-item">
              <Link className="nav-link" href="/listings">
                我的刊登
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" href="/dashboard">
                會員中心
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link nav-notification" href="/notifications">
                <i className="fas fa-bell"></i>
                <span className="notification-badge">3</span>
              </Link>
            </li>
            <li className="nav-item">
              <button className="btn btn-logout" onClick={() => {
                // TODO: 實作登出邏輯
                console.log('登出');
              }}>
                登出
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
}
