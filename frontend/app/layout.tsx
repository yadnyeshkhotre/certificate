import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'QR Certificate Generator',
  description: 'Generate and verify certificates with QR codes.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
