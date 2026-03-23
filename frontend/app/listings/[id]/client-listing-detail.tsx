'use client';

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
  const book = listing.book;
  const seller = listing.seller;
  const price = parseFloat(listing.used_price).toFixed(2);

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
            <button className={styles.btnPrimary}>我要預約</button>
            <button className={styles.btnSecondary}>加入收藏</button>
          </div>
        </div>
      </div>
    </div>
  );
}
