'use client';

import React, { useEffect, useRef, useState } from 'react';
import type { Vehicle } from '@/types';
import { getStatusLabel, formatNumber, formatCurrency } from '@/lib/utils';

declare global {
  interface Window {
    ymaps: any;
  }
}

interface YandexMapProps {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  onSelectVehicle: (vehicle: Vehicle | null) => void;
  className?: string;
}

const STATUS_COLORS: Record<string, string> = {
  active: '#10b981',
  maintenance: '#f59e0b',
  repair: '#ef4444',
  inactive: '#94a3b8',
};

const STATUS_BG: Record<string, string> = {
  active: '#ecfdf5',
  maintenance: '#fffbeb',
  repair: '#fef2f2',
  inactive: '#f8fafc',
};

/** Build an SVG data URL for a truck icon marker */
function buildTruckIconSvg(color: string, bg: string, plate: string): string {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="48" height="56" viewBox="0 0 48 56">
    <defs>
      <filter id="s" x="-20%" y="-10%" width="140%" height="140%">
        <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.25"/>
      </filter>
    </defs>
    <g filter="url(#s)">
      <path d="M24 52 L18 42 L6 42 C3.8 42 2 40.2 2 38 L2 6 C2 3.8 3.8 2 6 2 L42 2 C44.2 2 46 3.8 46 6 L46 38 C46 40.2 44.2 42 42 42 L30 42 Z" fill="white" stroke="${color}" stroke-width="2"/>
      <rect x="6" y="6" width="36" height="28" rx="4" fill="${bg}"/>
      <g transform="translate(14, 10)">
        <path d="M12 16V5a1.5 1.5 0 0 0-1.5-1.5h-6A1.5 1.5 0 0 0 3 5v10a.75.75 0 0 0 .75.75H5" fill="none" stroke="${color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M12.75 16H8.25" fill="none" stroke="${color}" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M15.75 16h1.5a.75.75 0 0 0 .75-.75v-2.74a.75.75 0 0 0-.165-.468l-2.61-3.26a.75.75 0 0 0-.585-.282H12" fill="none" stroke="${color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="14.25" cy="16" r="1.5" fill="none" stroke="${color}" stroke-width="1.5"/>
        <circle cx="6" cy="16" r="1.5" fill="none" stroke="${color}" stroke-width="1.5"/>
      </g>
    </g>
  </svg>`;
  return 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(svg);
}

let ymapsScriptLoaded = false;
let ymapsReady = false;
let ymapsReadyCallbacks: (() => void)[] = [];

function loadYmaps(): Promise<void> {
  return new Promise((resolve) => {
    if (ymapsReady) {
      resolve();
      return;
    }
    ymapsReadyCallbacks.push(resolve);
    if (!ymapsScriptLoaded) {
      ymapsScriptLoaded = true;
      const script = document.createElement('script');
      script.src = 'https://api-maps.yandex.ru/2.1/?lang=ru_RU';
      script.type = 'text/javascript';
      script.async = true;
      script.onload = () => {
        window.ymaps.ready(() => {
          ymapsReady = true;
          ymapsReadyCallbacks.forEach((cb) => cb());
          ymapsReadyCallbacks = [];
        });
      };
      document.head.appendChild(script);
    }
  });
}

export function YandexMap({ vehicles, selectedVehicle, onSelectVehicle, className }: YandexMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<Map<string, any>>(new Map());
  const clusterRef = useRef<any>(null);
  const [loading, setLoading] = useState(true);

  // Initialize map
  useEffect(() => {
    let cancelled = false;

    loadYmaps().then(() => {
      if (cancelled || !containerRef.current) return;
      const ymaps = window.ymaps;

      const map = new ymaps.Map(containerRef.current, {
        center: [55.7558, 37.6173],
        zoom: 11,
        controls: [],
      }, {
        suppressMapOpenBlock: true,
      });

      map.controls.add('zoomControl', { float: 'right', size: 'small' });
      map.controls.add('geolocationControl', { float: 'right' });
      map.controls.add('typeSelector', { float: 'right', panoramasItemMode: 'off' });
      map.controls.add('rulerControl', { float: 'right' });
      map.controls.add('trafficControl', { float: 'right' });
      map.behaviors.enable(['scrollZoom', 'drag', 'multiTouch']);

      map.events.add('click', () => {
        onSelectVehicle(null);
      });

      mapRef.current = map;
      setLoading(false);
    });

    return () => {
      cancelled = true;
      if (mapRef.current) {
        mapRef.current.destroy();
        mapRef.current = null;
      }
      markersRef.current.clear();
      clusterRef.current = null;
    };
  }, []);

  // Update markers when vehicles change
  useEffect(() => {
    if (!mapRef.current || !ymapsReady) return;
    const ymaps = window.ymaps;
    const map = mapRef.current;

    if (clusterRef.current) {
      map.geoObjects.remove(clusterRef.current);
    }
    markersRef.current.clear();

    const clusterer = new ymaps.Clusterer({
      preset: 'islands#invertedDarkBlueClusterIcons',
      groupByCoordinates: false,
      clusterDisableClickZoom: false,
      clusterHideIconOnBalloonOpen: false,
      geoObjectHideIconOnBalloonOpen: false,
      clusterBalloonContentLayout: 'cluster#balloonCarousel',
    });

    const placemarks: any[] = [];

    vehicles.forEach((v) => {
      if (!v.location) return;

      const statusColor = STATUS_COLORS[v.status] || '#94a3b8';
      const statusBg = STATUS_BG[v.status] || '#f8fafc';
      const statusLabel = getStatusLabel(v.status);
      const healthBar = v.healthScore >= 80 ? '#10b981' : v.healthScore >= 60 ? '#3b82f6' : v.healthScore >= 40 ? '#f59e0b' : '#ef4444';

      const balloonContent = `
        <div style="padding:10px;min-width:240px;font-family:Inter,-apple-system,sans-serif;">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
            <div style="width:36px;height:36px;border-radius:10px;background:${statusBg};border:1.5px solid ${statusColor};display:flex;align-items:center;justify-content:center;">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="${statusColor}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/>
                <path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/>
                <circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>
              </svg>
            </div>
            <div>
              <div style="font-weight:700;font-size:14px;color:#0f172a;">${v.plate}</div>
              <div style="font-size:11px;color:#64748b;">${v.brand} ${v.model} · ${v.year}</div>
            </div>
          </div>
          <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap;">
            <span style="padding:2px 8px;border-radius:9999px;font-size:10px;font-weight:600;background:${statusBg};color:${statusColor};border:1px solid ${statusColor}30;">${statusLabel}</span>
            <span style="padding:2px 8px;border-radius:9999px;font-size:10px;font-weight:600;background:#f1f5f9;color:#475569;">❤ ${v.healthScore}%</span>
          </div>
          ${v.assignedDriver ? `<div style="font-size:11px;color:#475569;margin-bottom:4px;">👤 ${v.assignedDriver}</div>` : ''}
          <div style="font-size:11px;color:#475569;margin-bottom:4px;">📍 ${v.location?.address || '—'}</div>
          <div style="display:flex;gap:12px;font-size:11px;color:#475569;margin-bottom:6px;">
            <span>🛣 ${formatNumber(v.mileage)} км</span>
            <span>💰 ${formatCurrency(v.totalServiceCost)}</span>
          </div>
          <div style="height:5px;border-radius:5px;background:#e2e8f0;overflow:hidden;">
            <div style="height:100%;width:${v.healthScore}%;border-radius:5px;background:${healthBar};transition:width .3s;"></div>
          </div>
        </div>
      `;

      const iconUrl = buildTruckIconSvg(statusColor, statusBg, v.plate);

      const placemark = new ymaps.Placemark(
        [v.location.lat, v.location.lng],
        {
          balloonContentBody: balloonContent,
          hintContent: `${v.plate} — ${statusLabel} — ${v.brand} ${v.model}`,
          vehicleId: v.id,
        },
        {
          iconLayout: 'default#image',
          iconImageHref: iconUrl,
          iconImageSize: [44, 52],
          iconImageOffset: [-22, -52],
        }
      );

      placemark.events.add('click', (e: any) => {
        e.stopPropagation();
        onSelectVehicle(v);
      });

      markersRef.current.set(v.id, placemark);
      placemarks.push(placemark);
    });

    clusterer.add(placemarks);
    map.geoObjects.add(clusterer);
    clusterRef.current = clusterer;

    if (placemarks.length > 0) {
      map.setBounds(clusterer.getBounds(), {
        checkZoomRange: true,
        zoomMargin: 50,
      }).catch(() => {});
    }
  }, [vehicles, onSelectVehicle]);

  // Pan to selected vehicle
  useEffect(() => {
    if (!mapRef.current || !selectedVehicle?.location) return;

    mapRef.current.panTo(
      [selectedVehicle.location.lat, selectedVehicle.location.lng],
      { flying: true, duration: 500 }
    ).then(() => {
      if (mapRef.current && mapRef.current.getZoom() < 14) {
        mapRef.current.setZoom(14, { duration: 300 });
      }
    });

    const marker = markersRef.current.get(selectedVehicle.id);
    if (marker) {
      marker.balloon.open();
    }
  }, [selectedVehicle]);

  return (
    <div className={className} style={{ position: 'relative', width: '100%', height: '100%' }}>
      {loading && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-slate-100 dark:bg-slate-800 rounded-2xl">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-brand-600 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-slate-500 dark:text-slate-400">Загрузка карты...</span>
          </div>
        </div>
      )}
      <div
        ref={containerRef}
        style={{ width: '100%', height: '100%', borderRadius: 'inherit' }}
      />
    </div>
  );
}
