'use client';

import React from 'react';
import Link from 'next/link';
import {
  Truck,
  Wrench,
  Bell,
  ClipboardList,
  BarChart3,
  Shield,
  Zap,
  ArrowRight,
  CheckCircle2,
  MessageSquare,
  Users,
  Clock,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* ──────── Navbar ──────── */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-xl border-b border-slate-200/60">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-16 px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <img src="/logo-carvix.png" alt="Carvix" className="w-8 h-8 rounded-lg object-cover" />
            <span className="text-base font-bold text-slate-900 tracking-tight">Carvix</span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <a href="#features" className="hover:text-slate-900 transition-colors">Возможности</a>
            <a href="#how-it-works" className="hover:text-slate-900 transition-colors">Как это работает</a>
            <a href="#dashboard" className="hover:text-slate-900 transition-colors">Платформа</a>
            <a href="#stats" className="hover:text-slate-900 transition-colors">Результаты</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Войти</Button>
            </Link>
            <Link href="/register">
              <Button size="sm">Начать работу</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ──────── Hero ──────── */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-50/60 via-white to-white" />
        <div className="relative max-w-7xl mx-auto px-6">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-50 border border-brand-100 text-brand-700 text-xs font-medium mb-6 animate-fade-in">
              <Zap size={13} />
              Информационная система нового поколения
            </div>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1] mb-6 animate-slide-up">
              Управление ремонтом{' '}
              <span className="gradient-text">автопарка</span>{' '}
              в одной системе
            </h1>
            <p className="text-lg text-slate-600 leading-relaxed max-w-2xl mx-auto mb-10 animate-slide-up animate-delay-100">
              Подача заявок на ремонт, уведомления о плановом ТО, история обращений и оперативное
              взаимодействие с диспетчерской — всё в едином цифровом пространстве.
            </p>
            <div className="flex items-center justify-center gap-4 animate-slide-up animate-delay-200">
              <Link href="/dashboard">
                <Button size="lg">
                  Открыть платформу
                  <ArrowRight size={16} />
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg">Демо-доступ</Button>
              </Link>
            </div>
          </div>

          {/* Dashboard Preview */}
          <div className="mt-16 lg:mt-20 max-w-5xl mx-auto animate-slide-up animate-delay-300">
            <div className="rounded-2xl border border-slate-200 bg-slate-950 shadow-2xl shadow-slate-900/10 overflow-hidden">
              {/* Window Chrome */}
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-900 border-b border-slate-800">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <div className="flex-1 flex justify-center">
                  <div className="px-4 py-1 rounded-md bg-slate-800/80 text-xs text-slate-400">
                    carvix.app/dashboard
                  </div>
                </div>
              </div>
              {/* Mock Dashboard */}
              <div className="p-6 bg-slate-50">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  {[
                    { label: 'Активные ТС', value: '24', color: 'text-emerald-600' },
                    { label: 'Заявки на ремонт', value: '7', color: 'text-amber-600' },
                    { label: 'Завершённые ТО', value: '156', color: 'text-brand-600' },
                    { label: 'Водители', value: '31', color: 'text-slate-700' },
                  ].map((item) => (
                    <div key={item.label} className="bg-white rounded-lg border border-slate-200 p-3.5">
                      <p className="text-[11px] text-slate-500 font-medium">{item.label}</p>
                      <p className={`text-xl font-bold mt-1 ${item.color}`}>{item.value}</p>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="md:col-span-2 bg-white rounded-lg border border-slate-200 p-4 h-36">
                    <p className="text-xs font-semibold text-slate-700 mb-3">Заявки за полугодие</p>
                    <div className="flex items-end justify-between h-20 gap-2 px-2">
                      {[60, 80, 50, 75, 90, 65].map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                          <div className="w-full rounded-t bg-brand-500/80" style={{ height: `${h}%` }} />
                          <span className="text-[9px] text-slate-400">{['Окт', 'Ноя', 'Дек', 'Янв', 'Фев', 'Мар'][i]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="bg-white rounded-lg border border-slate-200 p-4 h-36">
                    <p className="text-xs font-semibold text-slate-700 mb-3">Последние события</p>
                    <div className="space-y-2.5">
                      {[
                        'Заявка REQ-041 обновлена',
                        'ТО запланировано — А 123 МО',
                        'Новый водитель добавлен',
                      ].map((text, i) => (
                        <div key={i} className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-brand-500 flex-shrink-0" />
                          <span className="text-[11px] text-slate-600 truncate">{text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ──────── Features ──────── */}
      <section id="features" className="py-20 lg:py-28 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-2xl mx-auto text-center mb-16">
            <p className="text-sm font-semibold text-brand-600 mb-3 uppercase tracking-wider">Возможности</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Всё для управления автопарком
            </h2>
            <p className="text-base text-slate-500">
              Модульная система, покрывающая полный цикл обслуживания — от подачи заявки водителем до аналитики для руководства.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: <Wrench size={20} />,
                title: 'Подача заявок на ремонт',
                desc: 'Водитель создаёт заявку за минуту: категория неисправности, приоритет, описание и фото повреждения.',
                bg: 'bg-brand-50',
                iconColor: 'text-brand-600',
              },
              {
                icon: <Bell size={20} />,
                title: 'Уведомления о ТО',
                desc: 'Автоматические напоминания о предстоящем техническом обслуживании, просроченных проверках и срочных событиях.',
                bg: 'bg-amber-50',
                iconColor: 'text-amber-600',
              },
              {
                icon: <ClipboardList size={20} />,
                title: 'История обращений',
                desc: 'Полный журнал заявок с фильтрацией по статусу, приоритету, дате и транспортному средству.',
                bg: 'bg-emerald-50',
                iconColor: 'text-emerald-600',
              },
              {
                icon: <MessageSquare size={20} />,
                title: 'Связь с диспетчерской',
                desc: 'Оперативное взаимодействие водителя с диспетчером: обмен сообщениями, обновление статусов в реальном времени.',
                bg: 'bg-violet-50',
                iconColor: 'text-violet-600',
              },
              {
                icon: <BarChart3 size={20} />,
                title: 'Аналитика и отчёты',
                desc: 'Панель руководителя с KPI: количество активных ТС, незакрытые заявки, эффективность обслуживания.',
                bg: 'bg-cyan-50',
                iconColor: 'text-cyan-600',
              },
              {
                icon: <Shield size={20} />,
                title: 'Ролевой доступ',
                desc: 'Три уровня: водитель, диспетчер, администратор. Каждый видит только свой функционал и данные.',
                bg: 'bg-red-50',
                iconColor: 'text-red-600',
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="group relative bg-white rounded-2xl border border-slate-200/60 p-6 hover:shadow-card-hover hover:border-slate-300/60 transition-all duration-300"
              >
                <div className={`w-10 h-10 rounded-xl ${feature.bg} ${feature.iconColor} flex items-center justify-center mb-4`}>
                  {feature.icon}
                </div>
                <h3 className="text-base font-bold text-slate-900 mb-2">{feature.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────── How It Works ──────── */}
      <section id="how-it-works" className="py-20 lg:py-28 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-2xl mx-auto text-center mb-16">
            <p className="text-sm font-semibold text-brand-600 mb-3 uppercase tracking-wider">Процесс</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
              Как работает система
            </h2>
            <p className="text-base text-slate-500">
              От обнаружения проблемы до завершения ремонта — три простых шага.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              {
                step: '01',
                title: 'Водитель создаёт заявку',
                desc: 'Выбирает транспортное средство, описывает неисправность, указывает приоритет и отправляет обращение.',
                icon: <ClipboardList size={24} />,
              },
              {
                step: '02',
                title: 'Диспетчер обрабатывает',
                desc: 'Принимает заявку, назначает механика, контролирует сроки и информирует водителя о ходе ремонта.',
                icon: <Users size={24} />,
              },
              {
                step: '03',
                title: 'Работа завершена',
                desc: 'Механик закрывает заявку, водитель получает уведомление. Данные сохраняются в истории для аналитики.',
                icon: <CheckCircle2 size={24} />,
              },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="w-14 h-14 mx-auto mb-5 rounded-2xl bg-white border border-slate-200 shadow-card flex items-center justify-center text-brand-600">
                  {item.icon}
                </div>
                <span className="text-xs font-bold text-brand-600 uppercase tracking-wider">{item.step}</span>
                <h3 className="text-lg font-bold text-slate-900 mt-2 mb-2">{item.title}</h3>
                <p className="text-sm text-slate-500 leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────── Dashboard Preview Section ──────── */}
      <section id="dashboard" className="py-20 lg:py-28 bg-white">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <p className="text-sm font-semibold text-brand-600 mb-3 uppercase tracking-wider">Платформа</p>
              <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-5">
                Профессиональная панель для каждой роли
              </h2>
              <p className="text-base text-slate-500 leading-relaxed mb-8">
                Водители видят свои заявки и уведомления. Диспетчеры управляют очередью запросов. Администраторы анализируют KPI всего автопарка.
              </p>
              <div className="space-y-4">
                {[
                  'Панель водителя с быстрыми действиями и статусами ТС',
                  'Диспетчерский пульт с очередью заявок и назначением механиков',
                  'Административная аналитика с графиками и метриками',
                  'Адаптивный интерфейс для работы с мобильных устройств',
                ].map((text, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <CheckCircle2 size={18} className="text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-slate-700">{text}</span>
                  </div>
                ))}
              </div>
              <div className="mt-8">
                <Link href="/dashboard">
                  <Button>
                    Перейти к панели
                    <ChevronRight size={16} />
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="rounded-2xl border border-slate-200 bg-white shadow-xl overflow-hidden">
                <div className="bg-slate-900 px-4 py-3 flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                    <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80" />
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80" />
                  </div>
                </div>
                <div className="p-5 space-y-3 bg-slate-50">
                  {[
                    { id: 'REQ-041', cat: 'Двигатель', status: 'В работе', statusColor: 'bg-amber-100 text-amber-700', priority: 'Высокий' },
                    { id: 'REQ-040', cat: 'Тормоза', status: 'Завершена', statusColor: 'bg-emerald-100 text-emerald-700', priority: 'Критич.' },
                    { id: 'REQ-039', cat: 'Электрика', status: 'Новая', statusColor: 'bg-blue-100 text-blue-700', priority: 'Средний' },
                  ].map((req) => (
                    <div key={req.id} className="bg-white rounded-lg border border-slate-200 p-3.5 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                          <Wrench size={14} className="text-slate-500" />
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-slate-800">{req.id}</p>
                          <p className="text-xs text-slate-500">{req.cat}</p>
                        </div>
                      </div>
                      <span className={`text-[11px] font-medium px-2.5 py-1 rounded-full ${req.statusColor}`}>
                        {req.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ──────── Stats ──────── */}
      <section id="stats" className="py-20 lg:py-28 bg-slate-900">
        <div className="max-w-7xl mx-auto px-6">
          <div className="max-w-2xl mx-auto text-center mb-16">
            <p className="text-sm font-semibold text-brand-400 mb-3 uppercase tracking-wider">Результаты</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Цифры, которые говорят сами за себя
            </h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { value: '40%', label: 'Сокращение времени простоя' },
              { value: '2x', label: 'Ускорение обработки заявок' },
              { value: '98%', label: 'Своевременных ТО' },
              { value: '150+', label: 'Обслуживаемых ТС' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-3xl md:text-4xl font-extrabold text-white mb-2">{stat.value}</p>
                <p className="text-sm text-slate-400">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ──────── CTA ──────── */}
      <section className="py-20 lg:py-28 bg-white">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight mb-5">
            Готовы оптимизировать обслуживание автопарка?
          </h2>
          <p className="text-base text-slate-500 mb-8 max-w-xl mx-auto">
            Начните использовать Carvix уже сегодня и переведите управление ремонтом на новый уровень эффективности.
          </p>
          <div className="flex items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg">
                Начать работу
                <ArrowRight size={16} />
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg">Войти в систему</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ──────── Footer ──────── */}
      <footer className="border-t border-slate-200 bg-slate-50">
        <div className="max-w-7xl mx-auto px-6 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="md:col-span-1">
              <div className="flex items-center gap-2.5 mb-4">
                <img src="/logo-carvix.png" alt="Carvix" className="w-8 h-8 rounded-lg object-cover" />
                <span className="text-base font-bold text-slate-900">Carvix</span>
              </div>
              <p className="text-sm text-slate-500 leading-relaxed">
                Информационная система управления ремонтом и обслуживанием корпоративного автопарка.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Платформа</h4>
              <div className="space-y-2">
                {['Панель водителя', 'Диспетчерская', 'Администрирование', 'Аналитика'].map((l) => (
                  <p key={l} className="text-sm text-slate-500 hover:text-slate-700 cursor-pointer transition-colors">{l}</p>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Возможности</h4>
              <div className="space-y-2">
                {['Заявки на ремонт', 'Уведомления о ТО', 'История обращений', 'Связь с диспетчером'].map((l) => (
                  <p key={l} className="text-sm text-slate-500 hover:text-slate-700 cursor-pointer transition-colors">{l}</p>
                ))}
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-900 mb-3">Контакты</h4>
              <div className="space-y-2 text-sm text-slate-500">
                <p>support@carvix.ru</p>
                <p>+7 (495) 123-45-67</p>
                <p>Москва, Россия</p>
              </div>
            </div>
          </div>
          <div className="mt-10 pt-6 border-t border-slate-200 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-xs text-slate-400">© 2026 Carvix. Дипломный проект.</p>
            <div className="flex items-center gap-1 text-xs text-slate-400">
              <Clock size={12} />
              <span>Система управления ремонтом и ТО автопарка предприятия</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
