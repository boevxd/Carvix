'use client';

import React from 'react';
import { Bell, AlertTriangle, Info, Calendar, CheckCircle2, Clock, Check, Loader2 } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button } from '@/components/ui';
import { notifications as apiNotif } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function getIcon(type: string) {
  switch (type) {
    case 'urgent': return <AlertTriangle size={16} className="text-red-500" />;
    case 'maintenance': return <Calendar size={16} className="text-amber-500" />;
    case 'success': return <CheckCircle2 size={16} className="text-emerald-500" />;
    case 'reminder': return <Clock size={16} className="text-slate-400" />;
    default: return <Info size={16} className="text-blue-500" />;
  }
}

function fmtDt(s: string) {
  return new Date(s).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

export default function NotificationsPage() {
  const { data: notifs, loading, refetch } = useApi(() => apiNotif.list({ limit: 50 }), []);

  const unread = notifs?.filter(n => !n.is_read).length ?? 0;

  const markRead = async (id: number) => {
    await apiNotif.markRead(id);
    refetch();
  };

  const markAll = async () => {
    await apiNotif.markAllRead();
    refetch();
  };

  return (
    <>
      <Header title="Уведомления" subtitle={`${unread} непрочитанных`} />
      <div className="p-4 lg:p-8 space-y-6">
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium px-3 py-1 rounded-full ${unread > 0 ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-600'}`}>
            {unread} новых
          </span>
          {unread > 0 && (
            <Button variant="ghost" size="sm" onClick={markAll}>
              <Check size={15} /> Прочитать все
            </Button>
          )}
        </div>

        <Card padding="none">
          {loading && (
            <div className="p-8 flex justify-center">
              <Loader2 size={20} className="animate-spin text-slate-400" />
            </div>
          )}
          {!loading && !notifs?.length && (
            <div className="p-12 text-center">
              <Bell size={32} className="text-slate-300 mx-auto mb-3" />
              <p className="text-sm text-slate-400">Уведомлений нет</p>
            </div>
          )}
          {notifs && notifs.length > 0 && (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {notifs.map((notif) => (
                <div
                  key={notif.id}
                  className={`flex items-start gap-4 px-5 py-4 cursor-pointer hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors ${!notif.is_read ? 'bg-blue-50/30 dark:bg-blue-900/10' : ''}`}
                  onClick={() => !notif.is_read && markRead(notif.id)}
                >
                  <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
                    {getIcon(notif.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className={`text-sm font-semibold ${notif.is_read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white'}`}>
                          {notif.title}
                        </p>
                        <p className="text-sm text-slate-500 mt-1 leading-relaxed">{notif.message}</p>
                      </div>
                      <div className="flex flex-col items-end flex-shrink-0 gap-2">
                        <span className="text-xs text-slate-400 whitespace-nowrap">{fmtDt(notif.created_at)}</span>
                        {!notif.is_read && <span className="w-2 h-2 rounded-full bg-brand-600" />}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
