'use client';

import { useState, useEffect } from 'react';
import styles from './image-carousel.module.css';

interface ListingImage {
  id: number;
  file_path: string;
  is_primary: boolean;
  sort_order: number;
}

interface ImageCarouselProps {
  images: ListingImage[];
  bookTitle: string;
  bookCoverUrl?: string;
}

export default function ImageCarousel({
  images,
  bookTitle,
  bookCoverUrl,
}: ImageCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageUrls, setImageUrls] = useState<(string | null)[]>([]);

  // Build API-based image URLs on client side
  useEffect(() => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    const backendUrl = API_BASE_URL.replace('/api', '');

    const urls = images.map((img) => {
      if (img.file_path) {
        return `${backendUrl}/media/${img.file_path}`;
      }
      return null;
    });

    // Add fallback cover if available
    if (urls.length === 0 && bookCoverUrl) {
      urls.push(bookCoverUrl);
    }

    setImageUrls(urls);
  }, [images, bookCoverUrl]);

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev === 0 ? imageUrls.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev === imageUrls.length - 1 ? 0 : prev + 1));
  };

  const goToIndex = (index: number) => {
    setCurrentIndex(index);
  };

  const currentImageUrl = imageUrls[currentIndex];
  const hasMultipleImages = imageUrls.length > 1;

  return (
    <div className={styles.container}>
      {currentImageUrl ? (
        <>
          <div className={styles.imageWrapper}>
            <img
              src={currentImageUrl}
              alt={`${bookTitle} - 第 ${currentIndex + 1} 張圖`}
              className={styles.image}
            />

            {hasMultipleImages && (
              <>
                <button
                  className={styles.navButton + ' ' + styles.prevButton}
                  onClick={handlePrevious}
                  aria-label="上一張圖片"
                  title="上一張"
                >
                  ‹
                </button>
                <button
                  className={styles.navButton + ' ' + styles.nextButton}
                  onClick={handleNext}
                  aria-label="下一張圖片"
                  title="下一張"
                >
                  ›
                </button>
              </>
            )}
          </div>

          {hasMultipleImages && (
            <div className={styles.indicatorContainer}>
              {imageUrls.map((_, index) => (
                <button
                  key={index}
                  className={styles.indicator + (index === currentIndex ? ' ' + styles.active : '')}
                  onClick={() => goToIndex(index)}
                  aria-label={`查看第 ${index + 1} 張圖片`}
                  title={`圖片 ${index + 1}/${imageUrls.length}`}
                />
              ))}
            </div>
          )}

          {hasMultipleImages && (
            <div className={styles.imageCounter}>
              {currentIndex + 1} / {imageUrls.length}
            </div>
          )}
        </>
      ) : (
        <div className={styles.placeholder}>
          <div className={styles.placeholderContent}>
            <p className={styles.placeholderEmoji}>📖</p>
            <p className={styles.placeholderText}>北商傳書</p>
          </div>
        </div>
      )}
    </div>
  );
}
