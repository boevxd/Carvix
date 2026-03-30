'use client';
import React, { useState } from 'react';
import { Truck, Search, Plus, Loader2, Wrench, CheckCircle2, AlertTriangle } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button } from '@/components/ui';
import { vehicles as apiVehicles } from '@/lib/api';
import { useApi } from '@/lib/useApi';
import { cn } from '@/lib/utils';

function statusColor(s: string) {
  const m: Record<string, string> = {
    'Активен': 'bg-emerald-100 text-emerald-800 border-emerald-200',
    'На ремонте': 'bg-red-100 text-red-800 border-red-200',
    'В ремонте': 'bg-red-100 text-red-800 border-red-200',
    'Неактивен': 'bg-slate-100 text-slate-600 border-slate-200',
    'Плановое ТО': 'bg-amber-100 text-amber-800 border-amber-200',
  };
  return m[s] || 'bg-slate-100 text-slate-600 border-slate-200';
}

function statusIcon(s: string) {
  if (s === 'Активен') return <CheckCircle2 size={14} className="text-emerald-600" />;
  if (s === 'На ремонте' || s === 'В ремонте') return <Wrench size={14} className="text-red-600" />;
  return <AlertTriangle size={14} className="text-amber-600" />;
}

const STATUSES = ['Все', 'Активен', 'На ремонте', 'Неактивен'];

export default function AdminVehiclesPage() {
  const [statusFilter, setStatusFilter] = useState('Все');
  const [search, setSearch] = useState('');
  const { data: vehicles, loading } = useApi(() => apiVehicles.list({ limit: 200 }), []);

  const filtered = (vehicles ?? []).filter(v => {
    const matchStatus = statusFilter === 'Все' || v.status === statusFilter;
    const q = search.toLowerCase();
    const matchSearch = !q || v.vehicle_number?.toLowerCase().includes(q) ||
      v.brand?.toLowerCase().includes(q) || v.model?.toLowerCase().includes(q) ||
      v.department?.toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  return (
    <>
      <Header title="Автопарк" subtitle={`${vehicles?.length ?? 0} ТС в системе`} />
      <div className="p-4 lg:p-8 space-y-5">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex gap-2 flex-wrap">
            {STATUSES.map(s => (
              <button key={s} onClick={() => setStatusFilter(s)}
                className={cn('px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
                  statusFilter === s
                    ? 'bg-brand-600 text-white border-brand-600'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300'
                )}>
                {s} {s !== 'Все' && `(${(vehicles ?? []).filter(v => v.status === s).length})`}
              </button>
            ))}
          </div>
        </div>

        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Поиск по номеру, марке, подразделению..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-700 dark:text-slate-200 placeholder:text-slate-400 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {loading && Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="animate-pulse h-40 rounded-2xl bg-slate-100 dark:bg-slate-800" />
          ))}
          {!loading && !filtered.length && (
            <div className="col-span-full py-16 text-center text-sm text-slate-400">
              <Truck size={32} className="mx-auto mb-3 text-slate-300" />
              ТС не найдено
            </div>
          )}
          {filtered.map(v => (
            <Card key={v.id} className="hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-lg bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center">
                  <Truck size={20} className="text-brand-600" />
                </div>
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium border ${statusColor(v.status)}`}>
                  {statusIcon(v.status)} {v.status}
                </span>
              </div>
              <p className="text-base font-bold text-slate-900 dark:text-white">{v.vehicle_number}</p>
              <p className="text-sm text-slate-500 mt-0.5">{v.brand} {v.model} · {v.year}</p>
              <div className="mt-3 pt-3 border-t border-slate-100 dark:border-slate-700 grid grid-cols-2 gap-2 text-xs">
                <div>
                  <p className="text-slate-400">Пробег</p>
                  <p className="font-semibold text-slate-700 dark:text-slate-300">{v.mileage?.toLocaleString()} км</p>
                </div>
                {v.department && (
                  <div>
                    <p className="text-slate-400">Отдел</p>
                    <p className="font-semibold text-slate-700 dark:text-slate-300 truncate">{v.department}</p>
                  </div>
                )}
                {v.next_maintenance && (
                  <div className="col-span-2">
                    <p className="text-slate-400">След. ТО</p>
                    <p className="font-semibold text-amber-600">{new Date(v.next_maintenance).toLocaleDateString('ru-RU')}</p>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
