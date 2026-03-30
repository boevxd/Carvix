'use client';

import React, { useState, useMemo, useCallback } from 'react';
import { Card, Badge, Button } from '@/components/ui';
import { Avatar } from '@/components/ui/avatar';
import { Tabs } from '@/components/ui/tabs';
import { HealthScoreBar } from '@/components/ui/progress-bar';
import { YandexMap } from '@/components/map/yandex-map';
import { vehicles, drivers } from '@/lib/mock-data';
import { useLocale } from '@/contexts/locale-context';
import {
  cn, formatNumber, formatCurrency, getStatusLabel, getRiskLabel,
} from '@/lib/utils';
import {
  MapPin, Truck, Navigation, Gauge, Heart, DollarSign,
  ChevronRight, Radio, Layers, X,
} from 'lucide-react';
import type { Vehicle } from '@/types';

export default function FleetMapPage() {
  const { t } = useLocale();
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [showList, setShowList] = useState(true);

  const filtered = useMemo(() => {
    if (statusFilter === 'all') return vehicles.filter(v => v.location);
    return vehicles.filter(v => v.location && v.status === statusFilter);
  }, [statusFilter]);

  const statusCounts = {
    all: vehicles.filter(v => v.location).length,
    active: vehicles.filter(v => v.location && v.status === 'active').length,
    maintenance: vehicles.filter(v => v.location && v.status === 'maintenance').length,
    repair: vehicles.filter(v => v.location && v.status === 'repair').length,
    inactive: vehicles.filter(v => v.location && v.status === 'inactive').length,
  };

  const tabs = [
    { id: 'all', label: t('map.filter.all'), count: statusCounts.all },
    { id: 'active', label: t('vehicles.filter.active'), count: statusCounts.active },
    { id: 'maintenance', label: t('vehicles.filter.maintenance'), count: statusCounts.maintenance },
    { id: 'repair', label: t('vehicles.filter.repair'), count: statusCounts.repair },
  ];

  // Find nearest available vehicle to center
  const nearestAvailable = useMemo(() => {
    const center = { lat: 55.7558, lng: 37.6173 };
    return vehicles
      .filter(v => v.status === 'active' && v.location)
      .sort((a, b) => {
        const dA = Math.abs(a.location!.lat - center.lat) + Math.abs(a.location!.lng - center.lng);
        const dB = Math.abs(b.location!.lat - center.lat) + Math.abs(b.location!.lng - center.lng);
        return dA - dB;
      })[0];
  }, []);

  const handleSelectVehicle = useCallback((v: Vehicle | null) => {
    setSelectedVehicle(v);
  }, []);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">{t('map.title')}</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{t('map.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
            <Radio size={12} className="text-emerald-500 animate-pulse" />
            <span>{t('map.vehicles_on_map')}: {filtered.length}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <Tabs tabs={tabs} activeTab={statusFilter} onChange={setStatusFilter} variant="default" />

      {/* Map + sidebar layout */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-5" style={{ minHeight: '70vh' }}>
        {/* Map area — Real Yandex Maps */}
        <div className={cn(
          'relative rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700',
          showList ? 'xl:col-span-3' : 'xl:col-span-4'
        )}>
          <YandexMap
            vehicles={filtered}
            selectedVehicle={selectedVehicle}
            onSelectVehicle={handleSelectVehicle}
            className="w-full h-full min-h-[70vh]"
          />

          {/* Legend overlay */}
          <div className="absolute top-4 left-4 z-10 pointer-events-none">
            <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm rounded-lg shadow-md border border-slate-200 dark:border-slate-700 p-3 pointer-events-auto">
              <div className="flex items-center gap-3 text-[10px]">
                {[
                  { color: 'bg-emerald-500', label: t('vehicles.filter.active') },
                  { color: 'bg-amber-500', label: t('vehicles.filter.maintenance') },
                  { color: 'bg-red-500', label: t('vehicles.filter.repair') },
                  { color: 'bg-slate-400', label: t('vehicles.filter.inactive') },
                ].map(l => (
                  <div key={l.label} className="flex items-center gap-1.5">
                    <span className={cn('w-2.5 h-2.5 rounded-full', l.color)} />
                    <span className="text-slate-600 dark:text-slate-400">{l.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Selected vehicle popup overlay */}
          {selectedVehicle && (
            <div className="absolute bottom-4 left-4 z-10 w-80 animate-slide-up">
              <Card className="!p-4 shadow-xl">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className={cn(
                      'w-10 h-10 rounded-lg flex items-center justify-center',
                      selectedVehicle.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/20' :
                      selectedVehicle.status === 'repair' ? 'bg-red-50 dark:bg-red-900/20' :
                      'bg-amber-50 dark:bg-amber-900/20'
                    )}>
                      <Truck size={18} className={
                        selectedVehicle.status === 'active' ? 'text-emerald-600' :
                        selectedVehicle.status === 'repair' ? 'text-red-600' : 'text-amber-600'
                      } />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 dark:text-white">{selectedVehicle.plate}</p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">{selectedVehicle.brand} {selectedVehicle.model} · {selectedVehicle.year}</p>
                    </div>
                  </div>
                  <button onClick={() => setSelectedVehicle(null)} className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
                    <X size={14} />
                  </button>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant={selectedVehicle.status === 'active' ? 'success' : selectedVehicle.status === 'repair' ? 'danger' : 'warning'}>
                      {getStatusLabel(selectedVehicle.status)}
                    </Badge>
                    <Badge variant={selectedVehicle.riskLevel === 'low' ? 'success' : selectedVehicle.riskLevel === 'critical' ? 'danger' : 'warning'}>
                      {getRiskLabel(selectedVehicle.riskLevel)}
                    </Badge>
                  </div>
                  {selectedVehicle.assignedDriver && (
                    <div className="flex items-center gap-2 pt-1">
                      <Avatar name={selectedVehicle.assignedDriver} size="xs" />
                      <span className="text-xs text-slate-600 dark:text-slate-400">{selectedVehicle.assignedDriver}</span>
                    </div>
                  )}
                  <div className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 pt-1">
                    <MapPin size={12} />
                    <span>{selectedVehicle.location?.address}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2 pt-2">
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                      <Gauge size={12} className="mx-auto text-slate-400 mb-0.5" />
                      <p className="text-[10px] text-slate-400">Пробег</p>
                      <p className="text-xs font-bold text-slate-900 dark:text-white">{formatNumber(selectedVehicle.mileage)}</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                      <Heart size={12} className="mx-auto text-slate-400 mb-0.5" />
                      <p className="text-[10px] text-slate-400">Здоровье</p>
                      <p className="text-xs font-bold text-slate-900 dark:text-white">{selectedVehicle.healthScore}%</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                      <DollarSign size={12} className="mx-auto text-slate-400 mb-0.5" />
                      <p className="text-[10px] text-slate-400">Расходы</p>
                      <p className="text-xs font-bold text-slate-900 dark:text-white">{formatCurrency(selectedVehicle.totalServiceCost)}</p>
                    </div>
                  </div>
                  <HealthScoreBar score={selectedVehicle.healthScore} size="sm" showLabel={false} className="mt-1" />
                </div>
              </Card>
            </div>
          )}

          {/* Toggle list button (mobile) */}
          <button
            onClick={() => setShowList(!showList)}
            className="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white dark:bg-slate-900 shadow-md border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors xl:hidden"
          >
            <Layers size={16} />
          </button>
        </div>

        {/* Side list */}
        {showList && (
          <div className="xl:col-span-1 space-y-3 max-h-[70vh] overflow-y-auto">
            {/* Nearest available highlight */}
            {nearestAvailable && (
              <Card className="!p-3 border-brand-200 dark:border-brand-800 bg-brand-50/50 dark:bg-brand-900/10">
                <div className="flex items-center gap-2 mb-2">
                  <Navigation size={12} className="text-brand-600 dark:text-brand-400" />
                  <span className="text-[10px] font-semibold text-brand-700 dark:text-brand-300 uppercase tracking-wide">{t('map.nearest')}</span>
                </div>
                <button
                  className="flex items-center gap-2.5 w-full text-left"
                  onClick={() => handleSelectVehicle(nearestAvailable)}
                >
                  <div className="w-8 h-8 rounded-lg bg-brand-100 dark:bg-brand-900/30 flex items-center justify-center">
                    <Truck size={14} className="text-brand-600" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-slate-900 dark:text-white">{nearestAvailable.plate}</p>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">{nearestAvailable.assignedDriver}</p>
                  </div>
                </button>
              </Card>
            )}

            {/* Vehicle list */}
            {filtered.map(v => {
              const driver = drivers.find(d => d.id === v.assignedDriverId);
              const isSelected = selectedVehicle?.id === v.id;
              return (
                <Card
                  key={v.id}
                  className={cn(
                    '!p-3 cursor-pointer transition-all hover:shadow-card-hover',
                    isSelected && 'ring-2 ring-brand-500 ring-offset-1 dark:ring-offset-slate-950'
                  )}
                  padding="none"
                >
                  <div onClick={() => handleSelectVehicle(isSelected ? null : v)}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <div className={cn(
                          'w-8 h-8 rounded-lg flex items-center justify-center',
                          v.status === 'active' ? 'bg-emerald-50 dark:bg-emerald-900/20' :
                          v.status === 'repair' ? 'bg-red-50 dark:bg-red-900/20' :
                          v.status === 'maintenance' ? 'bg-amber-50 dark:bg-amber-900/20' :
                          'bg-slate-100 dark:bg-slate-800'
                        )}>
                          <Truck size={13} className={
                            v.status === 'active' ? 'text-emerald-600 dark:text-emerald-400' :
                            v.status === 'repair' ? 'text-red-600 dark:text-red-400' :
                            v.status === 'maintenance' ? 'text-amber-600 dark:text-amber-400' :
                            'text-slate-400'
                          } />
                        </div>
                        <div>
                          <p className="text-xs font-bold text-slate-900 dark:text-white">{v.plate}</p>
                          <p className="text-[10px] text-slate-400">{v.brand} {v.model}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-[10px] font-medium text-slate-500 dark:text-slate-400">{v.healthScore}%</span>
                        <ChevronRight size={14} className="text-slate-400" />
                      </div>
                    </div>
                    {v.assignedDriver && (
                      <div className="flex items-center gap-1.5 mt-2 pl-[42px]">
                        <Avatar name={v.assignedDriver} size="xs" status={driver?.status === 'На линии' ? 'online' : 'offline'} />
                        <span className="text-[10px] text-slate-500 dark:text-slate-400">{v.assignedDriver}</span>
                      </div>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
