'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  color?: 'brand' | 'emerald' | 'amber' | 'red' | 'slate';
  showLabel?: boolean;
  label?: string;
  className?: string;
}

export function ProgressBar({
  value,
  max = 100,
  size = 'md',
  color = 'brand',
  showLabel = false,
  label,
  className,
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));

  const sizes = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4',
  };

  const colors = {
    brand: 'bg-brand-500',
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    red: 'bg-red-500',
    slate: 'bg-slate-400',
  };

  return (
    <div className={cn('w-full', className)}>
      {(showLabel || label) && (
        <div className="flex items-center justify-between mb-1.5">
          {label && <span className="text-xs font-medium text-slate-600 dark:text-slate-400">{label}</span>}
          {showLabel && <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">{Math.round(pct)}%</span>}
        </div>
      )}
      <div className={cn('w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden', sizes[size])}>
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', colors[color])}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

interface HealthScoreBarProps {
  score: number;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function HealthScoreBar({ score, size = 'md', showLabel = true, className }: HealthScoreBarProps) {
  const color = score >= 80 ? 'emerald' : score >= 60 ? 'brand' : score >= 40 ? 'amber' : 'red';
  return <ProgressBar value={score} color={color} size={size} showLabel={showLabel} className={className} />;
}
