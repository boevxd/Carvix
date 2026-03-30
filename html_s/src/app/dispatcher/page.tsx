'use client';

import React from 'react';
import { Truck, Wrench, Clock, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, MetricCard } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { analytics, requests as apiRequests, vehicles as apiVehicles, maintenance as apiMaintenance } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Новая': 'bg-cyan-100 text-cyan-800 border-cyan-200',
    'В работе': 'bg-amber-100 text-amber-800 border-amber-200',
    'Выполнена': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'Закрыта': 'bg-slate-100 text-slate-600 border-slate-200',
    'Принята': 'bg-purple-100 text-purple-800 border-purple-200',
    'Запланировано': 'bg-blue-100 text-blue-800 border-blue-200',
  };
  return m[s] || 'bg-slate-100 text-slate-600 border-slate-200';
}
function fmtDate(s: string) { return s ? new Date(s).toLocaleDateString('ru-RU') : '—'; }

export default function DispatcherDashboard() {
  const { user } = useAuth();
  const { data: stats } = useApi(() => analytics.dashboard(), []);
  const { data: allRequests, loading: reqLoading } = useApi(() => apiRequests.list({ limit: 10 }), []);
  const { data: vehicleList, loading: vehLoading } = useApi(() => apiVehicles.list({ limit: 8 }), []);
  const { data: maintenanceList, loading: maintLoading } = useApi(
    () => apiMaintenance.list({ status: 'Запланировано', limit: 5 }), []
  );

  const newRequests = allRequests?.filter(r => r.status === 'Новая') ?? [];

  return (
    <>
      <Header title="Диспетчерская" subtitle={`Управление заявками — ${user?.full_name || ''}`} />
      <div className="p-4 lg:p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard title="Новых заявок" value={newRequests.length}
            icon={<AlertTriangle size={20} className="text-cyan-600" />} iconBg="bg-cyan-50 dark:bg-cyan-900/20" />
          <MetricCard title="В работе" value={stats?.requests.in_progress ?? '—'}
            icon={<Clock size={20} className="text-amber-600" />} iconBg="bg-amber-50 dark:bg-amber-900/20" />
          <MetricCard title="Всего ТС" value={stats?.vehicles.total ?? '—'}
            icon={<Truck size={20} className="text-brand-600" />} iconBg="bg-brand-50 dark:bg-brand-900/20" />
          <MetricCard title="Плановое ТО" value={stats?.maintenance.planned ?? '—'}
            icon={<CheckCircle2 size={20} className="text-emerald-600" />} iconBg="bg-emerald-50 dark:bg-emerald-900/20" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {newRequests.length > 0 && (
              <div className="p-4 rounded-xl bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-200 dark:border-cyan-800">
                <div className="flex items-center gap-2 mb-1">
                  <AlertTriangle size={16} className="text-cyan-600" />
                  <p className="text-sm font-semibold text-cyan-800 dark:text-cyan-300">
                    {newRequests.length} новых заявок требуют обработки
                  </p>
                </div>
                <p className="text-xs text-cyan-700 dark:text-cyan-400">Назначьте механиков и измените статус заявок</p>
              </div>
            )}

            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Все заявки</h2>
                {reqLoading && <Loader2 size={14} className="animate-spin text-slate-400" />}
              </div>
              {!allRequests?.length ? (
                <div className="p-8 text-center text-sm text-slate-400">Заявок нет</div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {allRequests.map((req) => (
                    <div key={req.id} className="flex items-start justify-between px-5 py-3.5 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{req.request_number}</span>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${statusColor(req.status)}`}>{req.status}</span>
                          <span className="text-[11px] text-slate-400">{req.priority}</span>
                        </div>
                        <p className="text-xs text-slate-500 mt-0.5 truncate">{req.vehicle_number} — {req.description?.slice(0, 60)}</p>
                        <div className="flex items-center gap-3 mt-0.5">
                          {req.created_by_name && <span className="text-[11px] text-slate-400">от {req.created_by_name}</span>}
                          {req.assigned_to_name && <span className="text-[11px] text-emerald-600">→ {req.assigned_to_name}</span>}
                        </div>
                      </div>
                      <p className="text-[11px] text-slate-400 ml-4 flex-shrink-0">{fmtDate(req.created_at)}</p>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            <Card padding="none">
              <div className="px-5 pt-5 pb-3 flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Плановое ТО</h2>
                {maintLoading && <Loader2 size={14} className="animate-spin text-slate-400" />}
              </div>
              {!maintenanceList?.length ? (
                <div className="p-6 text-center text-sm text-slate-400">Плановых ТО нет</div>
              ) : (
                <div className="divide-y divide-slate-100 dark:divide-slate-800">
                  {maintenanceList.map((m) => (
                    <div key={m.id} className="px-5 py-3.5 flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{m.request_number}</p>
                        <p className="text-xs text-slate-500">{m.vehicle_number} · {m.maintenance_type_name || 'ТО'}</p>
                      </div>
                      <div className="text-right">
                        <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${statusColor(m.status)}`}>{m.status}</span>
                        <p className="text-[11px] text-slate-400 mt-1">{fmtDate(m.scheduled_date)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          <div className="space-y-6">
            <Card padding="none">
              <div className="px-5 pt-5 pb-3 flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Автопарк</h2>
                {vehLoading && <Loader2 size={14} className="animate-spin text-slate-400" />}
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {vehicleList?.map(v => (
                  <div key={v.id} className="px-5 py-3 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{v.vehicle_number}</p>
                        <p className="text-xs text-slate-500">{v.brand} {v.model}</p>
                      </div>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${statusColor(v.status)}`}>{v.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {stats && (
              <Card>
                <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Сводка</h2>
                <div className="space-y-2">
                  {[
                    { label: 'Активных ТС', val: stats.vehicles.active, color: 'text-emerald-600' },
                    { label: 'На ремонте', val: stats.vehicles.in_repair, color: 'text-red-600' },
                    { label: 'Выполнено заявок', val: stats.requests.completed, color: 'text-emerald-600' },
                    { label: 'Запчасти (мало)', val: stats.parts.low_stock,
                      color: stats.parts.low_stock > 0 ? 'text-red-600' : 'text-slate-600' },
                  ].map(item => (
                    <div key={item.label} className="flex items-center justify-between">
                      <span className="text-sm text-slate-500">{item.label}</span>
                      <span className={`text-sm font-bold ${item.color}`}>{item.val}</span>
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
