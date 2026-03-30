'use client';

import React, { useState } from 'react';
import {
  Bell,
  AlertTriangle,
  Info,
  Calendar,
  CheckCircle2,
  Clock,
  Check,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Badge } from '@/components/ui';
import { notifications, maintenanceTasks } from '@/lib/mock-data';
import { formatDateTime, formatDate, getStatusColor, getStatusLabel } from '@/lib/utils';

export default function NotificationsPage() {
  const [notifs, setNotifs] = useState(notifications);

  const markAllRead = () => {
    setNotifs(notifs.map((n) => ({ ...n, read: true })));
  };

  const markRead = (id: string) => {
    setNotifs(notifs.map((n) => (n.id === id ? { ...n, read: true } : n)));
  };

  const unreadCount = notifs.filter((n) => !n.read).length;

  const getNotifIcon = (type: string) => {
    switch (type) {
      case 'urgent':
        return <AlertTriangle size={16} className="text-red-500" />;
      case 'maintenance':
        return <Calendar size={16} className="text-amber-500" />;
      case 'info':
        return <CheckCircle2 size={16} className="text-blue-500" />;
      case 'reminder':
        return <Clock size={16} className="text-slate-400" />;
      default:
        return <Info size={16} className="text-slate-400" />;
    }
  };

  const getNotifBg = (type: string, read: boolean) => {
    if (read) return 'bg-white dark:bg-slate-900';
    switch (type) {
      case 'urgent':
        return 'bg-red-50/50 dark:bg-red-900/10';
      case 'maintenance':
        return 'bg-amber-50/50 dark:bg-amber-900/10';
      default:
        return 'bg-blue-50/30 dark:bg-blue-900/10';
    }
  };

  return (
    <>
      <Header title="Уведомления" subtitle={`${unreadCount} непрочитанных`} />

      <div className="p-4 lg:p-8 space-y-6">
        {/* Actions Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Badge variant={unreadCount > 0 ? 'danger' : 'default'}>
              {unreadCount} новых
            </Badge>
          </div>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" onClick={markAllRead}>
              <Check size={15} />
              Прочитать все
            </Button>
          )}
        </div>

        {/* Notifications List */}
        <Card padding="none">
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {notifs.map((notif) => (
              <div
                key={notif.id}
                className={`flex items-start gap-4 px-5 py-4 transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/50 cursor-pointer ${getNotifBg(notif.type, notif.read)}`}
                onClick={() => markRead(notif.id)}
              >
                <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0 mt-0.5">
                  {getNotifIcon(notif.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className={`text-sm font-semibold ${notif.read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white'}`}>
                        {notif.title}
                      </p>
                      <p className="text-sm text-slate-500 mt-1 leading-relaxed">{notif.message}</p>
                      {notif.vehiclePlate && (
                        <span className="inline-flex items-center gap-1 mt-2 text-xs text-slate-400">
                          <span className="w-1 h-1 rounded-full bg-slate-300" />
                          {notif.vehiclePlate}
                        </span>
                      )}
                    </div>
                    <div className="flex flex-col items-end flex-shrink-0">
                      <span className="text-xs text-slate-400 whitespace-nowrap">
                        {formatDateTime(notif.createdAt)}
                      </span>
                      {!notif.read && (
                        <span className="w-2 h-2 rounded-full bg-brand-600 mt-2" />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Maintenance Schedule */}
        <div>
          <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Расписание ТО</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {maintenanceTasks.map((task) => (
              <Card key={task.id}>
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-brand-600" />
                    <p className="text-sm font-bold text-slate-900 dark:text-white">{task.type}</p>
                  </div>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${getStatusColor(task.status)}`}>
                    {getStatusLabel(task.status)}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mb-2">{task.description}</p>
                <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-700">
                  <span className="text-xs text-slate-400">{task.vehiclePlate}</span>
                  <span className="text-xs font-medium text-slate-600 dark:text-slate-300">{formatDate(task.scheduledDate)}</span>
                </div>
                {task.status === 'overdue' && (
                  <div className="mt-3 p-2.5 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                    <p className="text-xs text-red-700 font-medium">
                      ⚠ ТО просрочено — свяжитесь с диспетчерской
                    </p>
                  </div>
                )}
                {task.status === 'scheduled' && (
                  <div className="mt-3">
                    <Button variant="outline" size="sm" className="w-full">
                      Подтвердить готовность
                    </Button>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
