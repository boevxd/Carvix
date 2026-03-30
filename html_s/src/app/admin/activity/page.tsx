'use client';
import React from 'react';
import { Activity, Loader2, Wrench, Truck, Package } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card } from '@/components/ui';
import { requests as apiRequests, vehicles as apiVehicles } from '@/lib/api';
import { useApi } from '@/lib/useApi';

function fmtDt(s: string) {
  return new Date(s).toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Новая': 'bg-cyan-100 text-cyan-800',
    'В работе': 'bg-amber-100 text-amber-800',
    'Выполнена': 'bg-emerald-100 text-emerald-800',
    'Закрыта': 'bg-slate-100 text-slate-600',
  };
  return m[s] || 'bg-slate-100 text-slate-600';
}

export default function AdminActivityPage() {
  const { data: requests, loading } = useApi(() => apiRequests.list({ limit: 20 }), []);
  const { data: vehicles } = useApi(() => apiVehicles.list({ limit: 100 }), []);

  const inRepair = (vehicles ?? []).filter(v => v.status === 'На ремонте' || v.status === 'В ремонте');
  const newReqs = (requests ?? []).filter(r => r.status === 'Новая');
  const inProgress = (requests ?? []).filter(r => r.status === 'В работе');

  return (
    <>
      <Header title="Активность" subtitle="Текущее состояние системы" />
      <div className="p-4 lg:p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {[
            { label: 'Новых заявок', value: newReqs.length, color: 'text-cyan-600', bg: 'bg-cyan-50 dark:bg-cyan-900/20', icon: <Wrench size={20} className="text-cyan-600" /> },
            { label: 'В работе', value: inProgress.length, color: 'text-amber-600', bg: 'bg-amber-50 dark:bg-amber-900/20', icon: <Activity size={20} className="text-amber-600" /> },
            { label: 'ТС на ремонте', value: inRepair.length, color: 'text-red-600', bg: 'bg-red-50 dark:bg-red-900/20', icon: <Truck size={20} className="text-red-600" /> },
          ].map(item => (
            <Card key={item.label}>
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${item.bg}`}>{item.icon}</div>
                <div>
                  <p className="text-xs text-slate-500">{item.label}</p>
                  <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        <Card padding="none">
          <div className="px-5 pt-5 pb-3">
            <h2 className="text-base font-bold text-slate-900 dark:text-white">Последние заявки</h2>
          </div>
          {loading ? (
            <div className="p-8 flex justify-center"><Loader2 size={20} className="animate-spin text-slate-400" /></div>
          ) : (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {(requests ?? []).map(req => (
                <div key={req.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{req.request_number}</span>
                      <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium ${statusColor(req.status)}`}>{req.status}</span>
                    </div>
                    <p className="text-xs text-slate-500 truncate mt-0.5">{req.vehicle_number} — {req.description?.slice(0, 60)}</p>
                  </div>
                  <p className="text-[11px] text-slate-400 ml-4 flex-shrink-0">{fmtDt(req.created_at)}</p>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
