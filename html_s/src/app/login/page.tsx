'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Truck, Eye, EyeOff, AlertCircle } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { useLocale } from '@/contexts/locale-context';
import { UserRole } from '@/types';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loginAsRole, user } = useAuth();
  const { t } = useLocale();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      const routes: Record<UserRole, string> = { driver: '/dashboard', dispatcher: '/dispatcher', admin: '/admin' };
      router.push(routes[user.role]);
    }
  }, [user, router]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!email || !password) { setError(t('auth.error.fill')); return; }
    const result = login(email, password);
    if (!result.success) setError(t(result.error || 'auth.error.invalid'));
  };

  const demoItems: { role: UserRole; label: string }[] = [
    { role: 'driver', label: t('role.driver') },
    { role: 'dispatcher', label: t('role.dispatcher') },
    { role: 'admin', label: t('role.admin') },
  ];

  return (
    <div className="min-h-screen flex dark:bg-slate-950">
      {/* Left: Form */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <Link href="/" className="flex items-center gap-2.5 mb-10">
            <img src="/logo-carvix.png" alt="Carvix" className="w-9 h-9 rounded-lg object-cover" />
            <span className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Carvix</span>
          </Link>

          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{t('auth.login')}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">{t('auth.login.subtitle')}</p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-2">
              <AlertCircle size={16} className="text-red-600 dark:text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <Input
              label={t('auth.email')}
              type="email"
              placeholder="name@company.ru"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <div className="relative">
              <Input
                label={t('auth.password')}
                type={showPassword ? 'text' : 'password'}
                placeholder={t('auth.password.placeholder')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-[34px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500" />
                <span className="text-sm text-slate-600 dark:text-slate-400">{t('auth.remember')}</span>
              </label>
              <span className="text-sm font-medium text-brand-600 hover:text-brand-700 transition-colors cursor-pointer">
                {t('auth.forgot')}
              </span>
            </div>

            <Button className="w-full" size="lg" type="submit">{t('auth.submit')}</Button>
          </form>

          <div className="mt-8 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t('auth.no_account')}{' '}
              <Link href="/register" className="font-medium text-brand-600 hover:text-brand-700 transition-colors">
                {t('auth.register_link')}
              </Link>
            </p>
          </div>

          {/* Demo access shortcuts */}
          <div className="mt-8 p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-700/60">
            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3">{t('auth.demo')}</p>
            <div className="space-y-2">
              {demoItems.map((item) => (
                <button
                  key={item.role}
                  onClick={() => loginAsRole(item.role)}
                  className="flex items-center justify-between w-full p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-brand-300 hover:shadow-sm transition-all text-sm"
                >
                  <span className="font-medium text-slate-700 dark:text-slate-200">{item.label}</span>
                  <span className="text-xs text-brand-600">{t('auth.enter')}</span>
                </button>
              ))}
            </div>
            <p className="text-[10px] text-slate-400 mt-3">driver@fleet.ru / driver123 · dispatcher@fleet.ru / dispatcher123 · admin@fleet.ru / admin123</p>
          </div>
        </div>
      </div>

      {/* Right: Visual */}
      <div className="hidden lg:flex flex-1 bg-slate-900 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-brand-900/30 via-slate-900 to-slate-900" />
        <div className="relative z-10 max-w-md text-center">
          <div className="w-16 h-16 rounded-2xl bg-brand-600/20 border border-brand-500/20 flex items-center justify-center mx-auto mb-8">
            <Truck className="text-brand-400" size={32} />
          </div>
          <h2 className="text-2xl font-bold text-white mb-3">
            Единая платформа для управления автопарком
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Подача заявок на ремонт, контроль технического обслуживания, аналитика эффективности — всё в одном месте.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-4">
            {[
              { value: '150+', label: 'Транспортных средств' },
              { value: '24/7', label: 'Мониторинг' },
              { value: '98%', label: 'Вовремя ТО' },
            ].map((s) => (
              <div key={s.label} className="text-center">
                <p className="text-xl font-bold text-white">{s.value}</p>
                <p className="text-[11px] text-slate-500 mt-1">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
