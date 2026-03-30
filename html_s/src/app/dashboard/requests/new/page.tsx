'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Send, Loader2, CheckCircle2 } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Input, Select } from '@/components/ui';
import { vehicles as apiVehicles, requests as apiRequests, references } from '@/lib/api';
import { useApi } from '@/lib/useApi';
import { useRouter } from 'next/navigation';

export default function NewRequestPage() {
  const router = useRouter();
  const { data: vehicleList } = useApi(() => apiVehicles.list({ limit: 100 }), []);
  const { data: repairTypes } = useApi(() => references.repairTypes(), []);
  const { data: defectCats } = useApi(() => references.defectCategories(), []);

  const [vehicleId, setVehicleId] = useState('');
  const [repairTypeId, setRepairTypeId] = useState('');
  const [defectCatId, setDefectCatId] = useState('');
  const [priority, setPriority] = useState('Средний');
  const [description, setDescription] = useState('');
  const [mileage, setMileage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [created, setCreated] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!vehicleId) { setError('Выберите транспортное средство'); return; }
    if (!description.trim()) { setError('Введите описание проблемы'); return; }
    setSubmitting(true);
    try {
      const req = await apiRequests.create({
        vehicle_id: parseInt(vehicleId),
        description,
        priority,
        repair_type_id: repairTypeId ? parseInt(repairTypeId) : undefined,
        defect_category_id: defectCatId ? parseInt(defectCatId) : undefined,
      });
      setCreated(req);
    } catch (e: any) {
      setError(e.message || 'Ошибка создания заявки');
    }
    setSubmitting(false);
  };

  if (created) {
    return (
      <>
        <Header title="Новая заявка" subtitle="Заявка успешно создана" />
        <div className="p-4 lg:p-8">
          <Card className="max-w-lg mx-auto text-center py-12">
            <div className="w-16 h-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 size={28} className="text-emerald-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Заявка отправлена</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">
              Заявка зарегистрирована под номером
            </p>
            <p className="text-lg font-bold text-brand-600 mb-6">{created.request_number}</p>
            <p className="text-sm text-slate-400 mb-8">Диспетчер рассмотрит её в ближайшее время</p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/dashboard/requests">
                <Button variant="outline">Мои заявки</Button>
              </Link>
              <Button onClick={() => { setCreated(null); setVehicleId(''); setDescription(''); }}>Создать ещё</Button>
            </div>
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <Header title="Новая заявка" subtitle="Заявка на ремонт транспортного средства" />
      <div className="p-4 lg:p-8">
        <div className="max-w-2xl mx-auto">
          <Link href="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-6 transition-colors">
            <ArrowLeft size={16} /> Вернуться к обзору
          </Link>

          <Card>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Заявка на ремонт</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              Заполните форму. Все обязательные поля отмечены.
            </p>

            {error && (
              <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 text-sm text-red-700">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <Select
                label="Транспортное средство *"
                placeholder="Выберите ТС"
                value={vehicleId}
                onChange={(e) => setVehicleId(e.target.value)}
                options={(vehicleList ?? []).map(v => ({
                  value: String(v.id),
                  label: `${v.vehicle_number} — ${v.brand} ${v.model} (${v.status})`,
                }))}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="Тип ремонта"
                  placeholder="Выберите тип"
                  value={repairTypeId}
                  onChange={(e) => setRepairTypeId(e.target.value)}
                  options={(repairTypes ?? []).map(rt => ({ value: String(rt.id), label: rt.name }))}
                />
                <Select
                  label="Категория дефекта"
                  placeholder="Выберите категорию"
                  value={defectCatId}
                  onChange={(e) => setDefectCatId(e.target.value)}
                  options={(defectCats ?? []).map(dc => ({ value: String(dc.id), label: dc.name }))}
                />
              </div>

              <Select
                label="Приоритет"
                placeholder="Выберите приоритет"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                options={[
                  { value: 'Низкий', label: 'Низкий — плановый ремонт' },
                  { value: 'Средний', label: 'Средний — требует внимания' },
                  { value: 'Высокий', label: 'Высокий — срочный ремонт' },
                  { value: 'Критический', label: 'Критический — ТС неисправно' },
                ]}
              />

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1.5">
                  Описание проблемы *
                </label>
                <textarea
                  value={description}
                  onChange={e => setDescription(e.target.value)}
                  placeholder="Опишите неисправность: когда возникает, какие симптомы..."
                  rows={4}
                  className="w-full rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-3 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 transition-all resize-none"
                />
              </div>

              <Input
                label="Текущий пробег (км)"
                type="number"
                placeholder="124500"
                value={mileage}
                onChange={(e) => setMileage(e.target.value)}
              />

              <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <p className="text-sm font-semibold text-blue-800 dark:text-blue-300">После отправки</p>
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  Заявка получит статус «Новая» и будет направлена диспетчеру.
                </p>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Link href="/dashboard">
                  <Button type="button" variant="outline">Отмена</Button>
                </Link>
                <Button type="submit" disabled={submitting}>
                  {submitting ? (
                    <><Loader2 size={16} className="animate-spin" /> Отправка...</>
                  ) : (
                    <><Send size={16} /> Отправить заявку</>
                  )}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </>
  );
}
