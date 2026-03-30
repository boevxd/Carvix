'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Truck, Eye, EyeOff, AlertCircle, Loader2 } from 'lucide-react';
import { Button, Input } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { login, user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) {
      const roleMap: Record<string, string> = {
        admin: '/admin', Администратор: '/admin',
        dispatcher: '/dispatcher', Диспетчер: '/dispatcher',
      };
      router.push(roleMap[user.role_name] || '/dashboard');
    }
  }, [user, loading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!username || !password) { setError('Введите логин и пароль'); return; }
    setSubmitting(true);
    const result = await login(username, password);
    if (!result.success) setError(result.error || 'Неверный логин или пароль');
    setSubmitting(false);
  };

  const quickLogin = async (u: string, p: string) => {
    setUsername(u); setPassword(p);
    setSubmitting(true);
    const result = await login(u, p);
    if (!result.success) setError(result.error || 'Ошибка входа');
    setSubmitting(false);
  };

  const demoAccounts = [
    { label: 'Администратор', username: 'admin', password: 'admin' },
    { label: 'Диспетчер', username: 'dispatcher', password: 'dispatcher' },
    { label: 'Пользователь', username: 'user', password: 'user' },
  ];

  return (
    <div className=min-h-screen flex dark:bg-slate-950>
      <div className=flex-1 flex items-center justify-center px-6 py-12>
        <div className=w-full max-w-sm>
          <Link href=/ className=flex items-center gap-2.5 mb-10>
            <img src=/logo-carvix.png alt=Carvix className=w-9 h-9 rounded-lg object-cover />
            <span className=text-lg font-bold text-slate-900 dark:text-white tracking-tight>Carvix</span>
          </Link>

          <h1 className=text-2xl font-bold text-slate-900 dark:text-white mb-1>Вход в систему</h1>
          <p className=text-sm text-slate-500 dark:text-slate-400 mb-8>Управление автопарком — единая платформа</p>

          {error && (
            <div className=mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 flex items-center gap-2>
              <AlertCircle size={16} className=text-red-600 dark:text-red-400 flex-shrink-0 />
              <p className=text-sm text-red-700 dark:text-red-400>{error}</p>
            </div>
          )}

          <form className=space-y-5 onSubmit={handleSubmit}>
            <Input
              label=Логин
              type=text
              placeholder=admin
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
            />
            <div className=relative>
              <Input
                label=Пароль
                type={showPassword ? 'text' : 'password'}
                placeholder=Введите пароль
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={submitting}
              />
              <button
                type=button
                onClick={() => setShowPassword(!showPassword)}
                className=absolute right-3 top-[34px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
            <Button className=w-full size=lg type=submit disabled={submitting}>
              {submitting ? <><Loader2 size={16} className=animate-spin mr-2 />Вход...</> : 'Войти'}
            </Button>
          </form>

          <div className=mt-8 p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200/60 dark:border-slate-700/60>
            <p className=text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3>Быстрый вход</p>
            <div className=space-y-2>
              {demoAccounts.map((acc) => (
                <button
                  key={acc.username}
                  onClick={() => quickLogin(acc.username, acc.password)}
                  disabled={submitting}
                  className=flex items-center justify-between w-full p-2.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-brand-300 hover:shadow-sm transition-all text-sm disabled:opacity-50
                >
                  <span className=font-medium text-slate-700 dark:text-slate-200>{acc.label}</span>
                  <span className=text-xs text-brand-600>{acc.username} / {acc.password}</span>
                </button>
              ))}
            </div>
            <p className=text-[10px] text-slate-400 mt-3>Используются учётные записи из основного приложения Carvix</p>
          </div>
        </div>
      </div>

      <div className=hidden lg:flex flex-1 bg-slate-900 items-center justify-center p-12 relative overflow-hidden>
        <div className=absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-brand-900/30 via-slate-900 to-slate-900 />
        <div className=relative z-10 max-w-md text-center>
          <div className=w-16 h-16 rounded-2xl bg-brand-600/20 border border-brand-500/20 flex items-center justify-center mx-auto mb-8>
            <Truck className=text-brand-400 size={32} />
          </div>
          <h2 className=text-2xl font-bold text-white mb-3>Синхронизация с десктоп-приложением</h2>
          <p className=text-sm text-slate-400 leading-relaxed>
            Данные сайта и приложения Carvix полностью синхронизированы через единый API. Любые изменения отображаются в обоих интерфейсах в реальном времени.
          </p>
          <div className=mt-10 grid grid-cols-3 gap-4>
            {[
              { value: 'API', label: 'FastAPI бэкенд' },
              { value: 'SQLite', label: 'Единая БД' },
              { value: 'Real-time', label: 'Синхронизация' },
            ].map((s) => (
              <div key={s.label} className=text-center>
                <p className=text-xl font-bold text-white>{s.value}</p>
                <p className=text-[11px] text-slate-500 mt-1>{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
