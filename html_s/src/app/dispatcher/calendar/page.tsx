'use client';

import React, { useState, useMemo } from 'react';
import { Card, Badge, Button } from '@/components/ui';
import { Tabs } from '@/components/ui/tabs';
import { Avatar } from '@/components/ui/avatar';
import { maintenanceTasks, vehicles } from '@/lib/mock-data';
import { useLocale } from '@/contexts/locale-context';
import { cn, formatDate, formatCurrency, daysUntil, getStatusLabel } from '@/lib/utils';
import {
  Calendar, ChevronLeft, ChevronRight, Clock, AlertTriangle,
  CheckCircle2, Wrench, Truck, CalendarDays, CalendarClock,
} from 'lucide-react';

const MONTHS_RU = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
const DAYS_RU = ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'];

export default function MaintenanceCalendarPage() {
  const { t } = useLocale();
  const now = new Date();
  const [currentMonth, setCurrentMonth] = useState(now.getMonth());
  const [currentYear, setCurrentYear] = useState(now.getFullYear());
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const prevMonth = () => {
    if (currentMonth === 0) { setCurrentMonth(11); setCurrentYear(y => y - 1); }
    else setCurrentMonth(m => m - 1);
  };
  const nextMonth = () => {
    if (currentMonth === 11) { setCurrentMonth(0); setCurrentYear(y => y + 1); }
    else setCurrentMonth(m => m + 1);
  };

  // Calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    let startDay = firstDay.getDay() - 1;
    if (startDay < 0) startDay = 6;

    const days: { date: number; isCurrentMonth: boolean; dateStr: string }[] = [];

    // Previous month padding
    const prevLastDay = new Date(currentYear, currentMonth, 0).getDate();
    for (let i = startDay - 1; i >= 0; i--) {
      const d = prevLastDay - i;
      const m = currentMonth === 0 ? 11 : currentMonth - 1;
      const y = currentMonth === 0 ? currentYear - 1 : currentYear;
      days.push({ date: d, isCurrentMonth: false, dateStr: `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}` });
    }

    // Current month
    for (let d = 1; d <= lastDay.getDate(); d++) {
      days.push({
        date: d,
        isCurrentMonth: true,
        dateStr: `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
      });
    }

    // Next month padding
    const remaining = 42 - days.length;
    for (let d = 1; d <= remaining; d++) {
      const m = currentMonth === 11 ? 0 : currentMonth + 1;
      const y = currentMonth === 11 ? currentYear + 1 : currentYear;
      days.push({ date: d, isCurrentMonth: false, dateStr: `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}` });
    }

    return days;
  }, [currentMonth, currentYear]);

  const getTasksForDate = (dateStr: string) => {
    return maintenanceTasks.filter(task => task.scheduledDate === dateStr);
  };

  // Stats
  const upcoming = maintenanceTasks.filter(m => m.status === 'scheduled');
  const overdue = maintenanceTasks.filter(m => m.status === 'overdue');
  const inProgress = maintenanceTasks.filter(m => m.status === 'in_progress');
  const completed = maintenanceTasks.filter(m => m.status === 'completed');
  const totalEstimatedCost = maintenanceTasks.reduce((s, m) => s + (m.estimatedCost || 0), 0);

  // Filtered list
  const filteredTasks = useMemo(() => {
    let result = [...maintenanceTasks];
    if (filterStatus !== 'all') result = result.filter(m => m.status === filterStatus);
    return result.sort((a, b) => new Date(a.scheduledDate).getTime() - new Date(b.scheduledDate).getTime());
  }, [filterStatus]);

  const tabs = [
    { id: 'all', label: t('activity.filter.all'), count: maintenanceTasks.length },
    { id: 'scheduled', label: t('calendar.upcoming'), count: upcoming.length },
    { id: 'overdue', label: t('calendar.overdue'), count: overdue.length },
    { id: 'in_progress', label: t('status.in_progress'), count: inProgress.length },
  ];

  const isToday = (dateStr: string) => {
    const today = new Date();
    return dateStr === `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('calendar.title')}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{t('calendar.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant={viewMode === 'calendar' ? 'primary' : 'outline'} size="sm" onClick={() => setViewMode('calendar')}>
            <CalendarDays size={14} /> Календарь
          </Button>
          <Button variant={viewMode === 'list' ? 'primary' : 'outline'} size="sm" onClick={() => setViewMode('list')}>
            <CalendarClock size={14} /> Список
          </Button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
        {[
          { label: t('calendar.upcoming'), value: upcoming.length, icon: <Clock size={16} />, color: 'bg-blue-50 dark:bg-blue-900/20', iconColor: 'text-blue-600 dark:text-blue-400' },
          { label: t('calendar.overdue'), value: overdue.length, icon: <AlertTriangle size={16} />, color: 'bg-red-50 dark:bg-red-900/20', iconColor: 'text-red-600 dark:text-red-400' },
          { label: t('status.in_progress'), value: inProgress.length, icon: <Wrench size={16} />, color: 'bg-amber-50 dark:bg-amber-900/20', iconColor: 'text-amber-600 dark:text-amber-400' },
          { label: t('calendar.completed'), value: completed.length, icon: <CheckCircle2 size={16} />, color: 'bg-emerald-50 dark:bg-emerald-900/20', iconColor: 'text-emerald-600 dark:text-emerald-400' },
          { label: 'Бюджет ТО', value: formatCurrency(totalEstimatedCost), icon: <Calendar size={16} />, color: 'bg-violet-50 dark:bg-violet-900/20', iconColor: 'text-violet-600 dark:text-violet-400' },
        ].map((kpi, i) => (
          <Card key={i} className="!p-4">
            <div className="flex items-center gap-3">
              <div className={cn('p-2 rounded-lg', kpi.color)}>
                <span className={kpi.iconColor}>{kpi.icon}</span>
              </div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">{kpi.label}</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{kpi.value}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {viewMode === 'calendar' ? (
        /* ═══ CALENDAR VIEW ═══ */
        <Card className="!p-0 overflow-hidden">
          {/* Month navigation */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
            <button onClick={prevMonth} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors">
              <ChevronLeft size={18} />
            </button>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              {MONTHS_RU[currentMonth]} {currentYear}
            </h2>
            <button onClick={nextMonth} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors">
              <ChevronRight size={18} />
            </button>
          </div>

          {/* Days header */}
          <div className="grid grid-cols-7 border-b border-slate-100 dark:border-slate-800">
            {DAYS_RU.map(d => (
              <div key={d} className="px-2 py-2.5 text-center text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase">
                {d}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7">
            {calendarDays.map((day, i) => {
              const tasks = getTasksForDate(day.dateStr);
              const today = isToday(day.dateStr);
              return (
                <div
                  key={i}
                  className={cn(
                    'min-h-[90px] p-1.5 border-b border-r border-slate-100 dark:border-slate-800 transition-colors',
                    !day.isCurrentMonth && 'bg-slate-50/50 dark:bg-slate-800/30',
                    today && 'bg-brand-50/50 dark:bg-brand-900/10',
                  )}
                >
                  <span className={cn(
                    'inline-flex items-center justify-center w-6 h-6 text-xs rounded-full mb-1',
                    today ? 'bg-brand-600 text-white font-bold' : 'text-slate-600 dark:text-slate-400',
                    !day.isCurrentMonth && 'text-slate-300 dark:text-slate-600',
                  )}>
                    {day.date}
                  </span>
                  <div className="space-y-0.5">
                    {tasks.map(task => (
                      <div
                        key={task.id}
                        className={cn(
                          'px-1.5 py-0.5 rounded text-[10px] font-medium truncate cursor-default',
                          task.status === 'overdue' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                          task.status === 'in_progress' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400' :
                          task.status === 'completed' ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400' :
                          'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                        )}
                        title={`${task.vehiclePlate} — ${task.type}`}
                      >
                        {task.vehiclePlate}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      ) : (
        /* ═══ LIST VIEW ═══ */
        <div className="space-y-4">
          <Tabs tabs={tabs} activeTab={filterStatus} onChange={setFilterStatus} variant="default" />

          <div className="space-y-3">
            {filteredTasks.map(task => {
              const vehicle = vehicles.find(v => v.id === task.vehicleId);
              const days = daysUntil(task.scheduledDate);
              return (
                <Card key={task.id} className="!p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={cn(
                        'w-10 h-10 rounded-lg flex items-center justify-center',
                        task.status === 'overdue' ? 'bg-red-50 dark:bg-red-900/20' :
                        task.status === 'in_progress' ? 'bg-amber-50 dark:bg-amber-900/20' :
                        task.status === 'completed' ? 'bg-emerald-50 dark:bg-emerald-900/20' :
                        'bg-blue-50 dark:bg-blue-900/20'
                      )}>
                        {task.status === 'overdue' ? <AlertTriangle size={18} className="text-red-600 dark:text-red-400" /> :
                         task.status === 'in_progress' ? <Wrench size={18} className="text-amber-600 dark:text-amber-400" /> :
                         task.status === 'completed' ? <CheckCircle2 size={18} className="text-emerald-600 dark:text-emerald-400" /> :
                         <Clock size={18} className="text-blue-600 dark:text-blue-400" />}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-white">{task.type}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <Truck size={11} className="text-slate-400" />
                          <span className="text-xs text-slate-500 dark:text-slate-400">{task.vehiclePlate}</span>
                          {vehicle && <span className="text-xs text-slate-400">• {vehicle.brand} {vehicle.model}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={task.status === 'overdue' ? 'danger' : task.status === 'in_progress' ? 'warning' : task.status === 'completed' ? 'success' : 'info'}>
                        {getStatusLabel(task.status)}
                      </Badge>
                      <p className={cn(
                        'text-[11px] font-medium mt-1',
                        days < 0 ? 'text-red-600 dark:text-red-400' : days <= 3 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-500 dark:text-slate-400'
                      )}>
                        {days < 0 ? `${Math.abs(days)} ${t('calendar.days_overdue')}` :
                         days === 0 ? 'Сегодня' :
                         `${days} ${t('calendar.days_left')}`}
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-slate-600 dark:text-slate-400 mb-3">{task.description}</p>

                  <div className="flex items-center justify-between pt-3 border-t border-slate-100 dark:border-slate-800">
                    <div className="flex items-center gap-4 text-xs text-slate-500 dark:text-slate-400">
                      <span><Calendar size={11} className="inline mr-1" />{formatDate(task.scheduledDate)}</span>
                      {task.estimatedCost && <span>{formatCurrency(task.estimatedCost)}</span>}
                    </div>
                    {task.assignedTo && (
                      <div className="flex items-center gap-1.5">
                        <Avatar name={task.assignedTo} size="xs" />
                        <span className="text-[11px] text-slate-500 dark:text-slate-400">{task.assignedTo}</span>
                      </div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
