'use client';

import React, { useState, useMemo } from 'react';
import { Card, Badge, Button } from '@/components/ui';
import { SearchInput } from '@/components/ui/search-input';
import { Tabs } from '@/components/ui/tabs';
import { HealthScoreBar } from '@/components/ui/progress-bar';
import { Avatar } from '@/components/ui/avatar';
import { Tooltip } from '@/components/ui/tooltip';
import { vehicles, maintenanceTasks, repairRequests } from '@/lib/mock-data';
import { useLocale } from '@/contexts/locale-context';
import {
  formatCurrency, formatNumber, formatDate, getStatusColor, getStatusLabel,
  getRiskColor, getRiskLabel, getFuelTypeLabel, daysUntil, cn,
} from '@/lib/utils';
import {
  Truck, Search, Filter, ChevronRight, Fuel, Gauge, Calendar, Shield,
  AlertTriangle, Wrench, MapPin, Heart, ArrowUpDown,
} from 'lucide-react';
import type { Vehicle, VehicleStatus } from '@/types';

type SortKey = 'plate' | 'brand' | 'mileage' | 'healthScore' | 'totalServiceCost';
type SortDir = 'asc' | 'desc';

export default function VehiclesPage() {
  const { t } = useLocale();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortKey, setSortKey] = useState<SortKey>('plate');
  const [sortDir, setSortDir] = useState<SortDir>('asc');
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const tabs = [
    { id: 'all', label: t('vehicles.filter.all'), count: vehicles.length },
    { id: 'active', label: t('vehicles.filter.active'), count: vehicles.filter(v => v.status === 'active').length },
    { id: 'maintenance', label: t('vehicles.filter.maintenance'), count: vehicles.filter(v => v.status === 'maintenance').length },
    { id: 'repair', label: t('vehicles.filter.repair'), count: vehicles.filter(v => v.status === 'repair').length },
    { id: 'inactive', label: t('vehicles.filter.inactive'), count: vehicles.filter(v => v.status === 'inactive').length },
  ];

  const filtered = useMemo(() => {
    let result = vehicles;
    if (statusFilter !== 'all') result = result.filter(v => v.status === statusFilter);
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(v =>
        v.plate.toLowerCase().includes(q) ||
        v.brand.toLowerCase().includes(q) ||
        v.model.toLowerCase().includes(q) ||
        v.vin.toLowerCase().includes(q)
      );
    }
    result = [...result].sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDir === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortDir === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
    });
    return result;
  }, [search, statusFilter, sortKey, sortDir]);

  const selectedVehicle = selectedId ? vehicles.find(v => v.id === selectedId) : null;

  const toggleSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortKey(key); setSortDir('asc'); }
  };

  // Stats
  const avgHealth = Math.round(vehicles.reduce((s, v) => s + v.healthScore, 0) / vehicles.length);
  const totalCost = vehicles.reduce((s, v) => s + v.totalServiceCost, 0);
  const criticalCount = vehicles.filter(v => v.riskLevel === 'critical' || v.riskLevel === 'high').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('vehicles.title')}</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{t('vehicles.subtitle')}</p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-brand-50 dark:bg-brand-900/20">
              <Truck size={18} className="text-brand-600 dark:text-brand-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">{t('vehicles.total')}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{vehicles.length}</p>
            </div>
          </div>
        </Card>
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-900/20">
              <Heart size={18} className="text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">{t('vehicles.health_score')}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{avgHealth}%</p>
            </div>
          </div>
        </Card>
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-50 dark:bg-amber-900/20">
              <AlertTriangle size={18} className="text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">{t('risk.high_risk')}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{criticalCount}</p>
            </div>
          </div>
        </Card>
        <Card className="!p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-violet-50 dark:bg-violet-900/20">
              <Wrench size={18} className="text-violet-600 dark:text-violet-400" />
            </div>
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">{t('vehicles.total_cost')}</p>
              <p className="text-lg font-bold text-slate-900 dark:text-white">{formatCurrency(totalCost)}</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <Tabs tabs={tabs} activeTab={statusFilter} onChange={setStatusFilter} variant="default" />
        <SearchInput
          value={search}
          onChange={setSearch}
          placeholder={t('vehicles.search')}
          className="w-full sm:w-72"
        />
      </div>

      {/* Layout: List + Detail */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Vehicle List */}
        <div className={cn('space-y-3', selectedVehicle ? 'xl:col-span-2' : 'xl:col-span-3')}>
          {/* Sort bar */}
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
            <ArrowUpDown size={12} />
            <span>Сортировка:</span>
            {(['plate', 'brand', 'mileage', 'healthScore', 'totalServiceCost'] as SortKey[]).map(key => (
              <button
                key={key}
                onClick={() => toggleSort(key)}
                className={cn(
                  'px-2 py-1 rounded text-xs transition-colors',
                  sortKey === key
                    ? 'bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-300 font-medium'
                    : 'hover:bg-slate-100 dark:hover:bg-slate-800'
                )}
              >
                {{ plate: 'Номер', brand: 'Марка', mileage: 'Пробег', healthScore: 'Здоровье', totalServiceCost: 'Расходы' }[key]}
                {sortKey === key && (sortDir === 'asc' ? ' ↑' : ' ↓')}
              </button>
            ))}
          </div>

          {/* Cards grid */}
          <div className={cn(
            'grid gap-3',
            selectedVehicle ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
          )}>
            {filtered.map(v => (
              <VehicleCard
                key={v.id}
                vehicle={v}
                isSelected={selectedId === v.id}
                onClick={() => setSelectedId(selectedId === v.id ? null : v.id)}
              />
            ))}
          </div>

          {filtered.length === 0 && (
            <Card className="flex flex-col items-center justify-center py-16">
              <Truck size={40} className="text-slate-300 dark:text-slate-600 mb-3" />
              <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Транспорт не найден</p>
            </Card>
          )}
        </div>

        {/* Detail Panel */}
        {selectedVehicle && (
          <div className="xl:col-span-1">
            <VehicleDetail vehicle={selectedVehicle} onClose={() => setSelectedId(null)} />
          </div>
        )}
      </div>
    </div>
  );
}

/* ───── Vehicle Card ───── */
function VehicleCard({ vehicle: v, isSelected, onClick }: { vehicle: Vehicle; isSelected: boolean; onClick: () => void }) {
  const days = daysUntil(v.nextMaintenance);
  const riskVariant = v.riskLevel === 'low' ? 'success' : v.riskLevel === 'medium' ? 'warning' : 'danger';

  return (
    <Card
      className={cn(
        '!p-4 cursor-pointer transition-all duration-200 hover:shadow-card-hover',
        isSelected && 'ring-2 ring-brand-500 ring-offset-2 dark:ring-offset-slate-950'
      )}
      padding="none"
    >
      <div onClick={onClick}>
        {/* Top row */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div className={cn(
              'w-10 h-10 rounded-lg flex items-center justify-center text-sm font-bold',
              v.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400' :
              v.status === 'repair' ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400' :
              v.status === 'maintenance' ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400' :
              'bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400'
            )}>
              <Truck size={18} />
            </div>
            <div>
              <p className="text-sm font-bold text-slate-900 dark:text-white">{v.plate}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{v.brand} {v.model}</p>
            </div>
          </div>
          <Badge variant={riskVariant}>{getRiskLabel(v.riskLevel)}</Badge>
        </div>

        {/* Info grid */}
        <div className="grid grid-cols-2 gap-2 mb-3">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Gauge size={12} />
            <span>{formatNumber(v.mileage)} км</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Fuel size={12} />
            <span>{getFuelTypeLabel(v.fuelType)}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Calendar size={12} />
            <span className={days < 0 ? 'text-red-500 font-medium' : days <= 7 ? 'text-amber-500 font-medium' : ''}>
              {days < 0 ? `ТО: ${Math.abs(days)}д назад` : `ТО: ${days}д`}
            </span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Shield size={12} />
            <span>{v.year} г.</span>
          </div>
        </div>

        {/* Health bar */}
        <HealthScoreBar score={v.healthScore} size="sm" />

        {/* Driver */}
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 dark:border-slate-800">
          {v.assignedDriver ? (
            <div className="flex items-center gap-2">
              <Avatar name={v.assignedDriver} size="xs" />
              <span className="text-xs text-slate-600 dark:text-slate-400">{v.assignedDriver}</span>
            </div>
          ) : (
            <span className="text-xs text-slate-400 italic">Не назначен</span>
          )}
          <ChevronRight size={14} className="text-slate-400" />
        </div>
      </div>
    </Card>
  );
}

/* ───── Vehicle Detail Panel ───── */
function VehicleDetail({ vehicle: v, onClose }: { vehicle: Vehicle; onClose: () => void }) {
  const { t } = useLocale();
  const [tab, setTab] = useState('info');
  const vRequests = repairRequests.filter(r => r.vehicleId === v.id);
  const vMaintenance = maintenanceTasks.filter(m => m.vehicleId === v.id);

  const detailTabs = [
    { id: 'info', label: t('vehicles.info') },
    { id: 'repairs', label: t('vehicles.repair_history'), count: vRequests.length },
    { id: 'maintenance', label: 'ТО', count: vMaintenance.length },
  ];

  return (
    <Card className="sticky top-4 !p-0 overflow-hidden">
      {/* Header */}
      <div className={cn(
        'p-5 border-b border-slate-100 dark:border-slate-800',
        v.status === 'active' ? 'bg-gradient-to-r from-emerald-50 to-white dark:from-emerald-900/10 dark:to-slate-900' :
        v.status === 'repair' ? 'bg-gradient-to-r from-red-50 to-white dark:from-red-900/10 dark:to-slate-900' :
        v.status === 'maintenance' ? 'bg-gradient-to-r from-amber-50 to-white dark:from-amber-900/10 dark:to-slate-900' :
        'bg-gradient-to-r from-slate-50 to-white dark:from-slate-800/50 dark:to-slate-900'
      )}>
        <div className="flex items-start justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-slate-900 dark:text-white">{v.plate}</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">{v.brand} {v.model}, {v.year}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>✕</Button>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={v.status === 'active' ? 'success' : v.status === 'repair' ? 'danger' : v.status === 'maintenance' ? 'warning' : 'default'}>
            {getStatusLabel(v.status)}
          </Badge>
          <Badge variant={v.riskLevel === 'low' ? 'success' : v.riskLevel === 'medium' ? 'warning' : 'danger'}>
            {t('vehicles.risk_level')}: {getRiskLabel(v.riskLevel)}
          </Badge>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-5 pt-4">
        <Tabs tabs={detailTabs} activeTab={tab} onChange={setTab} variant="underline" />
      </div>

      {/* Tab Content */}
      <div className="p-5 max-h-[60vh] overflow-y-auto">
        {tab === 'info' && (
          <div className="space-y-4">
            {/* Health Score */}
            <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{t('vehicles.health_score')}</span>
                <span className={cn('text-2xl font-bold', v.healthScore >= 80 ? 'text-emerald-600' : v.healthScore >= 60 ? 'text-brand-600' : v.healthScore >= 40 ? 'text-amber-600' : 'text-red-600')}>
                  {v.healthScore}%
                </span>
              </div>
              <HealthScoreBar score={v.healthScore} size="md" showLabel={false} />
            </div>

            {/* Details grid */}
            <div className="space-y-3">
              {[
                { label: 'VIN', value: v.vin, mono: true },
                { label: t('vehicles.mileage'), value: `${formatNumber(v.mileage)} ${t('vehicles.km')}` },
                { label: t('vehicles.fuel'), value: getFuelTypeLabel(v.fuelType) },
                { label: t('vehicles.driver'), value: v.assignedDriver || t('vehicles.no_driver') },
                { label: t('vehicles.next_to'), value: formatDate(v.nextMaintenance), highlight: daysUntil(v.nextMaintenance) < 0 },
                { label: t('vehicles.last_to'), value: v.lastMaintenance ? formatDate(v.lastMaintenance) : '—' },
                { label: t('vehicles.insurance'), value: v.insuranceExpiry ? formatDate(v.insuranceExpiry) : '—' },
                { label: t('vehicles.total_cost'), value: formatCurrency(v.totalServiceCost) },
              ].map((row, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-slate-800 last:border-0">
                  <span className="text-xs text-slate-500 dark:text-slate-400">{row.label}</span>
                  <span className={cn(
                    'text-sm font-medium text-slate-900 dark:text-white text-right',
                    row.mono && 'font-mono text-xs',
                    row.highlight && 'text-red-600 dark:text-red-400',
                  )}>
                    {row.value}
                  </span>
                </div>
              ))}
            </div>

            {/* Location */}
            {v.location && (
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                <div className="flex items-start gap-2">
                  <MapPin size={14} className="text-slate-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-xs text-slate-600 dark:text-slate-300">{v.location.address}</p>
                    <p className="text-[10px] text-slate-400 mt-0.5">{t('map.last_update')}: {new Date(v.location.updatedAt).toLocaleString('ru-RU')}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'repairs' && (
          <div className="space-y-3">
            {vRequests.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">Нет ремонтных заявок</p>
            ) : vRequests.map(r => (
              <div key={r.id} className="p-3 rounded-lg border border-slate-200 dark:border-slate-700 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono font-medium text-slate-600 dark:text-slate-400">{r.id}</span>
                  <Badge variant={r.status === 'completed' ? 'success' : r.status === 'rejected' ? 'danger' : r.status === 'in_progress' ? 'warning' : 'info'}>
                    {getStatusLabel(r.status)}
                  </Badge>
                </div>
                <p className="text-sm text-slate-700 dark:text-slate-300">{r.category}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2">{r.description}</p>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{formatDate(r.createdAt)}</span>
                  {r.slaBreached && <span className="text-red-500 font-medium">SLA ⚠</span>}
                  {r.actualCost && <span>{formatCurrency(r.actualCost)}</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {tab === 'maintenance' && (
          <div className="space-y-3">
            {vMaintenance.length === 0 ? (
              <p className="text-sm text-slate-400 text-center py-8">Нет записей ТО</p>
            ) : vMaintenance.map(m => (
              <div key={m.id} className="p-3 rounded-lg border border-slate-200 dark:border-slate-700 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800 dark:text-slate-200">{m.type}</span>
                  <Badge variant={m.status === 'completed' ? 'success' : m.status === 'overdue' ? 'danger' : m.status === 'in_progress' ? 'warning' : 'info'}>
                    {getStatusLabel(m.status)}
                  </Badge>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">{m.description}</p>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{formatDate(m.scheduledDate)}</span>
                  {m.estimatedCost && <span>{formatCurrency(m.estimatedCost)}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Card>
  );
}
