import { notFound } from 'next/navigation';
import styles from './listing-detail.module.css';
import ClientListingDetail from './client-listing-detail';

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
  image_base64: string;  // base64 data URL (data:image/jpeg;base64,...)
  mime_type: string;     // e.g., "image/jpeg"
  file_name: string;     // e.g., "listing_1_img_1.jpeg"
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

  return <ClientListingDetail listing={listing} />;
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
