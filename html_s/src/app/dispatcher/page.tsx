'use client';

import React, { useState } from 'react';
import {
  Wrench,
  Users,
  Truck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  ChevronRight,
  Filter,
  Camera,
  MapPin,
  X,
  Send,
} from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Badge, MetricCard } from '@/components/ui';
import { PhotoUpload, PhotoGallery } from '@/components/ui/photo-upload';
import { repairRequests, drivers, vehicles } from '@/lib/mock-data';
import { formatDate, getStatusColor, getStatusLabel, getPriorityColor, getPriorityLabel, formatCurrency, cn } from '@/lib/utils';

export default function DispatcherPage() {
  const [selectedReq, setSelectedReq] = useState<string | null>(null);
  const [detailReq, setDetailReq] = useState<string | null>(null);
  const [dispatcherPhotos, setDispatcherPhotos] = useState<Record<string, string[]>>({});
  const [dispatcherComments, setDispatcherComments] = useState<Record<string, string[]>>({});
  const [commentText, setCommentText] = useState('');
  const pendingRequests = repairRequests.filter((r) => r.status === 'new' || r.status === 'pending');
  const inProgressRequests = repairRequests.filter((r) => r.status === 'in_progress');
  const detailRequest = detailReq ? repairRequests.find(r => r.id === detailReq) : null;

  return (
    <>
      <Header title="Панель диспетчера" subtitle="Управление заявками и распределение работ" />

      <div className="p-4 lg:p-8 space-y-6">
        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Входящие заявки"
            value={pendingRequests.length}
            icon={<AlertTriangle size={20} className="text-amber-600" />}
            iconBg="bg-amber-50"
          />
          <MetricCard
            title="В работе"
            value={inProgressRequests.length}
            icon={<Clock size={20} className="text-brand-600" />}
            iconBg="bg-brand-50"
          />
          <MetricCard
            title="Водители на линии"
            value={drivers.filter((d) => d.status === 'На линии').length}
            icon={<Users size={20} className="text-emerald-600" />}
            iconBg="bg-emerald-50"
          />
          <MetricCard
            title="ТС в ремонте"
            value={vehicles.filter((v) => v.status === 'repair').length}
            icon={<Truck size={20} className="text-red-600" />}
            iconBg="bg-red-50"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Request Queue */}
          <div className="lg:col-span-2 space-y-6">
            <Card padding="none">
              <div className="px-5 pt-5 pb-3 flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Очередь заявок</h2>
                <div className="flex items-center gap-2">
                  <Badge variant="warning">{pendingRequests.length} ожидают</Badge>
                  <Badge variant="info">{inProgressRequests.length} в работе</Badge>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-y border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
                      <th className="table-header">Номер</th>
                      <th className="table-header">Водитель</th>
                      <th className="table-header">ТС</th>
                      <th className="table-header">Категория</th>
                      <th className="table-header">Приоритет</th>
                      <th className="table-header">Статус</th>
                      <th className="table-header">Действия</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {repairRequests.filter((r) => r.status !== 'completed' && r.status !== 'rejected').map((req) => (
                      <tr key={req.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors">
                        <td className="table-cell font-semibold text-slate-900 dark:text-white text-xs">{req.id}</td>
                        <td className="table-cell text-xs">{req.driverName}</td>
                        <td className="table-cell text-xs font-mono">{req.vehiclePlate}</td>
                        <td className="table-cell text-xs">{req.category}</td>
                        <td className="table-cell">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${getPriorityColor(req.priority)}`}>
                            {getPriorityLabel(req.priority)}
                          </span>
                        </td>
                        <td className="table-cell">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium border ${getStatusColor(req.status)}`}>
                            {getStatusLabel(req.status)}
                          </span>
                        </td>
                        <td className="table-cell">
                          <div className="flex items-center gap-1.5">
                            {req.status === 'new' || req.status === 'pending' ? (
                              <Button size="sm" variant="outline" onClick={() => setSelectedReq(req.id)}>
                                Назначить
                              </Button>
                            ) : (
                              <span className="text-xs text-slate-400">{req.assignedTo?.split(' ').slice(0, 2).join(' ')}</span>
                            )}
                            <button
                              onClick={() => setDetailReq(detailReq === req.id ? null : req.id)}
                              className="p-1.5 rounded-lg text-slate-400 hover:text-brand-600 hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors"
                              title="Подробности"
                            >
                              <ChevronRight size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>

            {/* Assignment Modal */}
            {selectedReq && (
              <Card className="animate-fade-in border-brand-200">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-bold text-slate-900 dark:text-white">Назначение исполнителя — {selectedReq}</h3>
                  <button onClick={() => setSelectedReq(null)} className="text-xs text-slate-400 hover:text-slate-600">
                    Закрыть
                  </button>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {['Механик Иванов А.С.', 'Механик Смирнов В.П.', 'Маляр Кузьмин Д.А.'].map((name) => (
                    <button
                      key={name}
                      onClick={() => setSelectedReq(null)}
                      className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-brand-300 hover:bg-brand-50/30 dark:hover:bg-brand-900/10 transition-all text-left"
                    >
                      <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-300">
                        {name.split(' ').map((w) => w[0]).join('').slice(0, 2)}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-700 dark:text-slate-200">{name}</p>
                        <p className="text-[11px] text-slate-400">Свободен</p>
                      </div>
                    </button>
                  ))}
                </div>
              </Card>
            )}
          </div>

          {/* Right: Drivers + Vehicles */}
          <div className="space-y-6">
            <Card padding="none">
              <div className="px-5 pt-5 pb-3">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">Водители</h2>
              </div>
              <div className="divide-y divide-slate-100 dark:divide-slate-800">
                {drivers.map((driver) => (
                  <div key={driver.id} className="flex items-center justify-between px-5 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-300">
                        {driver.name.split(' ').map((w: string) => w[0]).join('')}
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200">{driver.name}</p>
                        <p className="text-[11px] text-slate-400">{driver.vehiclePlate}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${
                        driver.status === 'На линии' ? 'bg-emerald-50 text-emerald-700' :
                        driver.status === 'На базе' ? 'bg-blue-50 text-blue-700' :
                        'bg-red-50 text-red-700'
                      }`}>
                        {driver.status}
                      </span>
                      <p className="text-[10px] text-slate-400 mt-1">Заявок: {driver.totalRequests}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            <Card>
              <h2 className="text-base font-bold text-slate-900 dark:text-white mb-3">Сводка по парку</h2>
              <div className="space-y-3">
                {[
                  { label: 'Активные ТС', value: vehicles.filter((v) => v.status === 'active').length, total: vehicles.length, color: 'bg-emerald-500' },
                  { label: 'На обслуживании', value: vehicles.filter((v) => v.status === 'maintenance').length, total: vehicles.length, color: 'bg-amber-500' },
                  { label: 'В ремонте', value: vehicles.filter((v) => v.status === 'repair').length, total: vehicles.length, color: 'bg-red-500' },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="flex justify-between text-sm mb-1.5">
                      <span className="text-slate-600 dark:text-slate-400">{item.label}</span>
                      <span className="font-semibold text-slate-800 dark:text-slate-200">{item.value}/{item.total}</span>
                    </div>
                    <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${item.color} transition-all`}
                        style={{ width: `${(item.value / item.total) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Request Detail Panel */}
        {detailRequest && (
          <Card className="animate-fade-in !p-0 overflow-hidden">
            <div className={cn(
              'p-5 border-b border-slate-100 dark:border-slate-800',
              detailRequest.slaBreached ? 'bg-gradient-to-r from-red-50 to-white dark:from-red-900/10 dark:to-slate-900' : ''
            )}>
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white">{detailRequest.id} — {detailRequest.category}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{detailRequest.vehiclePlate} · {detailRequest.driverName} · {formatDate(detailRequest.createdAt)}</p>
                </div>
                <button onClick={() => setDetailReq(null)} className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white transition-colors">
                  <X size={16} />
                </button>
              </div>
              <div className="flex items-center gap-2 flex-wrap mt-3">
                <Badge variant={detailRequest.status === 'completed' ? 'success' : detailRequest.status === 'rejected' ? 'danger' : detailRequest.status === 'in_progress' ? 'warning' : 'info'}>
                  {getStatusLabel(detailRequest.status)}
                </Badge>
                <Badge variant={detailRequest.priority === 'critical' ? 'danger' : detailRequest.priority === 'high' ? 'warning' : 'default'}>
                  {getPriorityLabel(detailRequest.priority)}
                </Badge>
                {detailRequest.slaBreached && (
                  <Badge variant="danger"><AlertTriangle size={10} className="mr-1" /> SLA нарушен</Badge>
                )}
                {detailRequest.actualCost && (
                  <Badge variant="default">Стоимость: {formatCurrency(detailRequest.actualCost)}</Badge>
                )}
              </div>
            </div>

            <div className="p-5 grid grid-cols-1 lg:grid-cols-3 gap-5">
              {/* Description and info */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Описание</h4>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{detailRequest.description}</p>
                </div>
                <div className="space-y-2">
                  {[
                    { label: 'Исполнитель', value: detailRequest.assignedTo || 'Не назначен' },
                    ...(detailRequest.slaDeadline ? [{ label: 'Дедлайн SLA', value: formatDate(detailRequest.slaDeadline) }] : []),
                    ...(detailRequest.estimatedCost ? [{ label: 'Оценка', value: formatCurrency(detailRequest.estimatedCost) }] : []),
                  ].map((row, i) => (
                    <div key={i} className="flex justify-between py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
                      <span className="text-xs text-slate-400">{row.label}</span>
                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">{row.value}</span>
                    </div>
                  ))}
                </div>
                {/* Find vehicle on map */}
                {(() => {
                  const v = vehicles.find(veh => veh.plate === detailRequest.vehiclePlate);
                  return v?.location ? (
                    <a
                      href="/dispatcher/map"
                      className="flex items-center gap-2 p-2.5 rounded-lg bg-brand-50 dark:bg-brand-900/20 border border-brand-200 dark:border-brand-800 text-brand-700 dark:text-brand-300 text-xs font-medium hover:bg-brand-100 dark:hover:bg-brand-900/30 transition-colors"
                    >
                      <MapPin size={14} />
                      Показать {detailRequest.vehiclePlate} на карте
                    </a>
                  ) : null;
                })()}
              </div>

              {/* Photos from driver */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Camera size={12} /> Фото от водителя
                  </h4>
                  {detailRequest.photos && detailRequest.photos.length > 0 ? (
                    <PhotoGallery photos={detailRequest.photos} size="md" />
                  ) : (
                    <p className="text-xs text-slate-400">Фотографии не прикреплены</p>
                  )}
                </div>

                {/* Dispatcher photo upload */}
                <div>
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                    <Camera size={12} /> Фото диспетчера
                  </h4>
                  <PhotoUpload
                    photos={dispatcherPhotos[detailRequest.id] || []}
                    onChange={(newPhotos) => setDispatcherPhotos(prev => ({ ...prev, [detailRequest.id]: newPhotos }))}
                    maxPhotos={4}
                    compact
                    label=""
                  />
                </div>
              </div>

              {/* Comments */}
              <div>
                <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Комментарии</h4>
                <div className="space-y-2 max-h-48 overflow-y-auto mb-3">
                  {detailRequest.comments && detailRequest.comments.length > 0 ? (
                    detailRequest.comments.map((c) => (
                      <div key={c.id} className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-[11px] font-medium text-slate-700 dark:text-slate-300">{c.authorName}</span>
                          <span className="text-[10px] text-slate-400">{new Date(c.createdAt).toLocaleDateString('ru-RU')}</span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-400">{c.text}</p>
                      </div>
                    ))
                  ) : (
                    <p className="text-xs text-slate-400">Нет комментариев</p>
                  )}
                  {(dispatcherComments[detailRequest.id] || []).map((text, i) => (
                    <div key={`dc-${i}`} className="p-2.5 rounded-lg border border-brand-200 dark:border-brand-800 bg-brand-50/50 dark:bg-brand-900/10">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[11px] font-medium text-brand-700 dark:text-brand-300">Диспетчер</span>
                        <span className="text-[10px] text-slate-400">Только что</span>
                      </div>
                      <p className="text-xs text-slate-600 dark:text-slate-400">{text}</p>
                    </div>
                  ))}
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && commentText.trim()) {
                        setDispatcherComments(prev => ({
                          ...prev,
                          [detailRequest.id]: [...(prev[detailRequest.id] || []), commentText.trim()],
                        }));
                        setCommentText('');
                      }
                    }}
                    placeholder="Комментарий диспетчера..."
                    className="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none focus:border-brand-500"
                  />
                  <button
                    onClick={() => {
                      if (commentText.trim()) {
                        setDispatcherComments(prev => ({
                          ...prev,
                          [detailRequest.id]: [...(prev[detailRequest.id] || []), commentText.trim()],
                        }));
                        setCommentText('');
                      }
                    }}
                    className="p-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 transition-colors"
                  >
                    <Send size={12} />
                  </button>
                </div>
              </div>
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
