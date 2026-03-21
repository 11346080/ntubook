'use client';

import { ReactNode } from 'react';

interface FilterSectionProps {
  children: ReactNode;
}

export default function FilterSection({ children }: FilterSectionProps) {
  return (
    <div className="filter-section">
      <h6><i className="fas fa-filter"></i> 篩選條件</h6>
      {children}
    </div>
  );
}
