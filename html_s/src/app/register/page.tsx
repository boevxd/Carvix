'use client';

import React from 'react';
import Link from 'next/link';
import { Truck, Info, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui';

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-6 py-12">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/60 dark:border-slate-700/60 shadow-card p-8 text-center">
          <Link href="/" className="flex items-center justify-center gap-2.5 mb-8">
            <img src="/logo-carvix.png" alt="Carvix" className="w-9 h-9 rounded-lg object-cover" />
            <span className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Carvix</span>
          </Link>

          <div className="w-14 h-14 rounded-2xl bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center mx-auto mb-6">
            <Info size={28} className="text-blue-600" />
          </div>

          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-3">Регистрация</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 leading-relaxed">
            Учётные записи создаются администратором системы в десктоп-приложении Carvix.
            Если у вас ещё нет доступа — обратитесь к вашему администратору.
          </p>

          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 mb-6 text-left space-y-2">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Тестовые учётные записи</p>
            {[
              { role: 'Администратор', login: 'admin', pass: 'admin' },
              { role: 'Диспетчер', login: 'dispatcher', pass: '123456' },
              { role: 'Директор', login: 'director', pass: '123456' },
            ].map((acc) => (
              <div key={acc.login} className="flex items-center justify-between text-sm">
                <span className="text-slate-600 dark:text-slate-400">{acc.role}</span>
                <span className="text-xs text-brand-600 font-mono">{acc.login} / {acc.pass}</span>
              </div>
            ))}
          </div>

          <Link href="/login">
            <Button className="w-full" size="lg">
              <ArrowLeft size={16} />
              Войти в систему
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
