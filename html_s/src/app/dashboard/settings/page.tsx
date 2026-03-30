'use client';

import React, { useState, useEffect } from 'react';
import { User, Palette, Bell, Shield, Check, Sun, Moon, Monitor, Globe } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Button, Input, Card } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { useTheme } from '@/contexts/theme-context';
import { useLocale } from '@/contexts/locale-context';
import { cn } from '@/lib/utils';

type Tab = 'profile' | 'appearance' | 'notifications' | 'security';

export default function SettingsPage() {
  const { user, updateProfile, updateNotifPrefs, changePassword } = useAuth();
  const { theme, setTheme } = useTheme();
  const { t, locale, setLocale } = useLocale();
  const [activeTab, setActiveTab] = useState<Tab>('profile');

  // Profile state
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [profileSaved, setProfileSaved] = useState(false);

  // Security state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Notification prefs state
  const [notifEmail, setNotifEmail] = useState(true);
  const [notifPush, setNotifPush] = useState(true);
  const [notifSms, setNotifSms] = useState(false);
  const [notifSaved, setNotifSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setFirstName(user.firstName);
      setLastName(user.lastName);
      setEmail(user.email);
      setPhone(user.phone);
      setNotifEmail(user.notificationPrefs.email);
      setNotifPush(user.notificationPrefs.push);
      setNotifSms(user.notificationPrefs.sms);
    }
  }, [user]);

  const handleSaveProfile = () => {
    updateProfile({ firstName, lastName, email, phone });
    setProfileSaved(true);
    setTimeout(() => setProfileSaved(false), 2000);
  };

  const handleSaveNotifs = () => {
    updateNotifPrefs({ email: notifEmail, push: notifPush, sms: notifSms });
    setNotifSaved(true);
    setTimeout(() => setNotifSaved(false), 2000);
  };

  const handleChangePassword = () => {
    setPasswordMsg(null);
    if (newPassword !== confirmNewPassword) {
      setPasswordMsg({ type: 'error', text: t('settings.password.mismatch') });
      return;
    }
    const result = changePassword(currentPassword, newPassword);
    if (result.success) {
      setPasswordMsg({ type: 'success', text: t('settings.password.changed') });
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } else {
      setPasswordMsg({ type: 'error', text: t(result.error || 'common.error') });
    }
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'profile', label: t('settings.profile'), icon: <User size={18} /> },
    { id: 'appearance', label: t('settings.appearance'), icon: <Palette size={18} /> },
    { id: 'notifications', label: t('settings.notifications'), icon: <Bell size={18} /> },
    { id: 'security', label: t('settings.security'), icon: <Shield size={18} /> },
  ];

  const themeOptions: { value: 'light' | 'dark' | 'system'; label: string; icon: React.ReactNode }[] = [
    { value: 'light', label: t('settings.theme.light'), icon: <Sun size={20} /> },
    { value: 'dark', label: t('settings.theme.dark'), icon: <Moon size={20} /> },
    { value: 'system', label: t('settings.theme.system'), icon: <Monitor size={20} /> },
  ];

  const languageOptions: { value: 'ru' | 'en'; label: string }[] = [
    { value: 'ru', label: t('settings.language.ru') },
    { value: 'en', label: t('settings.language.en') },
  ];

  if (!user) return null;

  return (
    <>
      <Header title={t('settings.title')} subtitle={t('settings.subtitle')} />
      <div className="p-4 lg:p-8 max-w-4xl">
        {/* Tabs */}
        <div className="flex gap-1 mb-8 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl w-fit">
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

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{t('settings.profile')}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t('settings.profile.desc')}</p>

            <div className="flex items-center gap-4 mb-8">
              <div className="w-16 h-16 rounded-full bg-brand-600 flex items-center justify-center text-xl font-bold text-white flex-shrink-0">
                {firstName.charAt(0)}{lastName.charAt(0)}
              </div>
              <div>
                <p className="text-base font-semibold text-slate-900 dark:text-white">{firstName} {lastName}</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">{email}</p>
              </div>
            </div>

            <div className="space-y-5 max-w-lg">
              <div className="grid grid-cols-2 gap-4">
                <Input label={t('auth.firstName')} value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                <Input label={t('auth.lastName')} value={lastName} onChange={(e) => setLastName(e.target.value)} />
              </div>
              <Input label={t('auth.email')} type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              <Input label={t('auth.phone')} type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} />

              <div className="flex items-center gap-3 pt-2">
                <Button onClick={handleSaveProfile}>
                  {profileSaved ? <><Check size={16} /> {t('settings.saved')}</> : t('settings.save')}
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Appearance Tab */}
        {activeTab === 'appearance' && (
          <div className="space-y-6">
            <Card padding="lg">
              <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{t('settings.theme')}</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t('settings.appearance.desc')}</p>

              <div className="grid grid-cols-3 gap-4 max-w-lg">
                {themeOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setTheme(opt.value)}
                    className={cn(
                      'flex flex-col items-center gap-3 p-4 rounded-xl border-2 transition-all',
                      theme === opt.value
                        ? 'border-brand-600 bg-brand-50 dark:bg-brand-900/20'
                        : 'border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600',
                    )}
                  >
                    <div className={cn(
                      'p-3 rounded-lg',
                      theme === opt.value
                        ? 'bg-brand-600 text-white'
                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400',
                    )}>
                      {opt.icon}
                    </div>
                    <span className={cn(
                      'text-sm font-medium',
                      theme === opt.value ? 'text-brand-700 dark:text-brand-400' : 'text-slate-600 dark:text-slate-300',
                    )}>
                      {opt.label}
                    </span>
                  </button>
                ))}
              </div>
            </Card>

            <Card padding="lg">
              <div className="flex items-center gap-3 mb-4">
                <Globe size={20} className="text-slate-500 dark:text-slate-400" />
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">{t('settings.language')}</h2>
              </div>

              <div className="flex gap-3 max-w-lg">
                {languageOptions.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setLocale(opt.value)}
                    className={cn(
                      'flex-1 py-3 px-4 rounded-xl border-2 text-sm font-medium transition-all',
                      locale === opt.value
                        ? 'border-brand-600 bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-400'
                        : 'border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600',
                    )}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{t('settings.notifications')}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t('settings.notifications.desc')}</p>

            <div className="space-y-4 max-w-lg">
              {[
                { key: 'email' as const, label: t('settings.notif.email'), desc: t('settings.notif.email.desc'), value: notifEmail, setter: setNotifEmail },
                { key: 'push' as const, label: t('settings.notif.push'), desc: t('settings.notif.push.desc'), value: notifPush, setter: setNotifPush },
                { key: 'sms' as const, label: t('settings.notif.sms'), desc: t('settings.notif.sms.desc'), value: notifSms, setter: setNotifSms },
              ].map((item) => (
                <div key={item.key} className="flex items-center justify-between p-4 rounded-xl border border-slate-200 dark:border-slate-700">
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">{item.label}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{item.desc}</p>
                  </div>
                  <button
                    onClick={() => item.setter(!item.value)}
                    className={cn(
                      'relative w-11 h-6 rounded-full transition-colors flex-shrink-0',
                      item.value ? 'bg-brand-600' : 'bg-slate-300 dark:bg-slate-600',
                    )}
                  >
                    <span className={cn(
                      'absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform',
                      item.value ? 'translate-x-[22px]' : 'translate-x-0.5',
                    )} />
                  </button>
                </div>
              ))}

              <div className="pt-2">
                <Button onClick={handleSaveNotifs}>
                  {notifSaved ? <><Check size={16} /> {t('settings.saved')}</> : t('settings.save')}
                </Button>
              </div>
            </div>
          </Card>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <Card padding="lg">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">{t('settings.security')}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">{t('settings.security.desc')}</p>

            <div className="space-y-5 max-w-lg">
              <Input
                label={t('settings.password.current')}
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
              <Input
                label={t('settings.password.new')}
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <Input
                label={t('settings.password.confirm')}
                type="password"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
              />

              {passwordMsg && (
                <div className={cn(
                  'p-3 rounded-lg text-sm flex items-center gap-2',
                  passwordMsg.type === 'success'
                    ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800'
                    : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800',
                )}>
                  {passwordMsg.type === 'success' ? <Check size={16} /> : <Shield size={16} />}
                  {passwordMsg.text}
                </div>
              )}

              <Button onClick={handleChangePassword}>{t('settings.password.change')}</Button>
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
