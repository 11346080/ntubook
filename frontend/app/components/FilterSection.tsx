'use client';

import { ReactNode } from 'react';

interface FilterSectionProps {
  children: ReactNode;
}

export default function FilterSection({ children }: FilterSectionProps) {
  return (
    <aside
      style={{
        position: 'sticky',
        top: '2rem',
      }}
    >
      {children}
    </aside>
  );
}
