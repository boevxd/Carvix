import type { Metadata } from 'next';
import './globals.css';
import { Providers } from './providers';

export const metadata: Metadata = {
  title: 'Carvix — Управление ремонтом и обслуживанием автопарка',
  description:
    'Carvix — информационная система управления ремонтом и техническим обслуживанием корпоративного автопарка. Подача заявок, уведомления о ТО, история обращений, взаимодействие с диспетчерской.',
  icons: { icon: '/logo-carvix.png' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
