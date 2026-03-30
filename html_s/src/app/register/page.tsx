'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Truck, AlertCircle } from 'lucide-react';
import { Button, Input, Select } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { useLocale } from '@/contexts/locale-context';
import { UserRole } from '@/types';

export default function RegisterPage() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState<UserRole>('driver');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [terms, setTerms] = useState(false);
  const [error, setError] = useState('');
  const { register, user } = useAuth();
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
    if (!firstName || !lastName || !email || !password) { setError(t('auth.error.fill')); return; }
    if (password !== confirmPassword) { setError(t('auth.error.passwords')); return; }
    if (!terms) { setError(t('auth.error.terms')); return; }
    const result = register({ firstName, lastName, email, phone, role, password });
    if (!result.success) setError(result.error || t('common.error'));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-6 py-12">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200/60 dark:border-slate-700/60 shadow-card p-8">
          <Link href="/" className="flex items-center gap-2.5 mb-8">
            <img src="/logo-carvix.png" alt="Carvix" className="w-9 h-9 rounded-lg object-cover" />
            <span className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">Carvix</span>
          </Link>

          <h1 className="text-2xl font-bold text-slate-900 dark:text-white mb-1">{t('auth.register')}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-8">{t('auth.register.subtitle')}</p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-2">
              <AlertCircle size={16} className="text-red-600 dark:text-red-400 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="grid grid-cols-2 gap-4">
              <Input label={t('auth.firstName')} placeholder="Алексей" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
              <Input label={t('auth.lastName')} placeholder="Петров" value={lastName} onChange={(e) => setLastName(e.target.value)} />
            </div>
            <Input label={t('auth.email')} type="email" placeholder="name@company.ru" value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input label={t('auth.phone')} type="tel" placeholder="+7 (___) ___-__-__" value={phone} onChange={(e) => setPhone(e.target.value)} />
            <Select
              label={t('auth.role')}
              placeholder={t('auth.role.placeholder')}
              value={role}
              onChange={(e) => setRole(e.target.value as UserRole)}
              options={[
                { value: 'driver', label: t('role.driver') },
                { value: 'dispatcher', label: t('role.dispatcher') },
                { value: 'admin', label: t('role.admin') },
              ]}
            />
            <Input label={t('auth.password')} type="password" placeholder={t('auth.password.min')} value={password} onChange={(e) => setPassword(e.target.value)} />
            <Input label={t('auth.password.confirm')} type="password" placeholder={t('auth.password.repeat')} value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />

            <label className="flex items-start gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={terms}
                onChange={(e) => setTerms(e.target.checked)}
                className="w-4 h-4 mt-0.5 rounded border-slate-300 text-brand-600 focus:ring-brand-500"
              />
              <span className="text-sm text-slate-600 dark:text-slate-400">
                {t('auth.terms')}{' '}
                <span className="text-brand-600 hover:underline cursor-pointer">{t('auth.terms_link')}</span>{' '}
                {t('auth.and')}{' '}
                <span className="text-brand-600 hover:underline cursor-pointer">{t('auth.privacy_link')}</span>
              </span>
            </label>

            <Button className="w-full" size="lg" type="submit">{t('auth.register.submit')}</Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t('auth.has_account')}{' '}
              <Link href="/login" className="font-medium text-brand-600 hover:text-brand-700 transition-colors">
                {t('auth.login_link')}
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
