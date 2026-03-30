'use client';

import React, { useState } from 'react';
import { Card, Badge, Button } from '@/components/ui';
import { ProgressBar } from '@/components/ui/progress-bar';
import { vehicles, repairRequests, maintenanceTasks, spareParts, costDataMonthly } from '@/lib/mock-data';
import { useLocale } from '@/contexts/locale-context';
import { cn, formatCurrency, formatNumber, formatDate } from '@/lib/utils';
import {
  FileText, Download, BarChart3, Truck, Wrench, Calendar,
  Package, DollarSign, TrendingUp, TrendingDown, Loader2, CheckCircle2,
  PieChart, ArrowRight,
} from 'lucide-react';

interface ReportCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  iconBg: string;
  stats: { label: string; value: string | number }[];
  category: string;
}

export default function ReportsPage() {
  const { t } = useLocale();
  const [generating, setGenerating] = useState<string | null>(null);
  const [ready, setReady] = useState<string[]>([]);

  const handleGenerate = (id: string) => {
    setGenerating(id);
    setTimeout(() => {
      setGenerating(null);
      setReady(prev => prev.includes(id) ? prev : [...prev, id]);
    }, 2000);
  };

  const handleDownload = (id: string) => {
    // Mock download — create CSV content
    const csvContent = generateCSV(id);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `carvix_${id}_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Cost analytics summary
  const totalPlanned = costDataMonthly.reduce((s: number, c) => s + c.planned, 0);
  const totalEmergency = costDataMonthly.reduce((s: number, c) => s + c.emergency, 0);
  const totalParts = costDataMonthly.reduce((s: number, c) => s + c.parts, 0);
  const totalAll = totalPlanned + totalEmergency + totalParts;

  const reports: ReportCard[] = [
    {
      id: 'vehicles',
      title: t('export.vehicles'),
      description: 'Полная информация о транспортных средствах, пробег, состояние, расходы',
      icon: <Truck size={20} />,
      iconBg: 'bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400',
      stats: [
        { label: 'Всего ТС', value: vehicles.length },
        { label: 'Активных', value: vehicles.filter(v => v.status === 'active').length },
        { label: 'Ср. здоровье', value: `${Math.round(vehicles.reduce((s, v) => s + v.healthScore, 0) / vehicles.length)}%` },
      ],
      category: 'fleet',
    },
    {
      id: 'requests',
      title: t('export.requests'),
      description: 'Все ремонтные заявки с приоритетами, SLA, статусами и стоимостью',
      icon: <Wrench size={20} />,
      iconBg: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
      stats: [
        { label: 'Всего заявок', value: repairRequests.length },
        { label: 'Завершено', value: repairRequests.filter(r => r.status === 'completed').length },
        { label: 'SLA нарушен', value: repairRequests.filter(r => r.slaBreached).length },
      ],
      category: 'operations',
    },
    {
      id: 'maintenance',
      title: t('export.maintenance'),
      description: 'Расписание ТО, просроченные и выполненные работы',
      icon: <Calendar size={20} />,
      iconBg: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400',
      stats: [
        { label: 'Всего работ', value: maintenanceTasks.length },
        { label: 'Просрочено', value: maintenanceTasks.filter(m => m.status === 'overdue').length },
        { label: 'Бюджет', value: formatCurrency(maintenanceTasks.reduce((s, m) => s + (m.estimatedCost || 0), 0)) },
      ],
      category: 'operations',
    },
    {
      id: 'costs',
      title: t('export.costs'),
      description: 'Детализация расходов по месяцам: плановые, аварийные, запчасти',
      icon: <DollarSign size={20} />,
      iconBg: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400',
      stats: [
        { label: 'Итого', value: formatCurrency(totalAll) },
        { label: 'Плановые', value: formatCurrency(totalPlanned) },
        { label: 'Аварийные', value: formatCurrency(totalEmergency) },
      ],
      category: 'finance',
    },
    {
      id: 'parts',
      title: 'Отчёт по запчастям',
      description: 'Склад запчастей, расход, стоимость, требующие пополнения',
      icon: <Package size={20} />,
      iconBg: 'bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400',
      stats: [
        { label: 'Позиций', value: spareParts.length },
        { label: 'Мало', value: spareParts.filter(p => p.stockCount <= p.minStock && p.stockCount > 0).length },
        { label: 'Стоимость', value: formatCurrency(spareParts.reduce((s, p) => s + p.stockCount * p.unitCost, 0)) },
      ],
      category: 'finance',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('export.title')}</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{t('export.subtitle')}</p>
      </div>

      {/* Cost summary */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {[
          { label: 'Общие расходы', value: formatCurrency(totalAll), icon: <DollarSign size={16} />, color: 'bg-emerald-50 dark:bg-emerald-900/20', iconColor: 'text-emerald-600 dark:text-emerald-400' },
          { label: t('analytics.cost_planned'), value: formatCurrency(totalPlanned), icon: <TrendingUp size={16} />, color: 'bg-blue-50 dark:bg-blue-900/20', iconColor: 'text-blue-600 dark:text-blue-400', pct: Math.round(totalPlanned / totalAll * 100) },
          { label: t('analytics.cost_emergency'), value: formatCurrency(totalEmergency), icon: <TrendingDown size={16} />, color: 'bg-red-50 dark:bg-red-900/20', iconColor: 'text-red-600 dark:text-red-400', pct: Math.round(totalEmergency / totalAll * 100) },
          { label: t('analytics.cost_parts'), value: formatCurrency(totalParts), icon: <Package size={16} />, color: 'bg-violet-50 dark:bg-violet-900/20', iconColor: 'text-violet-600 dark:text-violet-400', pct: Math.round(totalParts / totalAll * 100) },
        ].map((kpi, i) => (
          <Card key={i} className="!p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className={cn('p-2 rounded-lg', kpi.color)}><span className={kpi.iconColor}>{kpi.icon}</span></div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">{kpi.label}</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{kpi.value}</p>
              </div>
            </div>
            {kpi.pct !== undefined && <ProgressBar value={kpi.pct} size="sm" color={i === 1 ? 'brand' : i === 2 ? 'red' : 'amber'} />}
          </Card>
        ))}
      </div>

      {/* Cost chart (bar chart with CSS) */}
      <Card>
        <h2 className="text-base font-bold text-slate-900 dark:text-white mb-1">{t('analytics.cost_by_month')}</h2>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Структура расходов за последние 6 месяцев</p>
        <div className="flex items-end gap-3 h-48">
          {costDataMonthly.map((month, i) => {
            const max = Math.max(...costDataMonthly.map(c => c.planned + c.emergency + c.parts));
            const total = month.planned + month.emergency + month.parts;
            const h = (total / max) * 100;
            const plannedH = (month.planned / total) * h;
            const emergencyH = (month.emergency / total) * h;
            const partsH = (month.parts / total) * h;
            return (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <span className="text-[10px] font-medium text-slate-600 dark:text-slate-400">{formatCurrency(total)}</span>
                <div className="w-full flex flex-col justify-end" style={{ height: '140px' }}>
                  <div className="w-full rounded-t bg-brand-500" style={{ height: `${plannedH}%` }} />
                  <div className="w-full bg-red-400" style={{ height: `${emergencyH}%` }} />
                  <div className="w-full rounded-b bg-violet-400" style={{ height: `${partsH}%` }} />
                </div>
                <span className="text-[10px] text-slate-500 dark:text-slate-400">{month.month}</span>
              </div>
            );
          })}
        </div>
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          {[
            { color: 'bg-brand-500', label: t('analytics.cost_planned') },
            { color: 'bg-red-400', label: t('analytics.cost_emergency') },
            { color: 'bg-violet-400', label: t('analytics.cost_parts') },
          ].map(l => (
            <div key={l.label} className="flex items-center gap-1.5 text-[10px] text-slate-500 dark:text-slate-400">
              <span className={cn('w-2.5 h-2.5 rounded', l.color)} />
              {l.label}
            </div>
          ))}
        </div>
      </Card>

      {/* Report cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {reports.map(report => {
          const isGenerating = generating === report.id;
          const isReady = ready.includes(report.id);
          return (
            <Card key={report.id} className="!p-5 flex flex-col">
              <div className="flex items-start gap-3 mb-4">
                <div className={cn('p-2.5 rounded-xl', report.iconBg)}>{report.icon}</div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">{report.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">{report.description}</p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                {report.stats.map((stat, i) => (
                  <div key={i} className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-center">
                    <p className="text-xs font-bold text-slate-900 dark:text-white">{stat.value}</p>
                    <p className="text-[10px] text-slate-500 dark:text-slate-400">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="mt-auto flex items-center gap-2">
                {isReady ? (
                  <Button size="sm" variant="primary" onClick={() => handleDownload(report.id)} className="flex-1">
                    <Download size={14} />
                    {t('export.download')} CSV
                  </Button>
                ) : (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleGenerate(report.id)}
                    disabled={isGenerating}
                    className="flex-1"
                  >
                    {isGenerating ? (
                      <><Loader2 size={14} className="animate-spin" /> {t('export.generating')}</>
                    ) : (
                      <><FileText size={14} /> Сформировать</>
                    )}
                  </Button>
                )}
                {isReady && (
                  <Badge variant="success">
                    <CheckCircle2 size={10} className="mr-1" /> {t('export.ready')}
                  </Badge>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}

function generateCSV(reportId: string): string {
  switch (reportId) {
    case 'vehicles':
      return [
        'Номер,Марка,Модель,Год,VIN,Пробег,Статус,Здоровье%,Риск,Расходы',
        ...vehicles.map(v => `${v.plate},${v.brand},${v.model},${v.year},${v.vin},${v.mileage},${v.status},${v.healthScore},${v.riskLevel},${v.totalServiceCost}`)
      ].join('\n');
    case 'requests':
      return [
        'ID,ТС,Категория,Приоритет,Статус,Создана,SLA нарушен,Стоимость',
        ...repairRequests.map(r => `${r.id},${r.vehiclePlate},${r.category},${r.priority},${r.status},${r.createdAt},${r.slaBreached},${r.actualCost || ''}`)
      ].join('\n');
    case 'maintenance':
      return [
        'ID,ТС,Тип,Статус,Дата,Стоимость,Исполнитель',
        ...maintenanceTasks.map(m => `${m.id},${m.vehiclePlate},${m.type},${m.status},${m.scheduledDate},${m.estimatedCost || ''},${m.assignedTo || ''}`)
      ].join('\n');
    case 'costs':
      return [
        'Месяц,Плановые,Аварийные,Запчасти,Итого',
        ...costDataMonthly.map(c => `${c.month},${c.planned},${c.emergency},${c.parts},${c.planned + c.emergency + c.parts}`)
      ].join('\n');
    case 'parts':
      return [
        'Артикул,Название,Категория,Остаток,Мин.запас,Цена,Поставщик',
        ...spareParts.map(p => `${p.partNumber},${p.name},${p.category},${p.stockCount},${p.minStock},${p.unitCost},${p.supplier}`)
      ].join('\n');
    default:
      return '';
  }
}
