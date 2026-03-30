'use client';

import React, { useState, useMemo } from 'react';
import { Card, Badge } from '@/components/ui';
import { Tabs } from '@/components/ui/tabs';
import { SearchInput } from '@/components/ui/search-input';
import { Avatar } from '@/components/ui/avatar';
import { activityLog } from '@/lib/mock-data';
import { useLocale } from '@/contexts/locale-context';
import { cn, formatDate, getActivityActionLabel } from '@/lib/utils';
import {
  Activity, FileText, Truck, Wrench, User, Package, Settings,
  Clock, ChevronRight, Filter,
} from 'lucide-react';

const categoryIcons: Record<string, React.ReactNode> = {
  request: <FileText size={14} />,
  vehicle: <Truck size={14} />,
  maintenance: <Wrench size={14} />,
  user: <User size={14} />,
  part: <Package size={14} />,
  system: <Settings size={14} />,
};

const categoryColors: Record<string, string> = {
  request: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
  vehicle: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400',
  maintenance: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400',
  user: 'bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400',
  part: 'bg-cyan-50 dark:bg-cyan-900/20 text-cyan-600 dark:text-cyan-400',
  system: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400',
};

export default function ActivityLogPage() {
  const { t } = useLocale();
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const categories = [
    { id: 'all', label: t('activity.filter.all'), count: activityLog.length },
    { id: 'request', label: t('activity.filter.requests'), count: activityLog.filter(a => a.targetType === 'request').length },
    { id: 'vehicle', label: t('activity.filter.vehicles'), count: activityLog.filter(a => a.targetType === 'vehicle').length },
    { id: 'maintenance', label: t('activity.filter.maintenance'), count: activityLog.filter(a => a.targetType === 'maintenance').length },
    { id: 'user', label: t('activity.filter.users'), count: activityLog.filter(a => a.targetType === 'user').length },
    { id: 'part', label: t('activity.filter.parts'), count: activityLog.filter(a => a.targetType === 'part').length },
    { id: 'system', label: t('activity.filter.system'), count: activityLog.filter(a => a.targetType === 'system').length },
  ];

  const filtered = useMemo(() => {
    let result = [...activityLog];
    if (categoryFilter !== 'all') result = result.filter(a => a.targetType === categoryFilter);
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(a =>
        a.details.toLowerCase().includes(q) ||
        a.actorName.toLowerCase().includes(q) ||
        getActivityActionLabel(a.action).toLowerCase().includes(q)
      );
    }
    return result.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }, [search, categoryFilter]);

  // Group by date
  const grouped = useMemo(() => {
    const groups: Record<string, typeof filtered> = {};
    filtered.forEach(entry => {
      const date = entry.timestamp.split('T')[0];
      if (!groups[date]) groups[date] = [];
      groups[date].push(entry);
    });
    return Object.entries(groups).sort(([a], [b]) => b.localeCompare(a));
  }, [filtered]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('activity.title')}</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{t('activity.subtitle')}</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <Tabs tabs={categories} activeTab={categoryFilter} onChange={setCategoryFilter} variant="default" />
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder="Поиск по событиям..."
          className="w-full sm:w-72"
        />
      </div>

      {/* Timeline */}
      <div className="space-y-6">
        {grouped.map(([date, entries]) => (
          <div key={date}>
            {/* Date separator */}
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                {formatDate(date)}
              </span>
              <div className="flex-1 h-px bg-slate-200 dark:bg-slate-700" />
              <span className="text-[10px] text-slate-400 dark:text-slate-500">{entries.length} событий</span>
            </div>

            {/* Entries */}
            <div className="space-y-2">
              {entries.map((entry, i) => (
                <Card key={entry.id} className="!p-3.5">
                  <div className="flex items-start gap-3">
                    {/* Category icon */}
                    <div className={cn(
                      'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                      categoryColors[entry.targetType] || categoryColors.system
                    )}>
                      {categoryIcons[entry.targetType] || categoryIcons.system}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-xs font-semibold text-slate-900 dark:text-white">
                          {getActivityActionLabel(entry.action)}
                        </span>
                        <Badge variant={
                          entry.targetType === 'request' ? 'info' :
                          entry.targetType === 'vehicle' ? 'success' :
                          entry.targetType === 'maintenance' ? 'warning' :
                          'default'
                        }>
                          {entry.targetType}
                        </Badge>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-2">{entry.details}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <div className="flex items-center gap-1.5">
                          <Avatar name={entry.actorName} size="xs" />
                          <span className="text-[11px] text-slate-500 dark:text-slate-400">{entry.actorName}</span>
                        </div>
                        <span className="text-[10px] text-slate-400">
                          <Clock size={10} className="inline mr-0.5" />
                          {new Date(entry.timestamp).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {entry.targetId && (
                          <span className="text-[10px] font-mono text-slate-400">{entry.targetId}</span>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <Card className="flex flex-col items-center justify-center py-16">
            <Activity size={40} className="text-slate-300 dark:text-slate-600 mb-3" />
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Нет событий</p>
          </Card>
        )}
      </div>
    </div>
  );
}
