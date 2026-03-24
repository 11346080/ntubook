'use client';

import { useState } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import styles from './listing-detail.module.css';
import ImageCarousel from './image-carousel';

interface Book {
  id: number;
  title: string;
  author_display: string;
  isbn13: string;
  isbn10?: string;
  publisher: string;
  publication_year?: number;
  publication_date_text?: string;
  edition?: string;
  cover_image_url?: string;
}

interface Department {
  id: number;
  code?: string;
  name_zh: string;
}

interface Seller {
  id: number;
  display_name: string;
  department?: Department | null;
}

interface ListingImage {
  id: number;
  image_base64: string;
  mime_type: string;
  file_name: string;
  is_primary: boolean;
  sort_order: number;
}

interface ClassGroup {
  id: number;
  code: string;
  name_zh: string;
  department?: Department | null;
}

interface ListingDetailData {
  id: number;
  book: Book | null;
  seller: Seller | null;
  used_price: string;
  condition_level: string;
  condition_level_display: string;
  description?: string;
  seller_note?: string;
  status: string;
  origin_academic_year: number;
  origin_term: number;
  origin_class_group?: ClassGroup | null;
  images: ListingImage[];
  created_at: string;
  updated_at: string;
}

interface ClientListingDetailProps {
  listing: ListingDetailData;
}

export default function ClientListingDetail({
  listing,
}: ClientListingDetailProps) {
  const { data: session } = useSession();
  const router = useRouter();
  const book = listing.book;
  const seller = listing.seller;
  const price = parseFloat(listing.used_price).toFixed(2);
  
  const [isFavorited, setIsFavorited] = useState(false);
  const [isLoadingFavorite, setIsLoadingFavorite] = useState(false);
  const [showReserveModal, setShowReserveModal] = useState(false);
  const [reserveMessage, setReserveMessage] = useState('');
  const [isSubmittingReserve, setIsSubmittingReserve] = useState(false);

  // 處理加入/移除收藏
  const handleToggleFavorite = async () => {
    // 檢查使用者是否已登入
    if (!session?.user) {
      const confirmed = window.confirm(
        '此操作需要登入。是否前往登入頁面？\n\nThis action requires login. Go to login page?'
      );
      if (confirmed) {
        const currentPath = window.location.pathname + window.location.search;
        router.push(`/login?callbackUrl=${encodeURIComponent(currentPath)}`);
      }
      return;
    }

    setIsLoadingFavorite(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const method = isFavorited ? 'DELETE' : 'POST';
      const response = await fetch(`${API_BASE_URL}/books/${book?.id}/favorite/`, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (response.ok) {
        setIsFavorited(!isFavorited);
      } else if (response.status === 401) {
        alert('您的登入已過期，請重新登入');
        router.push('/login');
      } else {
        alert('操作失敗，請稍後重試');
      }
    } catch (error) {
      // Toggle favorite error
      alert('無法連接伺服器');
    } finally {
      setIsLoadingFavorite(false);
    }
  };

  // 處理送出預約
  const handleSubmitReserve = async () => {
    // 檢查使用者是否已登入
    if (!session?.user) {
      const confirmed = window.confirm(
        '此操作需要登入。是否前往登入頁面？\n\nThis action requires login. Go to login page?'
      );
      if (confirmed) {
        const currentPath = window.location.pathname + window.location.search;
        router.push(`/login?callbackUrl=${encodeURIComponent(currentPath)}`);
      }
      return;
    }

    if (!reserveMessage.trim()) {
      alert('請填寫留言');
      return;
    }

    setIsSubmittingReserve(true);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_BASE_URL}/listings/${listing.id}/requests/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          buyer_message: reserveMessage,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        alert('預約成功！');
        setShowReserveModal(false);
        setReserveMessage('');
      } else if (response.status === 401) {
        alert('您的登入已過期，請重新登入');
        router.push('/login');
      } else {
        alert(data.error?.message || '預約失敗，請稍後重試');
      }
    } catch (error) {
      // Reserve error
      alert('無法連接伺服器');
    } finally {
      setIsSubmittingReserve(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.imageSection}>
          {/* Use ImageCarousel for multiple images */}
          {listing.images && listing.images.length > 0 ? (
            <ImageCarousel
              images={listing.images}
              bookTitle={book?.title || '書籍'}
              bookCoverUrl={book?.cover_image_url}
            />
          ) : book?.cover_image_url ? (
            <img
              src={book.cover_image_url}
              alt={book?.title || '書籍圖片'}
              className={styles.image}
            />
          ) : (
            <div className={styles.imagePlaceholder}>
              📖
              <p>北商傳書</p>
            </div>
          )}
        </div>

        <div className={styles.infoSection}>
          <div className={styles.headerArea}>
            <h1 className={styles.bookTitle}>{book?.title || '未知書籍'}</h1>
            <p className={styles.bookMeta}>
              {book?.author_display && <span>{book.author_display}</span>}
              {book?.author_display && book?.publisher && <span> • </span>}
              {book?.publisher && <span>{book.publisher}</span>}
            </p>
            {book?.edition && <p className={styles.bookEdition}>版次: {book.edition}</p>}
          </div>

          <div className={styles.priceArea}>
            <span className={styles.price}>NT$ {price}</span>
          </div>

          <div className={styles.tagsArea}>
            <span className={styles.tag}>{listing.condition_level_display}</span>
            {seller?.department && <span className={styles.tag}>{seller.department.name_zh}</span>}
            {listing.origin_class_group && (
              <span className={styles.tag}>
                {listing.origin_academic_year} 年級 {listing.origin_term} 學期
              </span>
            )}
          </div>

          {(book?.isbn13 || book?.isbn10) && (
            <div className={styles.isbnArea}>
              {book.isbn13 && <p>ISBN-13: {book.isbn13}</p>}
              {book.isbn10 && <p>ISBN-10: {book.isbn10}</p>}
            </div>
          )}

          <div className={styles.divider} />

          {(listing.description || listing.seller_note) && (
            <div className={styles.descriptionArea}>
              {listing.description && (
                <div className={styles.descriptionBlock}>
                  <h3 className={styles.descriptionTitle}>商品描述</h3>
                  <p className={styles.descriptionText}>{listing.description}</p>
                </div>
              )}
              {listing.seller_note && (
                <div className={styles.descriptionBlock}>
                  <h3 className={styles.descriptionTitle}>賣家備註</h3>
                  <p className={styles.descriptionText}>{listing.seller_note}</p>
                </div>
              )}
            </div>
          )}

          {seller && (
            <div className={styles.sellerArea}>
              <h3 className={styles.sellerTitle}>賣家資訊</h3>
              <div className={styles.sellerInfo}>
                <span className={styles.sellerName}>{seller.display_name}</span>
                {seller.department && (
                  <span className={styles.sellerDept}>{seller.department.name_zh}</span>
                )}
              </div>
            </div>
          )}

          <div className={styles.ctaArea}>
            <button 
              className={styles.btnPrimary}
              onClick={() => {
                if (!session?.user) {
                  const confirmed = window.confirm(
                    '此操作需要登入。是否前往登入頁面？\n\nThis action requires login. Go to login page?'
                  );
                  if (confirmed) {
                    const currentPath = window.location.pathname + window.location.search;
                    router.push(`/login?callbackUrl=${encodeURIComponent(currentPath)}`);
                  }
                } else {
                  setShowReserveModal(true);
                }
              }}
              disabled={isSubmittingReserve}
            >
              我要預約
            </button>
            <button 
              className={styles.btnSecondary}
              onClick={handleToggleFavorite}
              disabled={isLoadingFavorite}
              style={{
                backgroundColor: isFavorited ? '#9b2335' : 'transparent',
                color: isFavorited ? '#f5edd8' : '#9b2335',
              }}
            >
              {isFavorited ? '❤️ 已收藏' : '🤍 加入收藏'}
            </button>
          </div>

          {/* 預約模態框 */}
          {showReserveModal && (
            <div className={styles.modalOverlay} onClick={() => setShowReserveModal(false)}>
              <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
                <div className={styles.modalHeader}>
                  <h2>我要預約</h2>
                  <button 
                    className={styles.closeBtn}
                    onClick={() => setShowReserveModal(false)}
                  >
                    ✕
                  </button>
                </div>
                
                <div className={styles.modalBody}>
                  <p className={styles.bookInfo}>
                    <strong>{book?.title}</strong><br />
                    NT$ {price}
                  </p>
                  
                  <label htmlFor="reserveMessage" className={styles.label}>
                    給賣家的留言
                  </label>
                  <textarea
                    id="reserveMessage"
                    className={styles.textarea}
                    placeholder="例如：何時可交貨？可否議價？"
                    value={reserveMessage}
                    onChange={(e) => setReserveMessage(e.target.value)}
                    rows={4}
                  />
                </div>

                <div className={styles.modalFooter}>
                  <button 
                    className={styles.btnCancel}
                    onClick={() => setShowReserveModal(false)}
                  >
                    取消
                  </button>
                  <button 
                    className={styles.btnConfirm}
                    onClick={handleSubmitReserve}
                    disabled={isSubmittingReserve}
                  >
                    {isSubmittingReserve ? '送出中...' : '確認預約'}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
