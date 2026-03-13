# 北商傳書 (NTUB Used Books)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.x-green.svg)](https://www.djangoproject.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.11-orange.svg)](https://mariadb.org/)

北商傳書是一款專為臺北商業大學校內師生設計的二手課本交易平台，旨在解決傳統二手書交易中資訊不透明、買賣雙方缺乏信任基礎以及交易流程繁瑣等問題。

---

## 1. 企劃主旨

在校園二手書交易場景中，學生普遍面臨資訊散落各處難以整合、難以確認書籍適用課程是否正確、以及與陌生人交易時的信任風險等痛點。本平台透過校內帳號限定登入機制，建立基於真實身份的信任網絡，同時提供集中化的書籍瀏覽與搜尋功能，讓買家能夠快速找到符合自身需求的課本。

本專案的最終願景是打造一個安全、透明且高效的校園二手書交易生態系統，不僅幫助學生以合理的價格取得所需教材，也提供賣家一個便捷的書籍流通渠道，進而促進校園資源的循環利用。

---

## 2. 核心概念

- **校園身份驗證**：僅開放 `@ntub.edu.tw` 校內電子郵件註冊與登入，結合 Cloudflare Turnstile 與 Google OAuth 機制，確保所有使用者均為校內師生，建立交易信任基礎。

- **狀態驅動的刊登生命週期**：書籍刊登採用 PENDING（審核中）→ PUBLISHED（上架）→ RESERVED（保留）→ SOLD（已售）→ OFF_SHELF（下架）的狀態流轉機制，搭配風險評分與敏感詞檢查系統，確保平台內容合規性。

- **隱私保護的媒合流程**：買賣雙方的聯絡方式在交易完成前完全保密，僅於預約請求被接受後才釋出對方電子郵件，透過站內通知與 Email 雙軌機制推動交易進度。

- **集中化的搜尋與推薦**：支援關鍵字、ISBN、價格區間、系所、年級、課程名稱等多維度進階搜尋，並提供最新上架與熱門書籍等區塊，幫助使用者快速發現符合需求的教材。

---

## 3. 使用者角色

| 角色 | 說明 | 主要權限與任務 |
|------|------|---------------|
| **學生 (Student)** | 校內師生帳號持有者，可同時作為買家與賣家 | 作為買家：瀏覽書籍、搜尋、收藏、發送預約請求；作為賣家：建立/編輯/管理刊登、回覆預約請求、完成交易；個人資料管理、查看通知 |
| **管理員 (Admin)** | 系統維運人員，具備後台管理權限 | 用戶帳號管理（停權/解封）、刊登管理（強制下架）、檢舉案件處理、系統統計儀表板檢視 |
| **系統 (System)** | 自動化後端服務 | 敏感詞檢查、風險評分計算、站內與 Email 通知觸發、事件日誌記錄 |

---

## 4. 技術架構

| 層級 | 技術 | 說明 |
|------|------|------|
| **前端** | HTML5 / Bootstrap 5 | 響應式網頁介面，採用 Bootstrap Grid 系統與元件庫建構各頁面 |
| **前端互動** | JavaScript (原生) | DOM 操作、AJAX 非同步請求、表單驗證 |
| **後端框架** | Django 5.x (MTV 架構) | Model-Template-View 設計模式，依業務功能拆分為 accounts、books、listings、requests、reports、notifications、core 等 App |
| **認證機制** | Django Allauth + Google OAuth 2.0 | 校內帳號 OAuth 登入，整合 Cloudflare Turnstile 與 Google reCAPTCHA v3 進行人機驗證與風險評分 |
| **表單處理** | Django Forms / ModelForms | 伺服器端表單驗證，確保資料正確性 |
| **後台管理** | Django Admin | 初期快速建置後台管理介面，後續視需求擴充自建儀表板 |
| **API 層** | Django REST Framework (DRF) | 提供 RESTful API 端點，支援前期 Postman 測試與後期前端框架整合；(選用) JWT 權杖驗證 |
| **資料庫** | MariaDB 10.11 LTS | 關聯式資料庫，存放使用者、書籍、刊登、預約、檢舉、通知等 14 張資料表 |
| **網域** | ntubook.com | 專案網域，正式上線環境部署位置 |
| **版本控制** | Git / GitHub | 雙分支開發策略：`dev` 分支作為測試靶場，`main` 分支為正式上線版本 |

---

## 5. 專案結構

```
ntub-usedbooks/
├── accounts/          # 使用者帳號與個人資料
├── books/             # 書籍主檔與適用課程
├── listings/          # 書籍刊登與圖片
├── requests/          # 預約請求管理
├── reports/           # 檢舉管理
├── notifications/     # 通知系統
├── core/              # 共用元件（學制、系所、班級等）
├── templates/         # HTML 模板
├── static/            # 靜態資源 (CSS, JS, Images)
├── ntub_usedbooks/    # Django 專案設定
└── manage.py
```

---

## 6. 快速開始

### 環境需求

- Python 3.10+
- Django 5.x
- MariaDB 10.11 LTS
- Node.js (可選，用於靜態資產管理)

### 安裝步驟

```bash
# 1. 複製專案
git clone https://github.com/your-repo/ntub-usedbooks.git
cd ntub-usedbooks

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，設定資料庫與金鑰

# 5. 執行資料庫遷移
python manage.py migrate

# 6. 載入初始資料 (可選)
python manage.py loaddata fixtures/

# 7. 啟動開發伺服器
python manage.py runserver
```

---

## 7. 功能總覽

### 學生功能

- 校內帳號 OAuth 登入
- 瀏覽與進階搜尋書籍
- 收藏書籍
- 發送預約請求
- 建立與管理刊登
- 個人資料維護
- 接收站內與 Email 通知

### 管理員功能

- 用戶帳號管理
- 刊登強制下架
- 檢舉案件處理
- 系統統計儀表板

---

## 8. API 設計

本專案提供 RESTful API，採用統一的回傳格式：

```json
// 成功回傳
{
  "success": true,
  "data": { ... },
  "message": "選填的提示訊息"
}

// 失敗回傳
{
  "success": false,
  "error": {
    "code": "錯誤代碼",
    "message": "錯誤訊息"
  }
}
```

詳細 API 規格請參閱 [API Documentation](docs/API.md)。

---

## 9. 授權

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

---

## 10. 聯絡我們

- 專案網站：[ntubook.com](https://ntubook.com)
- 問題回報：[GitHub Issues](https://github.com/your-repo/ntub-usedbooks/issues)
