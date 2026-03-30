'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Plus, Wrench, Loader2, Search } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button } from '@/components/ui';
import { useAuth } from '@/contexts/auth-context';
import { requests as apiRequests } from '@/lib/api';
import { useApi } from '@/lib/useApi';
import { cn } from '@/lib/utils';

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
function priorityColor(p: string) {
  const m: Record<string, string> = {
    'Критический': 'bg-red-100 text-red-800 border-red-200',
    'Высокий': 'bg-orange-100 text-orange-800 border-orange-200',
    'Средний': 'bg-blue-100 text-blue-800 border-blue-200',
    'Низкий': 'bg-slate-100 text-slate-600 border-slate-200',
  };
  return m[p] || 'bg-slate-100 text-slate-600 border-slate-200';
}
function fmtDate(s: string) { return s ? new Date(s).toLocaleDateString('ru-RU') : '—'; }

const STATUSES = ['Все', 'Новая', 'Принята', 'В работе', 'Выполнена', 'Закрыта'];

export default function RequestHistoryPage() {
  const { user } = useAuth();
  const [statusFilter, setStatusFilter] = useState('Все');
  const [search, setSearch] = useState('');

  const { data: all, loading } = useApi(
    () => apiRequests.list({ limit: 100 }),
    [user?.id]
  );

  const filtered = (all ?? []).filter(r => {
    const matchStatus = statusFilter === 'Все' || r.status === statusFilter;
    const q = search.toLowerCase();
    const matchSearch = !q ||
      r.request_number?.toLowerCase().includes(q) ||
      r.vehicle_number?.toLowerCase().includes(q) ||
      r.description?.toLowerCase().includes(q);
    return matchStatus && matchSearch;
  });

  return (
    <>
      <Header title="Мои заявки" subtitle="История заявок на ремонт" />
      <div className="p-4 lg:p-8 space-y-5">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div className="flex gap-2 flex-wrap">
            {STATUSES.map(s => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-xs font-medium border transition-all',
                  statusFilter === s
                    ? 'bg-brand-600 text-white border-brand-600'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-slate-300',
                )}
              >
                {s} {s !== 'Все' && `(${(all ?? []).filter(r => r.status === s).length})`}
              </button>
            ))}
          </div>
          <Link href="/dashboard/requests/new">
            <Button size="sm"><Plus size={15} /> Новая заявка</Button>
          </Link>
        </div>

        <div className="relative">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Поиск по номеру, ТС, описанию..."
            className="w-full pl-9 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm text-slate-700 dark:text-slate-200 placeholder:text-slate-400 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all"
          />
        </div>

        <Card padding="none">
          {loading && (
            <div className="p-10 flex justify-center">
              <Loader2 size={20} className="animate-spin text-slate-400" />
            </div>
          )}
          {!loading && !filtered.length && (
            <div className="p-12 text-center">
              <Wrench size={32} className="text-slate-300 mx-auto mb-3" />
              <p className="text-sm text-slate-400">Заявок не найдено</p>
            </div>
          )}
          {filtered.length > 0 && (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {filtered.map(req => (
                <div key={req.id} className="flex items-start justify-between px-5 py-4 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                  <div className="flex items-start gap-3 min-w-0 flex-1">
                    <div className="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
                      <Wrench size={18} className="text-slate-500" />
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-bold text-slate-800 dark:text-slate-200">{req.request_number}</span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${statusColor(req.status)}`}>{req.status}</span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${priorityColor(req.priority)}`}>{req.priority}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-1 truncate">{req.vehicle_number} — {req.description?.slice(0, 80)}</p>
                      {req.assigned_to_name && (
                        <p className="text-[11px] text-emerald-600 mt-0.5">Назначен: {req.assigned_to_name}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right ml-4 flex-shrink-0">
                    <p className="text-[11px] text-slate-400">{fmtDate(req.created_at)}</p>
                    {req.estimated_cost && (
                      <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{req.estimated_cost.toLocaleString('ru-RU')} ₽</p>
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
