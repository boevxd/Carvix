'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface AvatarProps {
  name: string;
  src?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  status?: 'online' | 'offline' | 'busy' | 'away';
}

export function Avatar({ name, src, size = 'md', className, status }: AvatarProps) {
  const initials = name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  const sizes = {
    xs: 'w-6 h-6 text-[10px]',
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  };

  const statusSizes = {
    xs: 'w-1.5 h-1.5 right-0 bottom-0',
    sm: 'w-2 h-2 right-0 bottom-0',
    md: 'w-2.5 h-2.5 right-0 bottom-0',
    lg: 'w-3 h-3 right-0.5 bottom-0.5',
    xl: 'w-3.5 h-3.5 right-1 bottom-1',
  };

  const statusColors = {
    online: 'bg-emerald-500',
    offline: 'bg-slate-400',
    busy: 'bg-red-500',
    away: 'bg-amber-500',
  };

  const colors = [
    'bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300',
    'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300',
    'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300',
    'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300',
    'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300',
    'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300',
  ];

  const colorIdx = name.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % colors.length;

  return (
    <div className={cn('relative inline-flex flex-shrink-0', className)}>
      {src ? (
        <img
          src={src}
          alt={name}
          className={cn('rounded-full object-cover', sizes[size])}
        />
      ) : (
        <div
          className={cn(
            'rounded-full flex items-center justify-center font-bold',
            sizes[size],
            colors[colorIdx],
          )}
        >
          {initials}
        </div>
      )}
      {status && (
        <span
          className={cn(
            'absolute rounded-full border-2 border-white dark:border-slate-900',
            statusSizes[size],
            statusColors[status],
          )}
        />
      )}
    </div>
  );
}
