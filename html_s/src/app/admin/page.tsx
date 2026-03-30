'use client';

import React from 'react';
import {
  BarChart3,
  TrendingUp,
  Truck,
  Users,
  Wrench,
  DollarSign,
  Clock,
  CheckCircle2,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, MetricCard, Badge } from '@/components/ui';
import { repairRequests, vehicles, drivers, chartDataRequests, chartDataVehicles, recentEvents } from '@/lib/mock-data';
import { formatDate, getStatusColor, getStatusLabel } from '@/lib/utils';

export default function AdminDashboard() {
  const totalRequests = repairRequests.length;
  const completedRequests = repairRequests.filter((r) => r.status === 'completed').length;
  const avgResolutionDays = 3.2;

  return (
    <>
      <Header title="Аналитика" subtitle="Сводная панель управления автопарком" />

      <div className="p-4 lg:p-8 space-y-6">
        {/* KPI Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Всего ТС"
            value={vehicles.length}
            icon={<Truck size={20} className="text-brand-600" />}
            iconBg="bg-brand-50"
            change={{ value: 12, positive: true }}
          />
          <MetricCard
            title="Активные заявки"
            value={totalRequests - completedRequests}
            icon={<Wrench size={20} className="text-amber-600" />}
            iconBg="bg-amber-50"
            change={{ value: 5, positive: false }}
          />
          <MetricCard
            title="Водители"
            value={drivers.length}
            icon={<Users size={20} className="text-emerald-600" />}
            iconBg="bg-emerald-50"
          />
          <MetricCard
            title="Ср. время ремонта"
            value={`${avgResolutionDays} дн.`}
            icon={<Clock size={20} className="text-purple-600" />}
            iconBg="bg-purple-50"
            change={{ value: 8, positive: true }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Charts area */}
          <div className="lg:col-span-2 space-y-6">
            {/* Requests Chart */}
            <Card>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-base font-bold text-slate-900 dark:text-white">Динамика заявок</h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Количество заявок по месяцам</p>
                </div>
                <div className="flex items-center gap-4 text-xs">
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-brand-600" />
                    <span className="text-slate-500">Заявки</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                    <span className="text-slate-500">Выполнено</span>
                  </div>
                </div>
              </div>
              <div className="h-64 flex items-end gap-3">
                {chartDataRequests.map((item, i) => (
                  <div key={i} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full flex gap-1 items-end" style={{ height: '200px' }}>
                      <div
                        className="flex-1 bg-brand-100 rounded-t-md transition-all hover:bg-brand-200"
                        style={{ height: `${(item.total / 30) * 100}%` }}
                      />
                      <div
                        className="flex-1 bg-emerald-100 rounded-t-md transition-all hover:bg-emerald-200"
                        style={{ height: `${(item.completed / 30) * 100}%` }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-400 font-medium">{item.month}</span>
                  </div>
                ))}
              </div>
            </Card>

            {/* Vehicle Status Distribution */}
            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-1">Состояние автопарка</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-6">Распределение ТС по статусам</p>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {chartDataVehicles.map((item, i) => (
                  <div key={i} className="text-center p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                    <div
                      className={`w-12 h-12 rounded-xl mx-auto mb-3 flex items-center justify-center ${
                        item.status === 'active' ? 'bg-emerald-100' :
                        item.status === 'maintenance' ? 'bg-amber-100' :
                        item.status === 'repair' ? 'bg-red-100' : 'bg-slate-200'
                      }`}
                    >
                      <span className="text-lg font-bold text-slate-700 dark:text-slate-200">{item.count}</span>
                    </div>
                    <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{item.label}</p>
                    <p className="text-xs text-slate-400 mt-0.5">
                      {Math.round((item.count / vehicles.length) * 100)}% парка
                    </p>
                  </div>
                ))}
              </div>
            </Card>

            {/* Performance Table */}
            <Card padding="none">
              <div className="px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Эффективность водителей</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-y border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
                      <th className="table-header">Водитель</th>
                      <th className="table-header">ТС</th>
                      <th className="table-header">Статус</th>
                      <th className="table-header">Заявки</th>
                      <th className="table-header">Рейтинг</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {drivers.map((driver) => (
                      <tr key={driver.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="table-cell">
                          <div className="flex items-center gap-2.5">
                            <div className="w-7 h-7 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-[10px] font-bold text-slate-600 dark:text-slate-300">
                              {driver.name.split(' ').map((w: string) => w[0]).join('')}
                            </div>
                            <span className="text-sm font-medium text-slate-800 dark:text-slate-200">{driver.name}</span>
                          </div>
                        </td>
                        <td className="table-cell text-xs font-mono text-slate-600">{driver.vehiclePlate}</td>
                        <td className="table-cell">
                          <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
                            driver.status === 'На линии' ? 'bg-emerald-50 text-emerald-700' :
                            driver.status === 'На базе' ? 'bg-blue-50 text-blue-700' :
                            'bg-red-50 text-red-700'
                          }`}>
                            {driver.status}
                          </span>
                        </td>
                        <td className="table-cell text-sm font-semibold text-slate-700 dark:text-slate-300">{driver.totalRequests}</td>
                        <td className="table-cell">
                          <div className="flex items-center gap-1.5">
                            <div className="h-1.5 w-16 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-brand-500 rounded-full"
                                style={{ width: `${driver.rating * 20}%` }}
                              />
                            </div>
                            <span className="text-xs text-slate-500">{driver.rating}</span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Right Column */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Показатели KPI</h2>
              <div className="space-y-4">
                {[
                  { label: 'Выполнение SLA', value: '94.2%', trend: '+2.1%', positive: true },
                  { label: 'Среднее время отклика', value: '1.4 ч', trend: '-15 мин', positive: true },
                  { label: 'Расходы на ремонт', value: '₽ 2.4М', trend: '+12%', positive: false },
                  { label: 'Простой ТС', value: '6.8%', trend: '-0.5%', positive: true },
                  { label: 'Профилактика / Аварийн.', value: '3.2:1', trend: '+0.4', positive: true },
                ].map((kpi) => (
                  <div key={kpi.label} className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800 last:border-0">
                    <span className="text-sm text-slate-600 dark:text-slate-400">{kpi.label}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold text-slate-900 dark:text-white">{kpi.value}</span>
                      <span className={`flex items-center text-[11px] font-medium ${kpi.positive ? 'text-emerald-600' : 'text-red-500'}`}>
                        {kpi.positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
                        {kpi.trend}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Recent Events */}
            <Card padding="none">
              <div className="px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Последние события</h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {recentEvents.map((event) => (
                  <div key={event.id} className="px-5 py-3.5">
                    <div className="flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                        event.type === 'success' ? 'bg-emerald-500' :
                        event.type === 'warning' ? 'bg-amber-500' :
                        event.type === 'error' ? 'bg-red-500' : 'bg-blue-500'
                      }`} />
                      <div className="min-w-0">
                        <p className="text-sm text-slate-700 dark:text-slate-300">{event.message}</p>
                        <p className="text-[11px] text-slate-400 mt-0.5">{event.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Budget Summary */}
            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4">Бюджет обслуживания</h2>
              <div className="space-y-3">
                {[
                  { label: 'Плановое ТО', spent: 1250000, budget: 1500000, color: 'bg-brand-500' },
                  { label: 'Аварийный ремонт', spent: 680000, budget: 800000, color: 'bg-amber-500' },
                  { label: 'Запчасти', spent: 430000, budget: 500000, color: 'bg-emerald-500' },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-slate-600 dark:text-slate-400">{item.label}</span>
                      <span className="font-medium text-slate-700 dark:text-slate-300">
                        {(item.spent / 1000000).toFixed(1)}М / {(item.budget / 1000000).toFixed(1)}М ₽
                      </span>
                    </div>
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${item.color} transition-all`}
                        style={{ width: `${(item.spent / item.budget) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
