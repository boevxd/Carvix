'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  count?: number;
}

export function Skeleton({ className, variant = 'text', width, height, count = 1 }: SkeletonProps) {
  const base = 'animate-pulse bg-slate-200 dark:bg-slate-700 rounded';
  const variants = {
    text: 'h-4 rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  if (count === 1) {
    return <div className={cn(base, variants[variant], className)} style={style} />;
  }

  return (
    <div className="space-y-2.5">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className={cn(base, variants[variant], className)} style={style} />
      ))}
    </div>
  );
}

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('bg-white dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-700/60 p-5 space-y-3', className)}>
      <Skeleton variant="text" className="h-4 w-1/3" />
      <Skeleton variant="text" className="h-8 w-1/2" />
      <Skeleton variant="text" className="h-3 w-2/3" />
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4, className }: { rows?: number; cols?: number; className?: string }) {
  return (
    <div className={cn('bg-white dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-700/60 overflow-hidden', className)}>
      <div className="px-5 py-3 border-b border-slate-100 dark:border-slate-800 flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} variant="text" className="h-3 flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="px-5 py-3.5 border-b border-slate-50 dark:border-slate-800/50 flex gap-4">
          {Array.from({ length: cols }).map((_, c) => (
            <Skeleton key={c} variant="text" className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}
