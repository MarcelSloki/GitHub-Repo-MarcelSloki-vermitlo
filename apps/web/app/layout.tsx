import type { ReactNode } from 'react';

export const metadata = {
  title: 'Vermitlo MVP',
  description: 'Bid management MVP scaffold for Vermitlo',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
