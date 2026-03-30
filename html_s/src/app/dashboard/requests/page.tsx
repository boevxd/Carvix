'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { Search, Plus, Wrench, Eye, Clock, AlertTriangle, Camera, MessageSquare, DollarSign, ChevronRight, Image as ImageIcon, Send } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Badge } from '@/components/ui';
import { Tabs } from '@/components/ui/tabs';
import { SearchInput } from '@/components/ui/search-input';
import { Avatar } from '@/components/ui/avatar';
import { ProgressBar } from '@/components/ui/progress-bar';
import { PhotoUpload, PhotoGallery } from '@/components/ui/photo-upload';
import { repairRequests } from '@/lib/mock-data';
import { formatDate, getStatusColor, getStatusLabel, getPriorityColor, getPriorityLabel, formatCurrency, isSlaBreached, cn } from '@/lib/utils';

export default function RequestHistoryPage() {
  const [statusFilter, setStatusFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRequest, setSelectedRequest] = useState<string | null>(null);
  const [commentText, setCommentText] = useState('');
  const [uploadedPhotos, setUploadedPhotos] = useState<Record<string, string[]>>({});

  const statusCounts = {
    all: repairRequests.length,
    new: repairRequests.filter((r) => r.status === 'new').length,
    pending: repairRequests.filter((r) => r.status === 'pending').length,
    in_progress: repairRequests.filter((r) => r.status === 'in_progress').length,
    completed: repairRequests.filter((r) => r.status === 'completed').length,
    rejected: repairRequests.filter((r) => r.status === 'rejected').length,
  };

  const tabs = [
    { id: 'all', label: 'Все', count: statusCounts.all },
    { id: 'new', label: 'Новые', count: statusCounts.new },
    { id: 'in_progress', label: 'В работе', count: statusCounts.in_progress },
    { id: 'completed', label: 'Завершённые', count: statusCounts.completed },
    { id: 'rejected', label: 'Отклонённые', count: statusCounts.rejected },
  ];

  const slaBreachedCount = repairRequests.filter(r => r.slaBreached).length;

  const filtered = useMemo(() => {
    return repairRequests.filter((r) => {
      const matchesStatus = statusFilter === 'all' || r.status === statusFilter;
      const matchesSearch =
        searchQuery === '' ||
        r.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.vehiclePlate.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesStatus && matchesSearch;
    });
  }, [statusFilter, searchQuery]);

  const selected = selectedRequest ? repairRequests.find((r) => r.id === selectedRequest) : null;

  return (
    <>
      <Header title="История заявок" subtitle="Все заявки на ремонт и обслуживание" />

      <div className="p-4 lg:p-8 space-y-5">
        {/* KPI row */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <Card className="!p-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-brand-50 dark:bg-brand-900/20"><Wrench size={16} className="text-brand-600 dark:text-brand-400" /></div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">Всего заявок</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{repairRequests.length}</p>
              </div>
            </div>
          </Card>
          <Card className="!p-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-900/20"><Clock size={16} className="text-amber-600 dark:text-amber-400" /></div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">В работе</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{statusCounts.in_progress}</p>
              </div>
            </div>
          </Card>
          <Card className="!p-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-red-50 dark:bg-red-900/20"><AlertTriangle size={16} className="text-red-600 dark:text-red-400" /></div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">SLA нарушен</p>
                <p className="text-lg font-bold text-red-600 dark:text-red-400">{slaBreachedCount}</p>
              </div>
            </div>
          </Card>
          <Card className="!p-3.5">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-900/20"><DollarSign size={16} className="text-emerald-600 dark:text-emerald-400" /></div>
              <div>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">Общая стоимость</p>
                <p className="text-lg font-bold text-slate-900 dark:text-white">{formatCurrency(repairRequests.reduce((s, r) => s + (r.actualCost || 0), 0))}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Tabs tabs={tabs} activeTab={statusFilter} onChange={setStatusFilter} variant="default" />
          <div className="flex items-center gap-3">
            <SearchInput value={searchQuery} onChange={setSearchQuery} placeholder="Поиск по номеру, категории..." className="w-64" />
            <Link href="/dashboard/requests/new">
              <Button size="sm"><Plus size={15} /> Новая заявка</Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          {/* Table */}
          <div className={cn(selected ? 'xl:col-span-2' : 'xl:col-span-3')}>
            <Card padding="none">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
                      <th className="table-header">Номер</th>
                      <th className="table-header">ТС</th>
                      <th className="table-header">Категория</th>
                      <th className="table-header">Приоритет</th>
                      <th className="table-header">Статус</th>
                      <th className="table-header">SLA</th>
                      <th className="table-header">Стоимость</th>
                      <th className="table-header">Дата</th>
                      <th className="table-header w-10"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {filtered.map((req) => (
                      <tr
                        key={req.id}
                        className={cn(
                          'hover:bg-slate-50/50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer',
                          selectedRequest === req.id && 'bg-brand-50/30 dark:bg-brand-900/10',
                        )}
                        onClick={() => setSelectedRequest(selectedRequest === req.id ? null : req.id)}
                      >
                        <td className="table-cell">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-slate-900 dark:text-white">{req.id}</span>
                            {req.photos && req.photos.length > 0 && (
                              <Camera size={12} className="text-slate-400" />
                            )}
                            {req.comments && req.comments.length > 0 && (
                              <MessageSquare size={12} className="text-slate-400" />
                            )}
                          </div>
                        </td>
                        <td className="table-cell text-slate-700 dark:text-slate-300">{req.vehiclePlate}</td>
                        <td className="table-cell">
                          <div className="flex items-center gap-2">
                            <Wrench size={14} className="text-slate-400" />
                            <span className="text-slate-700 dark:text-slate-300">{req.category}</span>
                          </div>
                        </td>
                        <td className="table-cell">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium border ${getPriorityColor(req.priority)}`}>
                            {getPriorityLabel(req.priority)}
                          </span>
                        </td>
                        <td className="table-cell">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium border ${getStatusColor(req.status)}`}>
                            {getStatusLabel(req.status)}
                          </span>
                        </td>
                        <td className="table-cell">
                          {req.slaBreached ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-red-600 dark:text-red-400">
                              <AlertTriangle size={11} /> Нарушен
                            </span>
                          ) : req.slaDeadline ? (
                            <span className="text-[11px] text-emerald-600 dark:text-emerald-400 font-medium">В норме</span>
                          ) : (
                            <span className="text-[11px] text-slate-400">—</span>
                          )}
                        </td>
                        <td className="table-cell text-xs font-medium text-slate-700 dark:text-slate-300">
                          {req.actualCost ? formatCurrency(req.actualCost) : '—'}
                        </td>
                        <td className="table-cell text-slate-500 dark:text-slate-400 text-xs">{formatDate(req.createdAt)}</td>
                        <td className="table-cell">
                          <ChevronRight size={14} className="text-slate-400" />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {filtered.length === 0 && (
                <div className="py-16 text-center">
                  <Wrench size={32} className="mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Заявки не найдены</p>
                  <p className="text-xs text-slate-400 mt-1">Попробуйте изменить параметры фильтрации</p>
                </div>
              )}
            </Card>
          </div>

          {/* Detail Panel */}
          {selected && (
            <div className="xl:col-span-1">
              <Card className="sticky top-4 !p-0 overflow-hidden">
                {/* Header */}
                <div className={cn(
                  'p-5 border-b border-slate-100 dark:border-slate-800',
                  selected.slaBreached ? 'bg-gradient-to-r from-red-50 to-white dark:from-red-900/10 dark:to-slate-900' : 'bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/50 dark:to-slate-900'
                )}>
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-base font-bold text-slate-900 dark:text-white">{selected.id}</h3>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{selected.vehiclePlate} · {selected.category}</p>
                    </div>
                    <Button variant="ghost" size="sm" onClick={() => setSelectedRequest(null)}>✕</Button>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={selected.status === 'completed' ? 'success' : selected.status === 'rejected' ? 'danger' : selected.status === 'in_progress' ? 'warning' : 'info'}>
                      {getStatusLabel(selected.status)}
                    </Badge>
                    <Badge variant={selected.priority === 'critical' ? 'danger' : selected.priority === 'high' ? 'warning' : 'default'}>
                      {getPriorityLabel(selected.priority)}
                    </Badge>
                    {selected.slaBreached && (
                      <Badge variant="danger">
                        <AlertTriangle size={10} className="mr-1" /> SLA нарушен
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="p-5 max-h-[65vh] overflow-y-auto space-y-4">
                  {/* Description */}
                  <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700">
                    <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{selected.description}</p>
                  </div>

                  {/* Info grid */}
                  <div className="space-y-2.5">
                    {[
                      { label: 'Водитель', value: selected.driverName },
                      { label: 'Исполнитель', value: selected.assignedTo || 'Не назначен' },
                      { label: 'Создана', value: formatDate(selected.createdAt) },
                      { label: 'Обновлена', value: formatDate(selected.updatedAt) },
                      ...(selected.slaDeadline ? [{ label: 'Дедлайн SLA', value: formatDate(selected.slaDeadline), highlight: selected.slaBreached }] : []),
                      ...(selected.actualCost ? [{ label: 'Стоимость ремонта', value: formatCurrency(selected.actualCost) }] : []),
                      ...(selected.estimatedCost ? [{ label: 'Оценка стоимости', value: formatCurrency(selected.estimatedCost) }] : []),
                    ].map((row, i) => (
                      <div key={i} className="flex items-center justify-between py-1.5 border-b border-slate-100 dark:border-slate-800 last:border-0">
                        <span className="text-xs text-slate-500 dark:text-slate-400">{row.label}</span>
                        <span className={cn(
                          'text-sm font-medium text-slate-900 dark:text-white',
                          (row as { highlight?: boolean }).highlight && 'text-red-600 dark:text-red-400',
                        )}>{row.value}</span>
                      </div>
                    ))}
                  </div>

                  {/* Photos */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                      <Camera size={12} /> Фотографии
                      {((selected.photos?.length || 0) + (uploadedPhotos[selected.id]?.length || 0)) > 0 && (
                        <span className="text-slate-400 font-normal">
                          ({(selected.photos?.length || 0) + (uploadedPhotos[selected.id]?.length || 0)})
                        </span>
                      )}
                    </h4>
                    {selected.photos && selected.photos.length > 0 && (
                      <PhotoGallery photos={selected.photos} size="md" className="mb-2" />
                    )}
                    {(uploadedPhotos[selected.id]?.length || 0) > 0 && (
                      <PhotoGallery photos={uploadedPhotos[selected.id]} size="md" className="mb-2" />
                    )}
                    <PhotoUpload
                      photos={uploadedPhotos[selected.id] || []}
                      onChange={(newPhotos) => setUploadedPhotos(prev => ({ ...prev, [selected.id]: newPhotos }))}
                      maxPhotos={6}
                      compact
                      label=""
                    />
                  </div>

                  {/* Comments */}
                  {selected.comments && selected.comments.length > 0 && (
                    <div>
                      <h4 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                        <MessageSquare size={12} /> Комментарии ({selected.comments.length})
                      </h4>
                      <div className="space-y-2">
                        {selected.comments.map((comment) => (
                          <div key={comment.id} className="p-2.5 rounded-lg border border-slate-200 dark:border-slate-700">
                            <div className="flex items-center gap-2 mb-1">
                              <Avatar name={comment.authorName} size="xs" />
                              <span className="text-[11px] font-medium text-slate-700 dark:text-slate-300">{comment.authorName}</span>
                              <span className="text-[10px] text-slate-400">{new Date(comment.createdAt).toLocaleDateString('ru-RU')}</span>
                            </div>
                            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">{comment.text}</p>
                          </div>
                        ))}
                      </div>
                      {/* Add comment */}
                      <div className="flex items-center gap-2 mt-2">
                        <input
                          type="text"
                          value={commentText}
                          onChange={(e) => setCommentText(e.target.value)}
                          placeholder="Добавить комментарий..."
                          className="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none focus:border-brand-500"
                        />
                        <button
                          onClick={() => setCommentText('')}
                          className="p-2 rounded-lg bg-brand-600 text-white hover:bg-brand-700 transition-colors"
                        >
                          <Send size={12} />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </Card>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
