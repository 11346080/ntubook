'use client';

import { useState, useRef, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './create-listing.module.css';

// API 基礎 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// 敏感词库（基础版本，应与后端敏感词检查保证一致）
// 实际应使用完整的中文敏感词库或npm包：chinese-sensitive-words
const SENSITIVE_WORDS = [
  // 赌博相关
  '博彩', '赌博', '赌钱', '娱乐城',
  // 毒品相关
  '毒品', '大麻', '海洛因', '冰毒', '摇头丸',
  // 色情相关
  '色情', '淫秽', '黄色', '18禁',
  // 暴力相关
  '暴力', '恐怖', '炸弹', '枪支',
  // 诈骗相关
  '诈骗', '欺诈', '洗钱', '非法',
  // 违法相关
  '走私', '贩毒', '贩运',
  // 仇恨相关
  '仇恨', '歧视', '恐怖分子',
  // 平台特定的敏感词
  '假货', '假冒', '翻新', '来路不明',
];

function checkSensitiveWords(text: string): string[] {
  const found: string[] = [];
  const lowerText = text.toLowerCase();

  for (const word of SENSITIVE_WORDS) {
    if (lowerText.includes(word.toLowerCase())) {
      if (!found.includes(word)) {
        found.push(word);
      }
    }
  }

  return found;
}

interface BookData {
  title: string;
  author: string;
  publisher: string;
  isbn13?: string;
  isbn10?: string;
  publication_year?: number | null;
  publication_date_text?: string | null;
  cover_image_url?: string | null;
}

interface FormState {
  book: BookData;
  usedPrice: string;
  conditionLevel: string;
  description: string;
  sellerNote?: string;
  images: File[];
  imagePreviews: string[];
}

interface IsbnQueryMeta {
  source?: 'local' | 'external_api' | 'not_found' | 'error';
  message?: string;
  isNew?: boolean;
}

// /api/isbn 後端回應格式（消除 unknown，讓子屬性存取型別安全）
interface IsbnApiResponse {
  success: boolean;
  error?: string;
  note?: string;
  data?: {
    isbn13?: string;
    isbn10?: string;
    title?: string;
    author?: string;
    publisher?: string;
    publication_year?: number | null;
    publication_date_text?: string | null;
    cover_image_url?: string | null;
  };
  _source?: 'local' | 'external_api';
  _message?: string;
  _is_new?: boolean;
}

interface ProfileResponse {
  id: number;
  display_name: string;
  student_no: string | null;
  program_type_id: number | null;
  department_id: number | null;
  class_group_id: number | null;
  grade_no: number | null;
  contact_email: string | null;
  avatar_url: string | null;
}

interface Message {
  type: 'error' | 'success' | 'warning' | 'info';
  title: string;
  content: string;
  details?: string[];
}

const CONDITION_LEVEL_MAP: Record<string, string> = {
  '全新': 'LIKE_NEW',
  '近全新': 'LIKE_NEW',
  '良好': 'GOOD',
  '普通': 'FAIR',
  '差': 'POOR',
};

function mapConditionLevel(chineseCondition: string): string {
  return CONDITION_LEVEL_MAP[chineseCondition] || 'FAIR';
}

export default function CreateListingPage() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoadingIsbn, setIsLoadingIsbn] = useState(false);
  const [isCheckingImage, setIsCheckingImage] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<Message | null>(null);

  const [userProfile, setUserProfile] = useState<ProfileResponse | null>(null);
  const [userGradeDisplay, setUserGradeDisplay] = useState<string>('');

  const [formState, setFormState] = useState<FormState>({
    book: {
      title: '',
      author: '',
      publisher: '',
      isbn13: '',
      isbn10: '',
      publication_year: null,
      publication_date_text: null,
      cover_image_url: null,
    },
    usedPrice: '',
    conditionLevel: '普通',
    description: '',
    sellerNote: '',
    images: [],
    imagePreviews: [],
  });

  const [isbnInput, setIsbnInput] = useState('');
  const [isbnQueryMeta, setIsbnQueryMeta] = useState<IsbnQueryMeta>({});

  // 初始化：獲取用戶 profile（用於 academic context）
  useEffect(() => {
    const initializeAndFetchData = async () => {
      try {
        // 讓後端有機會刷新 session
        await fetch(`${API_BASE_URL}/listings/`, {
          method: 'GET',
          credentials: 'include',
        });

        const profileRes = await fetch('/api/accounts/profile', {
          method: 'GET',
          credentials: 'include',
        });
        if (profileRes.ok) {
          const profile: ProfileResponse = await profileRes.json();
          setUserProfile(profile);
          if (profile.grade_no) {
            const displayGrade = profile.grade_no - 1;
            setUserGradeDisplay(
              displayGrade === 1 ? '一年級' :
              displayGrade === 2 ? '二年級' :
              displayGrade === 3 ? '三年級' :
              displayGrade === 4 ? '四年級' :
              `${displayGrade}年級`
            );
          }
        }
      } catch (error) {
        // Failed to load base data
      }
    };

    initializeAndFetchData();
  }, []);

  // 清除提示訊息
  const clearMessage = useCallback(() => {
    setMessage(null);
  }, []);

  // 查询 ISBN
  const handleQueryIsbn = async () => {
    if (!isbnInput.trim()) {
      setMessage({
        type: 'error',
        title: '請輸入 ISBN',
        content: '請輸入有效的 ISBN（10 或 13 位數字）',
      });
      return;
    }

    setIsLoadingIsbn(true);
    clearMessage();
    setIsbnQueryMeta({});

    try {
      // [DEBUG] 查詢前
      console.log('[ISBN Lookup] 開始查詢, isbn=', isbnInput);

      const response = await fetch('/api/isbn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isbn: isbnInput }),
      });

      // [DEBUG] 收到 /api/isbn 回應
      console.log('[ISBN Lookup] /api/isbn 回應, status=', response.status);

      const data: IsbnApiResponse = await response.json();

      // [DEBUG] 解析後的資料內容
      console.log('[ISBN Lookup] /api/isbn 回應內容, data=', JSON.stringify(data));

      // -------- 後端直接錯誤 --------
      if (!response.ok) {
        setMessage({
          type: 'error',
          title: '查詢服務暫停',
          content: data.error || 'ISBN 查詢服務目前無法使用，請稍後再試，或直接手動填寫書籍資訊。',
          details: data.note ? [data.note] : undefined,
        });
        setIsbnQueryMeta({ source: 'error', message: '服務暫停' });
        return;
      }

      // -------- 查無資料 --------
      if (!data.success) {
        setIsbnQueryMeta({ source: 'not_found', message: data.error });
        setMessage({
          type: 'warning',
          title: '查無結果',
          content: data.error || '此 ISBN 查無書籍資訊，請確認號碼正確，或直接手動填寫。',
          details: data.note ? [data.note] : undefined,
        });
        return;
      }

      // -------- 查詢成功 --------
      if (data.data) {
        const bookInfo = data.data;
        const source = data._source as 'local' | 'external_api';
        const isNew = data._is_new as boolean;
        const apiMessage = data._message as string;

        // 只填「目前為空」的欄位，避免覆蓋使用者已填內容
        setFormState((prev) => {
          const updates: Partial<BookData> = {};
          if (!prev.book.title && bookInfo.title) updates.title = bookInfo.title;
          if (!prev.book.author && bookInfo.author) updates.author = bookInfo.author;
          if (!prev.book.publisher && bookInfo.publisher) updates.publisher = bookInfo.publisher;
          if (!prev.book.isbn13 && bookInfo.isbn13) updates.isbn13 = bookInfo.isbn13;
          if (!prev.book.isbn10 && bookInfo.isbn10) updates.isbn10 = bookInfo.isbn10;
          if (!prev.book.publication_year && bookInfo.publication_year) updates.publication_year = bookInfo.publication_year;
          if (!prev.book.publication_date_text && bookInfo.publication_date_text) updates.publication_date_text = bookInfo.publication_date_text;
          if (!prev.book.cover_image_url && bookInfo.cover_image_url) updates.cover_image_url = bookInfo.cover_image_url;

          return {
            ...prev,
            book: { ...prev.book, ...updates },
          };
        });

        // 同步 isbnInput 顯示（若有 isbn13）
        if (bookInfo.isbn13) {
          setIsbnInput(bookInfo.isbn13);
        } else if (bookInfo.isbn10) {
          setIsbnInput(bookInfo.isbn10);
        }

        // 記錄查詢元資料
        setIsbnQueryMeta({ source, isNew, message: apiMessage });

        // 根據來源給出不同色調的成功提示
        if (source === 'local') {
          setMessage({
            type: 'success',
            title: '從本地資料庫取得',
            content: apiMessage || '書籍資訊已自動帶入，請確認無誤並補充其餘項目。',
          });
        } else if (source === 'external_api') {
          setMessage({
            type: 'success',
            title: isNew ? '已從外部資料庫取得並寫入' : '已從外部資料庫取得',
            content: apiMessage || '書籍資訊已自動帶入，請確認無誤並補充其餘項目。',
          });
        }
      }
    } catch (error) {
      setIsbnQueryMeta({ source: 'error', message: '網路錯誤' });
      setMessage({
        type: 'warning',
        title: '無法連接',
        content: '無法連接書籍資料庫，但您可以直接填寫書籍詳細資料。',
      });
    } finally {
      setIsLoadingIsbn(false);
    }
  };

  // 处理图片上传
  const handleImageUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setIsCheckingImage(true);
    clearMessage();

    const validImages: File[] = [];
    const validPreviews: string[] = [];
    const errors: string[] = [];

    const generateDataUrl = (file: File): Promise<string> => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    };

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      // ✨ 圖片格式限制：只允許 jpg / png
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        errors.push(`${file.name}: 僅支援 JPG 與 PNG 格式`);
        continue;
      }

      if (file.size > 10 * 1024 * 1024) {
        errors.push(`${file.name}: 檔案過大（超過 10MB）`);
        continue;
      }

      const formData = new FormData();
      formData.append('image', file);

      try {
        const nsfwResponse = await fetch('/api/nsfw-check', {
          method: 'POST',
          body: formData,
        });

        const nsfwData = await nsfwResponse.json();

        if (!nsfwData.is_safe) {
          setMessage({
            type: 'error',
            title: '圖片意境不符',
            content: '圖片意境似有違和，請重新挑選清雅之作...',
          });
          continue;
        }

        const dataUrl = await generateDataUrl(file);
        validImages.push(file);
        validPreviews.push(dataUrl);
      } catch (error) {
        const dataUrl = await generateDataUrl(file);
        validImages.push(file);
        validPreviews.push(dataUrl);
      }
    }

    if (errors.length > 0 && validImages.length === 0) {
      setMessage({
        type: 'error',
        title: '圖片上傳失敗',
        content: '所有圖片均無法上傳',
        details: errors,
      });
      setIsCheckingImage(false);
      return;
    }

    setFormState((prev) => ({
      ...prev,
      images: [...prev.images, ...validImages],
      imagePreviews: [...prev.imagePreviews, ...validPreviews],
    }));

    if (errors.length > 0) {
      setMessage({
        type: 'warning',
        title: '部分圖片上傳失敗',
        content: '已上傳部分有效圖片，其他圖片因檢驗未通過被跳過。',
        details: errors,
      });
    } else {
      setMessage({
        type: 'success',
        title: '圖片上傳成功',
        content: `已新增 ${validImages.length} 張圖片`,
      });
    }

    setIsCheckingImage(false);
  };

  // 拖放區域事件
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleImageUpload(e.dataTransfer.files);
  };

  const getCsrfToken = (): string => {
    const name = 'csrftoken';
    let cookieValue = '';

    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }

    if (!cookieValue) {
      const tokenElement = document.querySelector('meta[name="csrf-token"]');
      if (tokenElement) {
        cookieValue = tokenElement.getAttribute('content') || '';
      }
    }

    if (!cookieValue) {
      const inputElement = document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement;
      if (inputElement) {
        cookieValue = inputElement.value;
      }
    }

    return cookieValue;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessage();

    const errors: string[] = [];
    const price = parseFloat(formState.usedPrice);

    if (!formState.book.title?.trim()) errors.push('書名');
    if (!formState.book.author?.trim()) errors.push('作者');
    if (!formState.book.publisher?.trim()) errors.push('出版社');

    if (!formState.usedPrice || isNaN(price) || price <= 0) {
      errors.push('售價（需為有效數字）');
    }

    if (formState.images.length < 3) errors.push('商品圖片（需至少 3 張）');

    if (errors.length > 0) {
      setMessage({
        type: 'error',
        title: '遺漏必填項目',
        content: `請補充以下項目：${errors.join('、')}`,
      });
      return;
    }

    const titleSensitive = checkSensitiveWords(formState.book.title);
    const descriptionSensitive = checkSensitiveWords(formState.description);
    const allSensitive = [...new Set([...titleSensitive, ...descriptionSensitive])];

    if (allSensitive.length > 0) {
      setMessage({
        type: 'error',
        title: '用詞不妥',
        content: '用詞似有不妥，請重新斟酌筆墨...',
        details: allSensitive.map((word) => `您使用了敏感詞：「${word}」`),
      });
      return;
    }

    setIsSubmitting(true);

    try {
      const imagePromises = formState.images.map(
        (file) =>
          new Promise<string>((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
              resolve(reader.result as string);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
          })
      );

      const imageBase64List = await Promise.all(imagePromises);

      let isbn13 = formState.book.isbn13 || '';
      let isbn10 = formState.book.isbn10 || '';

      if (!isbn13 && !isbn10 && isbnInput.trim()) {
        if (isbnInput.trim().replace(/[^0-9X]/g, '').length === 13) {
          isbn13 = isbnInput.trim();
        } else if (isbnInput.trim().replace(/[^0-9X]/g, '').length === 10) {
          isbn10 = isbnInput.trim();
        } else {
          isbn13 = isbnInput.trim();
        }
      }

      const submitData: Record<string, unknown> = {
        new_book: {
          isbn13: isbn13,
          isbn10: isbn10,
          title: formState.book.title,
          author_display: formState.book.author,
          publisher: formState.book.publisher,
          publication_year: formState.book.publication_year || null,
          publication_date_text: formState.book.publication_date_text || null,
        },
        used_price: parseFloat(formState.usedPrice),
        condition_level: mapConditionLevel(formState.conditionLevel),
        description: formState.description,
        seller_note: formState.sellerNote || null,
        images: imageBase64List,
      };

      const csrfToken = getCsrfToken();

      const response = await fetch(`${API_BASE_URL}/listings/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken && { 'X-CSRFToken': csrfToken }),
        },
        body: JSON.stringify(submitData),
        credentials: 'include',
      });

      let responseData;
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        const text = await response.text();
        throw new Error('Server returned non-JSON response');
      }

      if (responseData.success && responseData.data?.id) {
        setMessage({
          type: 'success',
          title: '書卷已遞交',
          content: '小二正在為您審核，請稍候...（通常在 1 分鐘內完成）',
        });

        setTimeout(() => {
          router.push('/dashboard');
        }, 2000);
      } else {
        setMessage({
          type: 'error',
          title: '刊登失敗',
          content: responseData.error?.message || '無法完成刊登，請稍後再試。',
          details: responseData.error?.details ? [JSON.stringify(responseData.error.details)] : undefined,
        });
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);

      setMessage({
        type: 'error',
        title: '提交錯誤',
        content: `伺服器發生錯誤：${errorMessage}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.headerSection}>
          <h1 className={styles.pageTitle}>新增刊登</h1>
          <p className={styles.pageSubtitle}>
            刊登您的書籍，讓知識流動於校園的每個角落
          </p>
        </div>

        {message && (
          <div className={`${styles.messageBox} ${styles[`message${message.type.charAt(0).toUpperCase() + message.type.slice(1)}`]}`}>
            <div className={styles.messageTitle}>{message.title}</div>
            <div className={styles.messageContent}>{message.content}</div>
            {message.details && message.details.length > 0 && (
              <ul className={styles.sensitiveWordsWarning}>
                {message.details.map((detail, idx) => (
                  <li key={idx}>{detail}</li>
                ))}
              </ul>
            )}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* ISBN 查詢區塊 */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>
              書籍資訊
              <span className={styles.sectionBadge}>必填</span>
            </h2>

            <div className={styles.isbnBlock}>
              <div className={styles.inputField}>
                <label className={styles.label}>ISBN (10 或 13 位)</label>
                <input
                  type="text"
                  className={styles.input}
                  placeholder="如: 9789570827044"
                  value={isbnInput}
                  onChange={(e) => setIsbnInput(e.target.value)}
                  disabled={isLoadingIsbn}
                />
                <div className={styles.helperText}>
                  支援 ISBN-10 或 ISBN-13，將自動帶入書籍資訊
                </div>
              </div>
              <button
                type="button"
                className={styles.btnOutline}
                onClick={handleQueryIsbn}
                disabled={isLoadingIsbn || !isbnInput.trim()}
              >
                {isLoadingIsbn ? '查詢中...' : '查詢'}
              </button>
            </div>

            {/* 書籍資訊表單 */}
            <div className={styles.formGrid}>
              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>書名</label>
                <input
                  type="text"
                  className={styles.input}
                  placeholder="請輸入書名"
                  value={formState.book.title}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      book: { ...prev.book, title: e.target.value },
                    }))
                  }
                />
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>作者</label>
                <input
                  type="text"
                  className={styles.input}
                  placeholder="請輸入作者"
                  value={formState.book.author}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      book: { ...prev.book, author: e.target.value },
                    }))
                  }
                />
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>出版社</label>
                <input
                  type="text"
                  className={styles.input}
                  placeholder="請輸入出版社"
                  value={formState.book.publisher}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      book: { ...prev.book, publisher: e.target.value },
                    }))
                  }
                />
              </div>

              <div className={styles.inputField}>
                <label className={styles.label}>書籍年份</label>
                <input
                  type="number"
                  className={styles.input}
                  placeholder="如: 2024"
                  min="1900"
                  max={new Date().getFullYear()}
                  value={formState.book.publication_year ?? ''}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      book: {
                        ...prev.book,
                        publication_year: e.target.value ? parseInt(e.target.value) : null,
                      },
                    }))
                  }
                  onInput={(e) => {
                    setFormState((prev) => ({
                      ...prev,
                      book: {
                        ...prev.book,
                        publication_year: (e.target as HTMLInputElement).value
                          ? parseInt((e.target as HTMLInputElement).value)
                          : null,
                      },
                    }));
                  }}
                />
                <div className={styles.helperText}>
                  書籍的出版年份（ISBN 查詢後自動帶入）
                </div>
              </div>
            </div>
          </section>

          {/* 刊登資訊區塊 */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>
              刊登資訊
              <span className={styles.sectionBadge}>必填</span>
            </h2>

            <div className={styles.formGrid}>
              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>售價 (元)</label>
                <input
                  type="number"
                  className={styles.input}
                  placeholder="0"
                  min="1"
                  step="10"
                  value={formState.usedPrice}
                  onChange={(e) => {
                    setFormState((prev) => ({
                      ...prev,
                      usedPrice: e.target.value,
                    }));
                  }}
                  onInput={(e) => {
                    setFormState((prev) => ({
                      ...prev,
                      usedPrice: (e.target as HTMLInputElement).value,
                    }));
                  }}
                />
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>
                  書況
                </label>
                <select
                  className={styles.select}
                  value={formState.conditionLevel}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      conditionLevel: e.target.value,
                    }))
                  }
                >
                  <option value="全新">全新</option>
                  <option value="近全新">近全新</option>
                  <option value="良好">良好</option>
                  <option value="普通">普通</option>
                  <option value="差">差</option>
                </select>
              </div>
            </div>

            <div className={styles.inputField} style={{ marginTop: '1.5rem' }}>
              <label className={`${styles.label} ${styles.labelRequired}`}>商品描述</label>
              <textarea
                className={styles.textarea}
                placeholder="請詳細描述書籍狀況、特殊標記或可議價等資訊..."
                value={formState.description}
                onChange={(e) =>
                  setFormState((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
              />
              <div className={styles.helperText}>
                字數越詳細，越能吸引有興趣的買家
              </div>
            </div>

            <div className={styles.inputField}>
              <label className={styles.label}>賣家備註 (可選)</label>
              <textarea
                className={styles.textarea}
                placeholder="您希望買家注意的事項..."
                value={formState.sellerNote}
                onChange={(e) =>
                  setFormState((prev) => ({
                    ...prev,
                    sellerNote: e.target.value,
                  }))
                }
                style={{ minHeight: '80px' }}
              />
            </div>
          </section>

          {/* 圖片上傳區塊 */}
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>
              商品圖片
              <span className={styles.sectionBadge}>必填</span>
            </h2>

            <div
              className={`${styles.imageUploadArea} ${isDragging ? styles.dragging : ''}`}
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className={styles.uploadText}>點擊或拖放上傳圖片</div>
              <div className={styles.uploadSubtext}>
                支援 JPG、PNG 格式，每張最大 10MB，至少 3 張
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              className={styles.imageInput}
              multiple
              accept="image/jpeg,image/png"
              onChange={(e) => handleImageUpload(e.target.files)}
              disabled={isCheckingImage}
            />

            {formState.images.length > 0 && (
              <div className={styles.imagePreviewList}>
                {formState.imagePreviews.map((previewUrl, idx) => (
                  <div key={idx} className={styles.imagePreview}>
                    <img
                      src={previewUrl}
                      alt={`Preview ${idx + 1}`}
                      className={styles.imagePreviewImg}
                    />
                  </div>
                ))}
              </div>
            )}

            <div className={styles.helperText} style={{ marginTop: '1rem' }}>
              已上傳 {formState.images.length} 張圖片
            </div>
          </section>

          {/* 提交按鈕 */}
          <div className={styles.submitSection}>
            <button
              type="button"
              className={styles.backBtn}
              onClick={() => router.back()}
              disabled={isSubmitting}
            >
              返回
            </button>
            <button
              type="submit"
              className={styles.btnPrimary}
              disabled={isSubmitting || isLoadingIsbn || isCheckingImage}
            >
              {isSubmitting ? '刊登中...' : '送出刊登'}
            </button>
          </div>
        </form>
      </div>

      {(isSubmitting || isCheckingImage) && (
        <div className={styles.loadingOverlay}>
          <div className={styles.loadingSpinner}></div>
        </div>
      )}
    </div>
  );
}
