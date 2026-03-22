import { notFound } from 'next/navigation';
import ImageCarousel from './image-carousel';
import styles from './listing-detail.module.css';

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
  file_path: string;
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

interface ApiResponse {
  success: boolean;
  data?: ListingDetailData;
  error?: { code: string; message: string };
}

async function getListingDetail(id: string): Promise<ListingDetailData | null> {
  try {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    const response = await fetch(`${API_BASE_URL}/listings/${id}/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
    });
    if (!response.ok) return null;
    const data: ApiResponse = await response.json();
    return data.success && data.data ? data.data : null;
  } catch (error) {
    console.error('Error:', error);
    return null;
  }
}

export default async function ListingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const listing = await getListingDetail(id);
  if (!listing) return <NotFoundView />;

  const book = listing.book;
  const seller = listing.seller;
  const price = parseFloat(listing.used_price).toFixed(2);

  return (
    <div className={styles.container}>
      <div className={styles.wrapper}>
        <div className={styles.imageSection}>
          <ImageCarousel 
            images={listing.images}
            bookTitle={book?.title || '未知書籍'}
            bookCoverUrl={book?.cover_image_url}
          />
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
            <button className={styles.btnPrimary}>我要預約</button>
            <button className={styles.btnSecondary}>加入收藏</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function NotFoundView() {
  return (
    <div className={styles.notFoundContainer}>
      <div className={styles.notFoundContent}>
        <p className={styles.notFoundEmoji}></p>
        <h1 className={styles.notFoundTitle}>查無此書</h1>
        <p className={styles.notFoundMessage}>或許已隨墨香遠去。請返回列表重新查閱。</p>
        <a href="/listings" className={styles.backButton}>返回列表</a>
      </div>
    </div>
  );
}
