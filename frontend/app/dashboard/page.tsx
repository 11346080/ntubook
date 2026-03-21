'use client';

import { useState } from 'react';

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState({
    display_name: '林小美',
    student_no: 'B11234567',
    email: 'b11234567@ntub.edu.tw',
    department: '資訊管理系',
    grade: 2,
  });

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: 發送更新請求至後端
    console.log('保存個人資料:', profileData);
  };

  return (
    <div className="mt-4">
      {/* 使用者檔案卡片 */}
      <div className="profile-card">
        <div className="profile-content">
          <div className="profile-avatar">
            <i className="fas fa-user"></i>
          </div>
          <div className="profile-info">
            <h2>{profileData.display_name}</h2>
            <p><i className="fas fa-id-card"></i> 學號：{profileData.student_no}</p>
            <p><i className="fas fa-building"></i> {profileData.department} {profileData.grade}年級</p>
            <div className="profile-stats">
              <div className="profile-stat">
                <div className="profile-stat-value">12</div>
                <div className="profile-stat-label">已刊登</div>
              </div>
              <div className="profile-stat">
                <div className="profile-stat-value">8</div>
                <div className="profile-stat-label">已售出</div>
              </div>
              <div className="profile-stat">
                <div className="profile-stat-value">4.8</div>
                <div className="profile-stat-label">評分</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 分頁籤 */}
      <ul className="nav nav-tabs" id="dashboardTabs" role="tablist">
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
            type="button"
          >
            <i className="fas fa-user-edit"></i> 個人資料
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'listings' ? 'active' : ''}`}
            onClick={() => setActiveTab('listings')}
            type="button"
          >
            <i className="fas fa-book"></i> 我的刊登
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'requests' ? 'active' : ''}`}
            onClick={() => setActiveTab('requests')}
            type="button"
          >
            <i className="fas fa-inbox"></i> 我的預約
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'favorites' ? 'active' : ''}`}
            onClick={() => setActiveTab('favorites')}
            type="button"
          >
            <i className="fas fa-heart"></i> 我的收藏
          </button>
        </li>
      </ul>

      {/* Tab 內容 */}
      <div className="tab-content" id="dashboardTabContent">
        {/* Tab 1: 個人資料 */}
        {activeTab === 'profile' && (
          <div className="form-section">
            <h5><i className="fas fa-edit"></i> 編輯個人資料</h5>
            <form onSubmit={handleSaveProfile}>
              <div className="row">
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="display_name">暱稱 *</label>
                    <input
                      type="text"
                      id="display_name"
                      name="display_name"
                      value={profileData.display_name}
                      onChange={handleProfileChange}
                      required
                    />
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="student_no">學號 *</label>
                    <input
                      type="text"
                      id="student_no"
                      name="student_no"
                      value={profileData.student_no}
                      onChange={handleProfileChange}
                      required
                      disabled
                    />
                  </div>
                </div>
              </div>
              <div className="row">
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="email">校內信箱 *</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={profileData.email}
                      onChange={handleProfileChange}
                      required
                    />
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="form-group">
                    <label htmlFor="department">系所</label>
                    <input
                      type="text"
                      id="department"
                      name="department"
                      value={profileData.department}
                      onChange={handleProfileChange}
                      disabled
                    />
                  </div>
                </div>
              </div>
              <button type="submit" className="btn btn-primary">
                <i className="fas fa-save"></i> 保存
              </button>
            </form>
          </div>
        )}

        {/* Tab 2: 我的刊登 */}
        {activeTab === 'listings' && (
          <div className="form-section">
            <h5><i className="fas fa-book"></i> 我的刊登</h5>
            <p className="text-muted">暫無刊登。<a href="#">建立新刊登</a></p>
          </div>
        )}

        {/* Tab 3: 我的預約 */}
        {activeTab === 'requests' && (
          <div className="form-section">
            <h5><i className="fas fa-inbox"></i> 我的預約</h5>
            <p className="text-muted">暫無預約請求。</p>
          </div>
        )}

        {/* Tab 4: 我的收藏 */}
        {activeTab === 'favorites' && (
          <div className="form-section">
            <h5><i className="fas fa-heart"></i> 我的收藏</h5>
            <p className="text-muted">暫無收藏的書籍。</p>
          </div>
        )}
      </div>
    </div>
  );
}
