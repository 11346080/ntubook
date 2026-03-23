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
}

interface FormState {
  book: BookData & {
    isbn13?: string;
    isbn10?: string;
  };
  campusId: string;
  programTypeId: string;
  departmentId: string;
  classGroupId: string;
  originAcademicYear: string;
  originTerm: string;
  usedPrice: string;
  conditionLevel: string;
  description: string;
  sellerNote?: string;
  images: File[];
  imagePreviews: string[]; // Data URLs for persistent preview even if local files are deleted
}

interface ClassGroup {
  id: number;
  code: string;
  name_zh: string;
  grade_no: number;
  section_code: string;
  department: number;
  program_type: number;
}

interface Campus {
  id: number;
  code: string;
  name_zh: string;
}

interface ProgramType {
  id: number;
  code: string;
  name_zh: string;
}

interface Department {
  id: number;
  code: string;
  name_zh: string;
  campus?: number;
  program_type?: number;
}

interface Message {
  type: 'error' | 'success' | 'warning' | 'info';
  title: string;
  content: string;
  details?: string[];
}

// 條件等級映射（中文 → 英文）
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
  
  // 四級聯動選擇狀態
  const [campusList, setCampusList] = useState<Campus[]>([]);
  const [programTypeList, setProgramTypeList] = useState<ProgramType[]>([]);
  const [departmentList, setDepartmentList] = useState<Department[]>([]);
  const [classGroups, setClassGroups] = useState<ClassGroup[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(false);

  const [formState, setFormState] = useState<FormState>({
    book: {
      title: '',
      author: '',
      publisher: '',
      isbn13: '',
      isbn10: '',
    },
    campusId: '',
    programTypeId: '',
    departmentId: '',
    classGroupId: '',
    originAcademicYear: '',
    originTerm: '1',
    usedPrice: '',
    conditionLevel: '普通',
    description: '',
    sellerNote: '',
    images: [],
    imagePreviews: [],
  });

  const [isbnInput, setIsbnInput] = useState('');

  // 加載四級選擇數據 + 初始化 CSRF token
  useEffect(() => {
    const initializeAndFetchData = async () => {
      setIsLoadingData(true);
      try {
        // 1️⃣ 初始化 CSRF token
        console.log('🔐 Initializing CSRF token...');
        await fetch(`${API_BASE_URL}/listings/`, {
          method: 'GET',
          credentials: 'include',
        });
        console.log('✓ CSRF token initialized');

        // 2️⃣ 加載校區列表
        const campusRes = await fetch(`${API_BASE_URL}/core/campuses/`);
        if (campusRes.ok) {
          const campusData = await campusRes.json();
          const campuses = Array.isArray(campusData) ? campusData : campusData.data || [];
          setCampusList(campuses);
          console.log(`✓ Loaded ${campuses.length} campuses`);
        }

        // 3️⃣ 加載學制列表
        const progRes = await fetch(`${API_BASE_URL}/core/program-types/`);
        if (progRes.ok) {
          const progData = await progRes.json();
          const programs = Array.isArray(progData) ? progData : progData.data || [];
          setProgramTypeList(programs);
          console.log(`✓ Loaded ${programs.length} program types`);
        }
      } catch (error) {
        console.error('✗ Failed to load base data:', error);
      } finally {
        setIsLoadingData(false);
      }
    };

    initializeAndFetchData();
  }, []);

  // 當選擇校區或學制時，加載科系列表
  useEffect(() => {
    if (!formState.campusId || !formState.programTypeId) {
      setDepartmentList([]);
      setFormState(prev => ({ ...prev, departmentId: '', classGroupId: '' }));
      return;
    }

    const loadDepartments = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/core/departments/?campus_id=${formState.campusId}&program_type_id=${formState.programTypeId}`
        );
        if (response.ok) {
          const data = await response.json();
          const depts = Array.isArray(data) ? data : data.data || [];
          setDepartmentList(depts);
          console.log(`✓ Loaded ${depts.length} departments`);
        }
      } catch (error) {
        console.error('✗ Failed to load departments:', error);
      }
    };

    loadDepartments();
  }, [formState.campusId, formState.programTypeId]);

  // 當選擇科系時，加載班級列表
  useEffect(() => {
    if (!formState.departmentId) {
      setClassGroups([]);
      setFormState(prev => ({ ...prev, classGroupId: '' }));
      return;
    }

    const loadClassGroups = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/core/class-groups/?department_id=${formState.departmentId}`
        );
        if (response.ok) {
          const data = await response.json();
          const groups = Array.isArray(data) ? data : data.data || [];
          setClassGroups(groups);
          console.log(`✓ Loaded ${groups.length} class groups`);
        }
      } catch (error) {
        console.error('✗ Failed to load class groups:', error);
      }
    };

    loadClassGroups();
  }, [formState.departmentId]);

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

    try {
      const response = await fetch('/api/isbn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ isbn: isbnInput }),
      });

      const data = await response.json();

      if (response.status === 503) {
        // 服務暫時不可用 - 引導用戶手動填寫
        setMessage({
          type: 'info',
          title: '無法自動查詢',
          content: '暫時無法查詢書籍資訊，但您可以直接填寫書籍詳細資料。系統會為您自動指配刊登號碼。',
        });
      } else if (data.success && data.data) {
        setFormState((prev) => ({
          ...prev,
          book: {
            ...prev.book,
            ...data.data,
          },
        }));

        setMessage({
          type: 'success',
          title: '查詢成功',
          content: '書籍資訊已自動帶入，請確認無誤並補充其餘項目。',
        });
      } else {
        setMessage({
          type: 'warning',
          title: '查詢無結果',
          content: data.error || '暫未查獲此 ISBN 之書籍，但您可以手動填寫書籍資訊並繼續刊登。',
        });
      }
    } catch (error) {
      console.error('ISBN Query Error:', error);
      setMessage({
        type: 'warning',
        title: '無法連接',
        content: '無法連接書籍資料庫，但您可以直接填寫書籍詳細資料。系統會為您自動指配刊登號碼。',
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

    // 生成 data URL 的辅助函数
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

      // 检查文件类型
      if (!['image/jpeg', 'image/png', 'image/webp', 'image/gif'].includes(file.type)) {
        errors.push(`${file.name}: 不支援此檔案格式`);
        continue;
      }

      // 检查文件大小
      if (file.size > 10 * 1024 * 1024) {
        errors.push(`${file.name}: 檔案過大（超過 10MB）`);
        continue;
      }

      // NSFW 检查
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

        // 生成 data URL
        const dataUrl = await generateDataUrl(file);
        validImages.push(file);
        validPreviews.push(dataUrl);
      } catch (error) {
        console.error('NSFW Check Error:', error);
        // 检查失败时也允许上传
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

  // 移除圖片
  const handleRemoveImage = (index: number) => {
    setFormState((prev) => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index),
      imagePreviews: prev.imagePreviews.filter((_, i) => i !== index),
    }));
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

  // 提交表单
  // 获取 CSRF 令牌
  const getCsrfToken = (): string => {
    // 方法 1: 從 Cookie 獲取
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

    // 方法 2: 從 Meta Tag 獲取（備用）
    if (!cookieValue) {
      const tokenElement = document.querySelector('meta[name="csrf-token"]');
      if (tokenElement) {
        cookieValue = tokenElement.getAttribute('content') || '';
      }
    }

    // 方法 3: 從 DOM 元素獲取（Django 表單中的隱藏字段）
    if (!cookieValue) {
      const inputElement = document.querySelector('input[name="csrfmiddlewaretoken"]') as HTMLInputElement;
      if (inputElement) {
        cookieValue = inputElement.value;
      }
    }

    console.log(`🔐 CSRF Token (${cookieValue ? '✓ found' : '✗ not found'}): ${cookieValue ? cookieValue.substring(0, 10) + '...' : 'undefined'}`);
    return cookieValue;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearMessage();

    console.log('📋 Validating form...');

    // 验证必填字段
    const errors: string[] = [];
    const price = parseFloat(formState.usedPrice);
    const year = parseInt(formState.originAcademicYear);

    console.log('📊 Form state:', {
      title: formState.book.title,
      author: formState.book.author,
      publisher: formState.book.publisher,
      price: price,
      year: year,
      term: formState.originTerm,
      campus: formState.campusId,
      programType: formState.programTypeId,
      department: formState.departmentId,
      classGroup: formState.classGroupId,
      images: formState.images.length,
    });

    if (!formState.book.title?.trim()) errors.push('書名');
    if (!formState.book.author?.trim()) errors.push('作者');
    if (!formState.book.publisher?.trim()) errors.push('出版社');
    
    // 檢查價格是否是有效的數字且大於 0
    if (!formState.usedPrice || isNaN(price) || price <= 0) {
      errors.push('售價（需為有效數字）');
    }
    
    // 檢查年份是否是有效的數字
    if (!formState.originAcademicYear || isNaN(year) || year <= 0) {
      errors.push('課程年份（需為有效數字）');
    }
    
    if (!formState.originTerm) errors.push('學期');
    if (!formState.campusId) errors.push('校區');
    if (!formState.programTypeId) errors.push('學制');
    if (!formState.departmentId) errors.push('科系');
    if (!formState.classGroupId) errors.push('班級');
    if (formState.images.length < 3) errors.push('商品圖片（需至少 3 張）');

    if (errors.length > 0) {
      console.log('❌ Missing fields:', errors);
      setMessage({
        type: 'error',
        title: '遺漏必填項目',
        content: `請補充以下項目：${errors.join('、')}`,
      });
      return;
    }

    console.log('✓ Form validation passed');

    // 检查敏感词
    const titleSensitive = checkSensitiveWords(formState.book.title);
    const descriptionSensitive = checkSensitiveWords(formState.description);
    const allSensitive = [...new Set([...titleSensitive, ...descriptionSensitive])];

    if (allSensitive.length > 0) {
      console.log('⚠️ Sensitive words found:', allSensitive);
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
      console.log('📤 Starting submission...');
      
      // 转换图片为 base64
      console.log('📸 Converting images to base64...');
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
      console.log(`✓ Converted ${imageBase64List.length} images`);

      // 构建提交数据
      const submitData = {
        new_book: {
          isbn13: formState.book.isbn13 || '',
          isbn10: formState.book.isbn10 || '',
          title: formState.book.title,
          author_display: formState.book.author,
          publisher: formState.book.publisher,
        },
        origin_academic_year: parseInt(formState.originAcademicYear),
        origin_term: parseInt(formState.originTerm),
        origin_class_group_id: parseInt(formState.classGroupId),
        used_price: parseFloat(formState.usedPrice),
        condition_level: mapConditionLevel(formState.conditionLevel),
        description: formState.description,
        seller_note: formState.sellerNote || null,
        images: imageBase64List,
      };

      console.log('📦 Submit data prepared:', {
        book: submitData.new_book,
        price: submitData.used_price,
        images: imageBase64List.length,
      });

      // 获取 CSRF 令牌
      const csrfToken = getCsrfToken();
      console.log('🔐 CSRF token:', csrfToken ? '✓ Found' : '✗ Not found');

      // 提交至 Django 后端
      console.log(`🔗 Posting to ${API_BASE_URL}/listings/...`);
      const response = await fetch(`${API_BASE_URL}/listings/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrfToken && { 'X-CSRFToken': csrfToken }),
          },
          body: JSON.stringify(submitData),
          credentials: 'include',
        }
      );

      console.log(`📨 Response status:`, response.status, response.statusText);
      
      // Parse response safely
      let responseData;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        responseData = await response.json();
      } else {
        const text = await response.text();
        console.error('❌ Non-JSON response:', text.substring(0, 200));
        throw new Error('Server returned non-JSON response');
      }

      console.log('✓ Response received:', responseData.success ? '成功' : '失敗');

      if (responseData.success && responseData.data?.id) {
        console.log(`🎉 Listing created with ID: ${responseData.data.id}`);
        
        setMessage({
          type: 'success',
          title: '刊登成功',
          content: '感謝您的分享，書籍已成功上架！',
        });

        // 延迟 1.5 秒后跳转
        console.log('⏱️ Waiting 1.5s before redirect...');
        setTimeout(() => {
          console.log(`📍 Redirecting to /listings/${responseData.data.id}`);
          router.push(`/listings/${responseData.data.id}`);
        }, 1500);
      } else {
        console.error('❌ Submission failed:', responseData.error);
        
        setMessage({
          type: 'error',
          title: '刊登失敗',
          content: responseData.error?.message || '無法完成刊登，請稍後再試。',
          details: responseData.error?.details ? [JSON.stringify(responseData.error.details)] : undefined,
        });
      }
    } catch (error) {
      console.error('❌ Submit Error:', error);
      
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      setMessage({
        type: 'error',
        title: '提交錯誤',
        content: `伺服器發生錯誤：${errorMessage}`,
      });
    } finally {
      setIsSubmitting(false);
      console.log('✓ Submission process completed');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        {/* 标题區塊 */}
        <div className={styles.headerSection}>
          <h1 className={styles.pageTitle}>新增刊登</h1>
          <p className={styles.pageSubtitle}>
            刊登您的書籍，讓知識流動於校園的每個角落
          </p>
        </div>

        {/* 提示訊息 */}
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
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      usedPrice: e.target.value,
                    }))
                  }
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

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>課程年份</label>
                <input
                  type="number"
                  className={styles.input}
                  placeholder="如: 2024"
                  min="2000"
                  max={new Date().getFullYear()}
                  value={formState.originAcademicYear}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      originAcademicYear: e.target.value,
                    }))
                  }
                />
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>學期</label>
                <select
                  className={styles.select}
                  value={formState.originTerm}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      originTerm: e.target.value,
                    }))
                  }
                >
                  <option value="1">第一學期</option>
                  <option value="2">第二學期</option>
                </select>
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>校區</label>
                <select
                  className={styles.select}
                  value={formState.campusId}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      campusId: e.target.value,
                    }))
                  }
                >
                  <option value="">
                    {isLoadingData ? '加載中...' : '請選擇校區'}
                  </option>
                  {campusList.map((campus) => (
                    <option key={campus.id} value={campus.id}>
                      {campus.name_zh}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>學制</label>
                <select
                  className={styles.select}
                  value={formState.programTypeId}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      programTypeId: e.target.value,
                    }))
                  }
                  disabled={!formState.campusId}
                >
                  <option value="">
                    {!formState.campusId ? '請先選擇校區' : '請選擇學制'}
                  </option>
                  {programTypeList.map((program) => (
                    <option key={program.id} value={program.id}>
                      {program.name_zh}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>科系</label>
                <select
                  className={styles.select}
                  value={formState.departmentId}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      departmentId: e.target.value,
                    }))
                  }
                  disabled={!formState.campusId || !formState.programTypeId}
                >
                  <option value="">
                    {!formState.campusId || !formState.programTypeId
                      ? '請先選擇校區與學制'
                      : departmentList.length === 0
                      ? '無可用科系'
                      : '請選擇科系'}
                  </option>
                  {departmentList.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name_zh}
                    </option>
                  ))}
                </select>
              </div>

              <div className={styles.inputField}>
                <label className={`${styles.label} ${styles.labelRequired}`}>班級</label>
                <select
                  className={styles.select}
                  value={formState.classGroupId}
                  onChange={(e) =>
                    setFormState((prev) => ({
                      ...prev,
                      classGroupId: e.target.value,
                    }))
                  }
                  disabled={!formState.departmentId}
                >
                  <option value="">
                    {!formState.departmentId
                      ? '請先選擇科系'
                      : classGroups.length === 0
                      ? '無可用班級'
                      : '請選擇班級'}
                  </option>
                  {classGroups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name_zh}
                    </option>
                  ))}
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
              <div className={styles.uploadIcon}>📸</div>
              <div className={styles.uploadText}>點擊或拖放上傳圖片</div>
              <div className={styles.uploadSubtext}>
                支援 JPG、PNG 等格式，每張最大 10MB
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              className={styles.imageInput}
              multiple
              accept="image/*"
              onChange={(e) => handleImageUpload(e.target.files)}
              disabled={isCheckingImage}
            />

            {/* 圖片預覽 */}
            {formState.images.length > 0 && (
              <div className={styles.imagePreviewList}>
                {formState.imagePreviews.map((previewUrl, idx) => (
                  <div key={idx} className={styles.imagePreview}>
                    <img
                      src={previewUrl}
                      alt={`Preview ${idx + 1}`}
                      className={styles.imagePreviewImg}
                    />
                    <button
                      type="button"
                      className={styles.imageRemoveBtn}
                      onClick={() => handleRemoveImage(idx)}
                      title="移除此圖片"
                    >
                      ✕
                    </button>
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

      {/* Loading Overlay */}
      {(isSubmitting || isCheckingImage) && (
        <div className={styles.loadingOverlay}>
          <div className={styles.loadingSpinner}></div>
        </div>
      )}
    </div>
  );
}
