'use client';

import React from 'react';
import { Truck, Wrench, DollarSign, Clock, CheckCircle2, AlertTriangle, Loader2, Package } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, MetricCard } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { analytics, requests as apiRequests, users as apiUsers } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Новая': 'bg-cyan-100 text-cyan-800 border-cyan-200',
    'В работе': 'bg-amber-100 text-amber-800 border-amber-200',
    'Выполнена': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'Закрыта': 'bg-slate-100 text-slate-600 border-slate-200',
    'Принята': 'bg-purple-100 text-purple-800 border-purple-200',
  };
  return m[s] || 'bg-slate-100 text-slate-600 border-slate-200';
}
function fmtDate(s: string) { return s ? new Date(s).toLocaleDateString('ru-RU') : '—'; }
function fmtCost(n?: number | null) { return n ? `${n.toLocaleString('ru-RU')} ₽` : '—'; }

export default function AdminDashboard() {
  const { user } = useAuth();
  const { data: stats, loading: statsLoading } = useApi(() => analytics.dashboard(), []);
  const { data: recentRequests, loading: reqLoading } = useApi(() => apiRequests.list({ limit: 10 }), []);
  const { data: userList } = useApi(() => apiUsers.list({ limit: 5 }), []);

  return (
    <>
      <Header title="Панель администратора"
        subtitle={`Добро пожаловать, ${user?.full_name?.split(' ')[0] || 'Администратор'}`} />
      <div className="p-4 lg:p-8 space-y-6">
        {statsLoading && (
          <div className="flex items-center gap-2 text-slate-500">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Синхронизация с базой данных...</span>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Всего ТС" value={stats?.vehicles.total ?? '—'}
            icon={<Truck size={20} className="text-brand-600" />} iconBg="bg-brand-50 dark:bg-brand-900/20" />
          <MetricCard title="Активных ТС" value={stats?.vehicles.active ?? '—'}
            icon={<CheckCircle2 size={20} className="text-emerald-600" />} iconBg="bg-emerald-50 dark:bg-emerald-900/20" />
          <MetricCard title="Заявок (всего)" value={stats?.requests.total ?? '—'}
            icon={<Wrench size={20} className="text-amber-600" />} iconBg="bg-amber-50 dark:bg-amber-900/20" />
          <MetricCard title="Затраты на ремонт" value={fmtCost(stats?.total_cost)}
            icon={<DollarSign size={20} className="text-red-600" />} iconBg="bg-red-50 dark:bg-red-900/20" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Новых заявок" value={stats?.requests.new ?? '—'}
            icon={<AlertTriangle size={20} className="text-cyan-600" />} iconBg="bg-cyan-50 dark:bg-cyan-900/20" />
          <MetricCard title="В работе" value={stats?.requests.in_progress ?? '—'}
            icon={<Clock size={20} className="text-amber-600" />} iconBg="bg-amber-50 dark:bg-amber-900/20" />
          <MetricCard title="Запчастей" value={stats?.parts.total ?? '—'}
            icon={<Package size={20} className="text-purple-600" />} iconBg="bg-purple-50 dark:bg-purple-900/20" />
          <MetricCard title="Мало на складе" value={stats?.parts.low_stock ?? '—'}
            icon={<AlertTriangle size={20} className="text-red-600" />} iconBg="bg-red-50 dark:bg-red-900/20" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Последние заявки</h2>
                {reqLoading && <Loader2 size={14} className="animate-spin text-slate-400" />}
              </div>
              {!recentRequests?.length ? (
                <div className="p-8 text-center text-sm text-slate-400">Заявок нет</div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {recentRequests.map((req) => (
                    <div key={req.id} className="flex items-center justify-between px-5 py-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{req.request_number}</span>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${statusColor(req.status)}`}>{req.status}</span>
                        </div>
                        <p className="text-xs text-slate-500 truncate mt-0.5">{req.vehicle_number} · {req.description?.slice(0, 50)}</p>
                        {req.created_by_name && <p className="text-[11px] text-slate-400 mt-0.5">от {req.created_by_name}</p>}
                      </div>
                      <div className="text-right ml-4 flex-shrink-0">
                        <p className="text-xs font-medium text-slate-600 dark:text-slate-400">{req.priority}</p>
                        <p className="text-[11px] text-slate-400">{fmtDate(req.created_at)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Статус автопарка</h2>
              <div className="space-y-2">
                {stats?.charts.vehicles_by_status.map(item => (
                  <div key={item.status} className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">{item.status}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <div className="h-full bg-brand-500 rounded-full"
                          style={{ width: `${stats.vehicles.total > 0 ? (item.count / stats.vehicles.total) * 100 : 0}%` }} />
                      </div>
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300 w-6 text-right">{item.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Заявки по статусам</h2>
              <div className="space-y-2">
                {stats?.charts.requests_by_status.map(item => (
                  <div key={item.status} className="flex items-center justify-between">
                    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusColor(item.status)}`}>{item.status}</span>
                    <span className="text-sm font-bold text-slate-700 dark:text-slate-300">{item.count}</span>
                  </div>
                ))}
              </div>
            </Card>

            {userList && userList.length > 0 && (
              <Card>
                <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Пользователи</h2>
                <div className="space-y-2">
                  {userList.map(u => (
                    <div key={u.id} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{u.full_name}</p>
                        <p className="text-xs text-slate-500">{u.role_name}</p>
                      </div>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full ${u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                        {u.is_active ? 'Активен' : 'Неактивен'}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
