'use client';

import React, { useState, useEffect } from 'react';
import { User, Palette, Bell, Shield, Check, Sun, Moon, Monitor, Loader2 } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { useTheme } from '@/contexts/theme-context';
import { useLocale } from '@/contexts/locale-context';
import { cn } from '@/lib/utils';
import { users as apiUsers } from '@/lib/api';

type Tab = 'profile' | 'appearance' | 'notifications' | 'security';

export default function SettingsPage() {
  const { user, updateProfile, changePassword } = useAuth();
  const { theme, setTheme } = useTheme();
  const { t, locale, setLocale } = useLocale();
  const [activeTab, setActiveTab] = useState<Tab>('profile');

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [department, setDepartment] = useState('');
  const [profileSaved, setProfileSaved] = useState(false);
  const [profileLoading, setProfileLoading] = useState(false);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [notifEmail, setNotifEmail] = useState(true);
  const [notifSaved, setNotifSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setPhone(user.phone || '');
      setDepartment(user.department || '');
    }
  }, [user]);

  const nameParts = fullName.split(' ');
  const initials = nameParts.length >= 2
    ? nameParts[0].charAt(0) + nameParts[1].charAt(0)
    : nameParts[0]?.charAt(0) ?? '?';

  const handleSaveProfile = async () => {
    if (!user) return;
    setProfileLoading(true);
    try {
      const updated = await apiUsers.update(user.id, { full_name: fullName, email, phone, department });
      updateProfile(updated);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 2000);
    } catch {}
    setProfileLoading(false);
  };

  const handleChangePassword = async () => {
    setPasswordMsg(null);
    if (newPassword !== confirmNewPassword) {
      setPasswordMsg({ type: 'error', text: 'Пароли не совпадают' });
      return;
    }
    if (newPassword.length < 6) {
      setPasswordMsg({ type: 'error', text: 'Пароль должен быть не менее 6 символов' });
      return;
    }
    setPasswordLoading(true);
    const result = await changePassword(currentPassword, newPassword);
    if (result.success) {
      setPasswordMsg({ type: 'success', text: 'Пароль успешно изменён' });
      setCurrentPassword(''); setNewPassword(''); setConfirmNewPassword('');
    } else {
      setPasswordMsg({ type: 'error', text: result.error || 'Ошибка смены пароля' });
    }
    setPasswordLoading(false);
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'profile', label: 'Профиль', icon: <User size={18} /> },
    { id: 'appearance', label: 'Оформление', icon: <Palette size={18} /> },
    { id: 'notifications', label: 'Уведомления', icon: <Bell size={18} /> },
    { id: 'security', label: 'Безопасность', icon: <Shield size={18} /> },
  ];

  const themeOptions: { value: 'light' | 'dark' | 'system'; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: 'Светлая', icon: <Sun size={20} /> },
    { value: 'dark', label: 'Тёмная', icon: <Moon size={20} /> },
    { value: 'system', label: 'Системная', icon: <Monitor size={20} /> },
  ];

  if (!user) return null;

  return (
    <>
      <Header title="Настройки" subtitle="Управление профилем и параметрами" />
      <div className="p-4 lg:p-8 max-w-4xl">
        <div className="flex gap-1 mb-8 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl w-fit flex-wrap">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all',
                activeTab === tab.id
                  ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
              )}
            >
              {tab.icon}
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          ))}
        </div>

        {activeTab === 'profile' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Профиль</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Информация о вашей учётной записи</p>

            <div className="flex items-center gap-4 mb-8">
              <div className="w-16 h-16 rounded-full bg-brand-600 flex items-center justify-center text-xl font-bold text-white flex-shrink-0">
                {initials}
              </div>
              <div>
                <p className="text-base font-semibold text-slate-900 dark:text-white">{fullName}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{email}</p>
                <p className="text-xs text-brand-600 mt-0.5">{user.role_name}</p>
              </div>
            </div>

            <div className="space-y-5 max-w-lg">
              <Input label="Полное имя" value={fullName} onChange={(e) => setFullName(e.target.value)} />
              <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input label="Телефон" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />
              <Input label="Подразделение" value={department} onChange={(e) => setDepartment(e.target.value)} />
              <div className="flex items-center gap-3 pt-2">
                <Button onClick={handleSaveProfile} disabled={profileLoading}>
                  {profileLoading ? (
                    <><Loader2 size={16} className="animate-spin" /> Сохранение...</>
                  ) : profileSaved ? (
                    <><Check size={16} /> Сохранено</>
                  ) : 'Сохранить'}
                </Button>
              </div>
            </div>
          </Card>
        )}

        {activeTab === 'appearance' && (
          <div className="space-y-6">
            <Card padding="lg">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Тема оформления</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Выберите предпочтительную тему интерфейса</p>
              <div className="grid grid-cols-3 gap-3">
                {themeOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setTheme(opt.value)}
                    className={cn(
                      'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all',
                      theme === opt.value
                        ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-600'
                        : 'border-slate-200 dark:border-slate-700 text-slate-500 hover:border-slate-300',
                    )}
                  >
                    {opt.icon}
                    <span className="text-sm font-medium">{opt.label}</span>
                    {theme === opt.value && <Check size={14} />}
                  </button>
                ))}
              </div>
            </Card>

            <Card padding="lg">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Язык интерфейса</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">Выберите язык</p>
              <div className="flex gap-3">
                {[{ value: 'ru', label: 'Русский' }, { value: 'en', label: 'English' }].map((lang) => (
                  <button
                    key={lang.value}
                    onClick={() => setLocale(lang.value as 'ru' | 'en')}
                    className={cn(
                      'px-4 py-2 rounded-lg border-2 text-sm font-medium transition-all',
                      locale === lang.value
                        ? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20 text-brand-600'
                        : 'border-slate-200 dark:border-slate-700 text-slate-500',
                    )}
                  >
                    {lang.label}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'notifications' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Уведомления</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Настройте способы получения уведомлений</p>
            <div className="space-y-4">
              {[
                { label: 'Email-уведомления', desc: 'Получать уведомления на почту', value: notifEmail, setter: setNotifEmail },
              ].map((item) => (
                <div key={item.label} className="flex items-center justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </div>
                  <button
                    onClick={() => item.setter(!item.value)}
                    className={cn(
                      'w-11 h-6 rounded-full transition-colors relative',
                      item.value ? 'bg-brand-600' : 'bg-slate-200 dark:bg-slate-700',
                    )}
                  >
                    <span className={cn(
                      'absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                      item.value && 'translate-x-5',
                    )} />
                  </button>
                </div>
              ))}
              <Button onClick={() => { setNotifSaved(true); setTimeout(() => setNotifSaved(false), 2000); }}>
                {notifSaved ? <><Check size={16} /> Сохранено</> : 'Сохранить'}
              </Button>
            </div>
          </Card>
        )}

        {activeTab === 'security' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Безопасность</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">Смените пароль учётной записи</p>

            {passwordMsg && (
              <div className={cn(
                'mb-4 p-3 rounded-lg border text-sm',
                passwordMsg.type === 'success'
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 text-emerald-700'
                  : 'bg-red-50 dark:bg-red-900/20 border-red-200 text-red-700',
              )}>
                {passwordMsg.text}
              </div>
            )}

            <div className="space-y-5 max-w-lg">
              <Input label="Текущий пароль" type="password" value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)} />
              <Input label="Новый пароль" type="password" value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)} />
              <Input label="Подтвердите новый пароль" type="password" value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)} />
              <Button onClick={handleChangePassword} disabled={passwordLoading}>
                {passwordLoading ? (
                  <><Loader2 size={16} className="animate-spin" /> Сохранение...</>
                ) : 'Сменить пароль'}
              </Button>
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
