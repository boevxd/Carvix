'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Upload, X, Camera, ArrowLeft, Send } from 'lucide-react';
import { Header } from '@/components/layout/header';
import { Card, Button, Input, Textarea, Select } from '@/components/ui';
import { PhotoUpload } from '@/components/ui/photo-upload';
import { vehicles } from '@/lib/mock-data';

export default function NewRequestPage() {
  const [photos, setPhotos] = useState<string[]>([]);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  if (submitted) {
    return (
      <>
        <Header title="Новая заявка" subtitle="Заявка на ремонт успешно создана" />
        <div className="p-4 lg:p-8">
          <Card className="max-w-lg mx-auto text-center py-12">
            <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center mx-auto mb-4">
              <Send size={28} className="text-emerald-600" />
            </div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Заявка отправлена</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 max-w-sm mx-auto">
              Ваша заявка на ремонт зарегистрирована под номером <span className="font-semibold text-slate-700 dark:text-slate-300">REQ-2026-0042</span>.
              Диспетчер рассмотрит её в ближайшее время.
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link href="/dashboard/requests">
                <Button variant="outline">Мои заявки</Button>
              </Link>
              <Button onClick={() => setSubmitted(false)}>Создать ещё</Button>
            </div>
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <Header title="Новая заявка" subtitle="Создание заявки на ремонт транспортного средства" />

      <div className="p-4 lg:p-8">
        <div className="max-w-2xl mx-auto">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 mb-6 transition-colors"
          >
            <ArrowLeft size={16} />
            Вернуться к обзору
          </Link>

          <Card>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-1">Заявка на ремонт</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
              Заполните форму для создания заявки на ремонт. Все поля обязательны для заполнения.
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <Select
                label="Транспортное средство"
                placeholder="Выберите ТС"
                defaultValue=""
                options={vehicles
                  .filter((v) => v.assignedDriver)
                  .map((v) => ({
                    value: v.id,
                    label: `${v.plate} — ${v.brand} ${v.model}`,
                  }))}
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <Select
                  label="Категория неисправности"
                  placeholder="Выберите категорию"
                  defaultValue=""
                  options={[
                    { value: 'engine', label: 'Двигатель' },
                    { value: 'brakes', label: 'Тормозная система' },
                    { value: 'electrical', label: 'Электрика' },
                    { value: 'suspension', label: 'Ходовая часть' },
                    { value: 'transmission', label: 'Трансмиссия' },
                    { value: 'body', label: 'Кузов' },
                    { value: 'tires', label: 'Шины и колёса' },
                    { value: 'other', label: 'Другое' },
                  ]}
                />
                <Select
                  label="Приоритет"
                  placeholder="Укажите приоритет"
                  defaultValue=""
                  options={[
                    { value: 'low', label: 'Низкий — плановый ремонт' },
                    { value: 'medium', label: 'Средний — требует внимания' },
                    { value: 'high', label: 'Высокий — срочный ремонт' },
                    { value: 'critical', label: 'Критический — ТС неисправно' },
                  ]}
                />
              </div>

              <Input
                label="Краткое описание проблемы"
                placeholder="Например: стук в передней подвеске при торможении"
              />

              <Textarea
                label="Подробное описание"
                placeholder="Опишите неисправность подробно: когда возникает, при каких условиях, какие симптомы наблюдаете..."
                rows={4}
              />

              <Input
                label="Текущий пробег (км)"
                type="number"
                placeholder="124500"
              />

              {/* Photo Upload */}
              <PhotoUpload
                photos={photos}
                onChange={setPhotos}
                maxPhotos={6}
                maxSizeMB={10}
                label="Фотографии повреждений"
              />

              {/* Status Preview */}
              <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-blue-800">Статус после отправки</p>
                    <p className="text-xs text-blue-600 mt-1">
                      Заявка получит статус «Новая» и будет направлена диспетчеру для рассмотрения и назначения механика.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Link href="/dashboard">
                  <Button type="button" variant="outline">Отмена</Button>
                </Link>
                <Button type="submit">
                  <Send size={16} />
                  Отправить заявку
                </Button>
              </div>
            </form>
          </Card>
        </div>
      </div>
    </>
  );
}
