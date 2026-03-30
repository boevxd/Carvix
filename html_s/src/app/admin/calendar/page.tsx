'use client';
import React from 'react';
import { Calendar, Loader2 } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card } from '@/components/ui';
import { maintenance as apiMaintenance } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function fmtDate(s: string) { return s ? new Date(s).toLocaleDateString('ru-RU', { day: '2-digit', month: 'long', year: 'numeric' }) : '—'; }

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Запланировано': 'bg-blue-100 text-blue-800 border-blue-200',
    'Выполнено': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'Отменено': 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return m[s] || 'bg-slate-100 text-slate-600 border-slate-200';
}

export default function AdminCalendarPage() {
  const { data: maintenanceList, loading } = useApi(() => apiMaintenance.list({ limit: 50 }), []);

  return (
    <>
      <Header title="Календарь ТО" subtitle="Плановые техобслуживания" />
      <div className="p-4 lg:p-8 space-y-5">
        <Card padding="none">
          <div className="flex items-center gap-2 px-5 pt-5 pb-3">
            <Calendar size={18} className="text-brand-600" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Расписание ТО</h2>
          </div>
          {loading ? (
            <div className="p-8 flex justify-center"><Loader2 size={20} className="animate-spin text-slate-400" /></div>
          ) : !maintenanceList?.length ? (
            <div className="p-12 text-center text-sm text-slate-400">
              <Calendar size={32} className="mx-auto mb-3 text-slate-300" />
              Плановых ТО нет
            </div>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {maintenanceList.map(m => (
                <div key={m.id} className="flex items-center justify-between px-5 py-4 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center flex-shrink-0">
                      <Calendar size={18} className="text-brand-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{m.request_number}</p>
                        <span className={`text-[11px] px-2 py-0.5 rounded-full border font-medium ${statusColor(m.status)}`}>{m.status}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{m.vehicle_number} · {m.brand} {m.model}</p>
                      {m.maintenance_type_name && <p className="text-[11px] text-slate-400 mt-0.5">{m.maintenance_type_name}</p>}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-slate-600 dark:text-slate-400">{fmtDate(m.scheduled_date)}</p>
                    {m.estimated_cost && (
                      <p className="text-xs text-slate-400 mt-0.5">{m.estimated_cost.toLocaleString('ru-RU')} ₽</p>
                    )}
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
