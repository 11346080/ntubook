'use client';

interface Listing {
  id: number;
  title: string;
  author_display: string;
  used_price: number;
  condition_level: string;
  cover_image_url?: string;
}

export default function ListingCard({ listing }: { listing: Listing }) {
  return (
    <div className="listing-card">
      {listing.cover_image_url && (
        <div className="listing-image">
          <img src={listing.cover_image_url} alt={listing.title} />
        </div>
      )}
      <div className="listing-content">
        <h5 className="listing-title">{listing.title}</h5>
        <p className="listing-author">{listing.author_display}</p>
        <p className="listing-price">NT${listing.used_price}</p>
        <span className="listing-condition">{listing.condition_level}</span>
      </div>
    </div>
  );
}
