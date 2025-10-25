import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';
import { Toaster } from 'sonner';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Tangerine.trading - Modern Citrus Tech',
  description: 'Modern citrus-powered DeFi optimization for concentrated liquidity positions on Uniswap V3 for Base Network',
  icons: {
    icon: '/tangerine-logo.svg',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
        <Toaster theme="dark" position="top-right" />
      </body>
    </html>
  );
}