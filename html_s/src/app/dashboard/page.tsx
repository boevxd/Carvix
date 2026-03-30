'use client';

import React from 'react';
import Link from 'next/link';
import {
  Truck, Wrench, Bell, AlertTriangle, CheckCircle2, Clock,
  ChevronRight, Plus, Gauge, Calendar, Heart, DollarSign,
  Fuel, Shield, MapPin, Camera, MessageSquare,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Badge, Button, MetricCard, StatusDot } from '@/components/ui';
import { HealthScoreBar } from '@/components/ui/progress-bar';
import { vehicles, repairRequests, notifications, maintenanceTasks, vehicleHealthReports } from '@/lib/mock-data';
import { formatDate, getStatusColor, getStatusLabel, getPriorityColor, getPriorityLabel, formatCurrency, formatNumber, daysUntil, getFuelTypeLabel, getRiskLabel, cn } from '@/lib/utils';

export default function DriverDashboard() {
  const myVehicle = vehicles[0];
  const myRequests = repairRequests.filter((r) => r.driverName === 'Алексей Петров');
  const unreadNotifications = notifications.filter((n) => !n.read);
  const upcomingMaintenance = maintenanceTasks.filter((t) => t.vehiclePlate === myVehicle.plate);
  const healthReport = vehicleHealthReports.find((h) => h.vehicleId === myVehicle.id);
  const slaBreachedRequests = myRequests.filter((r) => r.slaBreached);
  const nextToDays = daysUntil(myVehicle.nextMaintenance);

  return (
    <>
      <Header title="Панель водителя" subtitle="Обзор состояния и последние события" />

      <div className="p-4 lg:p-8 space-y-6">
        {/* SLA Alert Banner */}
        {slaBreachedRequests.length > 0 && (
          <div className="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 animate-fade-in">
            <div className="flex items-start gap-3">
              <AlertTriangle size={18} className="text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-red-800 dark:text-red-300">SLA нарушен</p>
                <p className="text-xs text-red-700 dark:text-red-400 mt-1">
                  {slaBreachedRequests.length} заявок с нарушенным SLA: {slaBreachedRequests.map(r => r.id).join(', ')}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Мои заявки"
            value={myRequests.length}
            icon={<Wrench size={20} className="text-brand-600" />}
            iconBg="bg-brand-50 dark:bg-brand-900/20"
          />
          <MetricCard
            title="В работе"
            value={myRequests.filter((r) => r.status === 'in_progress').length}
            icon={<Clock size={20} className="text-amber-600" />}
            iconBg="bg-amber-50 dark:bg-amber-900/20"
          />
          <MetricCard
            title="Уведомления"
            value={unreadNotifications.length}
            icon={<Bell size={20} className="text-red-600" />}
            iconBg="bg-red-50 dark:bg-red-900/20"
          />
          <MetricCard
            title="Здоровье ТС"
            value={`${myVehicle.healthScore}%`}
            icon={<Heart size={20} className="text-emerald-600" />}
            iconBg="bg-emerald-50 dark:bg-emerald-900/20"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Vehicle Info — Enhanced */}
            <Card>
              <div className="flex items-start justify-between mb-4">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Моё транспортное средство</h2>
                <StatusDot status={myVehicle.status} />
              </div>
              <div className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 mb-4">
                <div className="w-14 h-14 rounded-xl bg-brand-600/10 dark:bg-brand-900/20 flex items-center justify-center flex-shrink-0">
                  <Truck size={28} className="text-brand-600 dark:text-brand-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-lg font-bold text-slate-900 dark:text-white">{myVehicle.plate}</p>
                    <Badge variant="success">{getStatusLabel(myVehicle.status)}</Badge>
                    <Badge variant={myVehicle.riskLevel === 'low' ? 'success' : myVehicle.riskLevel === 'medium' ? 'warning' : 'danger'}>
                      {getRiskLabel(myVehicle.riskLevel)}
                    </Badge>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {myVehicle.brand} {myVehicle.model} · {myVehicle.year} г. · {formatNumber(myVehicle.mileage)} км
                  </p>
                </div>
              </div>

              {/* Vehicle details grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                {[
                  { icon: <Gauge size={14} />, label: 'Пробег', value: `${formatNumber(myVehicle.mileage)} км` },
                  { icon: <Fuel size={14} />, label: 'Топливо', value: getFuelTypeLabel(myVehicle.fuelType) },
                  { icon: <Calendar size={14} />, label: 'Следующее ТО', value: formatDate(myVehicle.nextMaintenance), highlight: nextToDays < 0 },
                  { icon: <DollarSign size={14} />, label: 'Расходы', value: formatCurrency(myVehicle.totalServiceCost) },
                ].map((item, i) => (
                  <div key={i} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50">
                    <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                      {item.icon}
                      <span className="text-[10px] uppercase tracking-wider font-medium">{item.label}</span>
                    </div>
                    <p className={cn(
                      'text-sm font-bold text-slate-900 dark:text-white',
                      item.highlight && 'text-red-600 dark:text-red-400'
                    )}>{item.value}</p>
                  </div>
                ))}
              </div>

              {/* Health score bar */}
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-slate-600 dark:text-slate-400">Состояние ТС</span>
                  <span className={cn(
                    'text-lg font-bold',
                    myVehicle.healthScore >= 80 ? 'text-emerald-600' : myVehicle.healthScore >= 60 ? 'text-brand-600' : 'text-amber-600',
                  )}>{myVehicle.healthScore}%</span>
                </div>
                <HealthScoreBar score={myVehicle.healthScore} size="md" showLabel={false} />
              </div>

              {/* Location */}
              {myVehicle.location && (
                <div className="flex items-center gap-2 mt-3 text-xs text-slate-500 dark:text-slate-400">
                  <MapPin size={12} />
                  <span>{myVehicle.location.address}</span>
                </div>
              )}
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <Link href="/dashboard/requests/new">
                <Card className="hover:border-brand-300 dark:hover:border-brand-700 hover:shadow-card-hover transition-all cursor-pointer group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-brand-50 dark:bg-brand-900/20 flex items-center justify-center group-hover:bg-brand-100 dark:group-hover:bg-brand-900/30 transition-colors">
                      <Plus size={20} className="text-brand-600 dark:text-brand-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">Создать заявку</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Сообщить о неисправности</p>
                    </div>
                  </div>
                </Card>
              </Link>
              <Link href="/dashboard/requests">
                <Card className="hover:border-brand-300 dark:hover:border-brand-700 hover:shadow-card-hover transition-all cursor-pointer group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center group-hover:bg-emerald-100 dark:group-hover:bg-emerald-900/30 transition-colors">
                      <CheckCircle2 size={20} className="text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">История заявок</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">Все мои обращения</p>
                    </div>
                  </div>
                </Card>
              </Link>
            </div>

            {/* Recent Requests — Enhanced with SLA */}
            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Последние заявки</h2>
                <Link href="/dashboard/requests" className="text-xs font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 flex items-center gap-1">
                  Все заявки <ChevronRight size={14} />
                </Link>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {myRequests.slice(0, 4).map((req) => (
                  <div key={req.id} className="flex items-center justify-between px-5 py-3.5 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={cn(
                        'w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0',
                        req.slaBreached ? 'bg-red-50 dark:bg-red-900/20' : 'bg-slate-100 dark:bg-slate-800'
                      )}>
                        <Wrench size={16} className={req.slaBreached ? 'text-red-500' : 'text-slate-500 dark:text-slate-400'} />
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{req.id}</p>
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${getStatusColor(req.status)}`}>
                            {getStatusLabel(req.status)}
                          </span>
                          {req.slaBreached && (
                            <span className="inline-flex items-center gap-0.5 text-[10px] font-medium text-red-600 dark:text-red-400">
                              <AlertTriangle size={10} /> SLA
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-0.5">
                          <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{req.category} · {req.vehiclePlate}</p>
                          {req.photos && req.photos.length > 0 && <Camera size={10} className="text-slate-400 flex-shrink-0" />}
                          {req.comments && req.comments.length > 0 && <MessageSquare size={10} className="text-slate-400 flex-shrink-0" />}
                        </div>
                      </div>
                    </div>
                    <div className="text-right flex-shrink-0 ml-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${getPriorityColor(req.priority)}`}>
                        {getPriorityLabel(req.priority)}
                      </span>
                      <p className="text-[11px] text-slate-400 mt-1">{formatDate(req.createdAt)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Right column */}
          <div className="space-y-6">
            {/* Health Factors */}
            {healthReport && (
              <Card>
                <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">Факторы состояния</h2>
                <div className="space-y-3">
                  {healthReport.factors.map((factor, i) => (
                    <div key={i}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-slate-600 dark:text-slate-400">{factor.label}</span>
                        <span className={cn(
                          'text-xs font-bold',
                          factor.status === 'good' ? 'text-emerald-600 dark:text-emerald-400' :
                          factor.status === 'warning' ? 'text-amber-600 dark:text-amber-400' :
                          'text-red-600 dark:text-red-400'
                        )}>{factor.score}%</span>
                      </div>
                      <HealthScoreBar score={factor.score} size="sm" showLabel={false} />
                      <p className="text-[10px] text-slate-400 mt-0.5">{factor.detail}</p>
                    </div>
                  ))}
                </div>
                {healthReport.recommendations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                    <p className="text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Рекомендации</p>
                    {healthReport.recommendations.map((rec, i) => (
                      <div key={i} className="flex items-start gap-1.5 mb-1.5">
                        <ChevronRight size={10} className="text-brand-500 mt-0.5 flex-shrink-0" />
                        <span className="text-[11px] text-slate-600 dark:text-slate-400">{rec}</span>
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            )}

            {/* Notifications */}
            <Card padding="none">
              <div className="flex items-center justify-between px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Уведомления</h2>
                <Link href="/dashboard/notifications" className="text-xs font-medium text-brand-600 hover:text-brand-700 dark:text-brand-400 flex items-center gap-1">
                  Все <ChevronRight size={14} />
                </Link>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {notifications.slice(0, 4).map((notif) => (
                  <div key={notif.id} className="px-5 py-3.5 hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                        notif.type === 'urgent' ? 'bg-red-500' :
                        notif.type === 'maintenance' ? 'bg-amber-500' :
                        notif.type === 'info' ? 'bg-blue-500' : 'bg-slate-400'
                      }`} />
                      <div className="min-w-0">
                        <p className={`text-sm font-medium ${notif.read ? 'text-slate-600 dark:text-slate-400' : 'text-slate-900 dark:text-white'}`}>
                          {notif.title}
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{notif.message}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Upcoming Maintenance */}
            <Card padding="none">
              <div className="px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Плановое ТО</h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {upcomingMaintenance.map((task) => {
                  const taskDays = daysUntil(task.scheduledDate);
                  return (
                    <div key={task.id} className="px-5 py-3.5">
                      <div className="flex items-center justify-between mb-1.5">
                        <p className="text-sm font-semibold text-slate-800 dark:text-slate-200">{task.type}</p>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${getStatusColor(task.status)}`}>
                          {getStatusLabel(task.status)}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                        <Calendar size={12} />
                        <span>{formatDate(task.scheduledDate)}</span>
                        <span className={cn(
                          'text-[10px] font-medium',
                          taskDays < 0 ? 'text-red-600 dark:text-red-400' : taskDays <= 3 ? 'text-amber-600 dark:text-amber-400' : 'text-slate-400'
                        )}>
                          {taskDays < 0 ? `(${Math.abs(taskDays)}д назад)` : taskDays === 0 ? '(сегодня)' : `(через ${taskDays}д)`}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 line-clamp-2">{task.description}</p>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Maintenance Alert */}
            {nextToDays <= 15 && (
              <div className={cn(
                'p-4 rounded-xl border',
                nextToDays < 0
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  : 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800'
              )}>
                <div className="flex items-start gap-3">
                  <AlertTriangle size={18} className={nextToDays < 0 ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'} />
                  <div>
                    <p className={cn('text-sm font-semibold', nextToDays < 0 ? 'text-red-800 dark:text-red-300' : 'text-amber-800 dark:text-amber-300')}>
                      {nextToDays < 0 ? 'ТО просрочено!' : 'Внимание'}
                    </p>
                    <p className={cn('text-xs mt-1', nextToDays < 0 ? 'text-red-700 dark:text-red-400' : 'text-amber-700 dark:text-amber-400')}>
                      {nextToDays < 0
                        ? `ТО просрочено на ${Math.abs(nextToDays)} дней. Свяжитесь с диспетчерской.`
                        : `До планового ТО осталось ${nextToDays} дней. Подготовьте автомобиль к сдаче.`}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
