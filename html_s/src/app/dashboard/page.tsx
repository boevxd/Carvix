'use client';

import React from 'react';
import Link from 'next/link';
import { Truck, Wrench, Bell, CheckCircle2, Clock, ChevronRight, Plus, Loader2, AlertTriangle } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, MetricCard } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { requests as apiRequests, notifications as apiNotifications, vehicles as apiVehicles, analytics } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Новая': 'bg-cyan-100 text-cyan-800 border-cyan-200 dark:bg-cyan-900/30 dark:text-cyan-300 dark:border-cyan-700',
    'В работе': 'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-900/30 dark:text-amber-300 dark:border-amber-700',
    'Выполнена': 'bg-emerald-100 text-emerald-800 border-emerald-200 dark:bg-emerald-900/30 dark:text-emerald-300 dark:border-emerald-700',
    'Закрыта': 'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:text-slate-400',
    'Принята': 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/30 dark:text-purple-300',
  };
  return m[s] || 'bg-slate-100 text-slate-600 border-slate-200';
}

function priorityColor(p: string) {
  const m: Record<string, string> = {
    'Критический': 'bg-red-100 text-red-800 border-red-200',
    'Высокий': 'bg-orange-100 text-orange-800 border-orange-200',
    'Средний': 'bg-blue-100 text-blue-800 border-blue-200',
    'Низкий': 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return m[p] || 'bg-slate-100 text-slate-600 border-slate-200';
}

function formatDate(s: string) {
  if (!s) return '—';
  return new Date(s).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export default function DriverDashboard() {
  const { user } = useAuth();

  const { data: stats, loading: statsLoading } = useApi(() => analytics.dashboard(), []);
  const { data: myRequests, loading: reqLoading } = useApi(
    () => user ? apiRequests.list({ created_by: user.id, limit: 5 }) : Promise.resolve([]),
    [user?.id]
  );
  const { data: myNotifications, loading: notifLoading } = useApi(
    () => apiNotifications.list({ limit: 5 }),
    [user?.id]
  );
  const { data: vehicleList } = useApi(() => apiVehicles.list({ limit: 1 }), []);
  const myVehicle = vehicleList?.[0];

  return (
    <>
      <Header
        title={`Добро пожаловать, ${user?.full_name?.split(' ')[0] || 'Пользователь'}`}
        subtitle="Обзор состояния и последние события"
      />
      <div className="p-4 lg:p-8 space-y-6">
        {statsLoading && (
          <div className="flex items-center gap-2 text-slate-500">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Загрузка данных...</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Мои заявки" value={myRequests?.length ?? '—'}
            icon={<Wrench size={20} className="text-brand-600" />} iconBg="bg-brand-50 dark:bg-brand-900/20" />
          <MetricCard title="В работе" value={myRequests?.filter(r => r.status === 'В работе').length ?? '—'}
            icon={<Clock size={20} className="text-amber-600" />} iconBg="bg-amber-50 dark:bg-amber-900/20" />
          <MetricCard title="Уведомления" value={myNotifications?.filter((n: any) => !n.is_read).length ?? '—'}
            icon={<Bell size={20} className="text-red-600" />} iconBg="bg-red-50 dark:bg-red-900/20" />
          <MetricCard title="Всего ТС" value={stats?.vehicles.total ?? '—'}
            icon={<Truck size={20} className="text-emerald-600" />} iconBg="bg-emerald-50 dark:bg-emerald-900/20" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {myVehicle && (
              <Card>
                <div className="flex items-start justify-between mb-4">
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">Закреплённое ТС</h2>
                  <span className={`text-xs px-2 py-1 rounded-full border font-medium ${statusColor(myVehicle.status)}`}>{myVehicle.status}</span>
                </div>
                <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                  <div className="w-14 h-14 rounded-xl bg-brand-600/10 flex items-center justify-center flex-shrink-0">
                    <Truck size={28} className="text-brand-600" />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-slate-900 dark:text-white">{myVehicle.vehicle_number}</p>
                    <p className="text-sm text-slate-500">{myVehicle.brand} {myVehicle.model} · {myVehicle.year} г. · {myVehicle.mileage?.toLocaleString()} км</p>
                    {myVehicle.department && <p className="text-xs text-slate-400 mt-1">{myVehicle.department}</p>}
                  </div>
                </div>
              </Card>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Link href="/dashboard/requests/new">
                <Card className="hover:border-brand-300 dark:hover:border-brand-700 hover:shadow-md transition-all cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center">
                      <Plus size={20} className="text-brand-600" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">Создать заявку</p>
                      <p className="text-xs text-slate-500">Сообщить о неисправности</p>
                    </div>
                  </div>
                </Card>
              </Link>
              <Link href="/dashboard/requests">
                <Card className="hover:border-brand-300 dark:hover:border-brand-700 hover:shadow-md transition-all cursor-pointer">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
                      <CheckCircle2 size={20} className="text-emerald-600" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">История заявок</p>
                      <p className="text-xs text-slate-500">Все мои обращения</p>
                    </div>
                  </div>
                </Card>
              </Link>
            </div>

            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Последние заявки</h2>
                <Link href="/dashboard/requests" className="text-xs font-medium text-brand-600 flex items-center gap-1">
                  Все заявки <ChevronRight size={14} />
                </Link>
              </div>
              {reqLoading ? (
                <div className="p-8 flex justify-center"><Loader2 size={20} className="animate-spin text-slate-400" /></div>
              ) : !myRequests?.length ? (
                <div className="p-8 text-center text-sm text-slate-400">Заявок пока нет</div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {myRequests.map((req) => (
                    <div key={req.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="w-9 h-9 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
                          <Wrench size={16} className="text-slate-500" />
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-2">
                            <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{req.request_number}</p>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${statusColor(req.status)}`}>{req.status}</span>
                          </div>
                          <p className="text-xs text-slate-500 truncate">{req.description?.slice(0, 50)} · {req.vehicle_number}</p>
                        </div>
                      </div>
                      <div className="text-right flex-shrink-0 ml-4">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${priorityColor(req.priority)}`}>{req.priority}</span>
                        <p className="text-[11px] text-slate-400 mt-1">{formatDate(req.created_at)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            {stats && (
              <Card>
                <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">Статистика парка</h2>
                <div className="space-y-3">
                  {[
                    { label: 'Всего ТС', value: stats.vehicles.total, color: 'text-slate-900 dark:text-white' },
                    { label: 'Активных', value: stats.vehicles.active, color: 'text-emerald-600' },
                    { label: 'На ремонте', value: stats.vehicles.in_repair, color: 'text-red-600' },
                    { label: 'Новых заявок', value: stats.requests.new, color: 'text-cyan-600' },
                    { label: 'В работе', value: stats.requests.in_progress, color: 'text-amber-600' },
                    { label: 'Выполнено', value: stats.requests.completed, color: 'text-emerald-600' },
                  ].map(item => (
                    <div key={item.label} className="flex items-center justify-between">
                      <span className="text-sm text-slate-500 dark:text-slate-400">{item.label}</span>
                      <span className={`text-sm font-bold ${item.color}`}>{item.value}</span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Уведомления</h2>
              </div>
              {notifLoading ? (
                <div className="p-6 flex justify-center"><Loader2 size={16} className="animate-spin text-slate-400" /></div>
              ) : !myNotifications?.length ? (
                <div className="p-6 text-center text-sm text-slate-400">Нет уведомлений</div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {myNotifications.slice(0, 5).map((notif: any) => (
                    <div key={notif.id} className="px-5 py-3.5">
                      <div className="flex items-start gap-3">
                        <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${notif.is_read ? 'bg-slate-300' : 'bg-brand-500'}`} />
                        <div>
                          <p className={`text-sm font-medium ${notif.is_read ? 'text-slate-500' : 'text-slate-900 dark:text-white'}`}>{notif.title}</p>
                          <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{notif.message}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
