'use client';
import { Settings } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card } from '@/components/ui';

export default function Page() {
  return (
    <>
      <Header title="Настройки" subtitle="Настройки диспетчера" />
      <div className="p-4 lg:p-8">
        <Card className="max-w-lg mx-auto text-center py-16">
          <Settings size={40} className="text-slate-300 mx-auto mb-4" />
          <p className="text-slate-500 text-sm">Настройки диспетчера</p>
        </Card>
      </div>
    </>
  );
}
