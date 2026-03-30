'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

interface TabsProps {
  tabs: Tab[];
  activeTab?: string;
  onChange?: (id: string) => void;
  variant?: 'default' | 'pills' | 'underline';
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, variant = 'default', className }: TabsProps) {
  const [internalActive, setInternalActive] = useState(tabs[0]?.id);
  const active = activeTab ?? internalActive;

  const handleClick = (id: string) => {
    setInternalActive(id);
    onChange?.(id);
  };

  const variants = {
    default: {
      container: 'flex gap-1 p-1 bg-slate-100 dark:bg-slate-800 rounded-lg',
      tab: 'px-3.5 py-2 text-sm font-medium rounded-md transition-all duration-200',
      active: 'bg-white dark:bg-slate-900 text-slate-900 dark:text-white shadow-sm',
      inactive: 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300',
    },
    pills: {
      container: 'flex gap-2',
      tab: 'px-4 py-2 text-sm font-medium rounded-full transition-all duration-200 border',
      active: 'bg-brand-600 text-white border-brand-600',
      inactive: 'text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:border-brand-300 hover:text-brand-600 dark:hover:text-brand-400',
    },
    underline: {
      container: 'flex gap-6 border-b border-slate-200 dark:border-slate-700',
      tab: 'pb-3 text-sm font-medium transition-all duration-200 border-b-2 -mb-px',
      active: 'text-brand-600 dark:text-brand-400 border-brand-600 dark:border-brand-400',
      inactive: 'text-slate-500 dark:text-slate-400 border-transparent hover:text-slate-700 dark:hover:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600',
    },
  };

  const v = variants[variant];

  return (
    <div className={cn(v.container, className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => handleClick(tab.id)}
          className={cn(v.tab, active === tab.id ? v.active : v.inactive)}
        >
          <span className="flex items-center gap-2">
            {tab.icon}
            {tab.label}
            {tab.count !== undefined && (
              <span className={cn(
                'text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center',
                active === tab.id
                  ? variant === 'pills' ? 'bg-white/20 text-white' : 'bg-brand-100 dark:bg-brand-900/30 text-brand-700 dark:text-brand-300'
                  : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-400',
              )}>
                {tab.count}
              </span>
            )}
          </span>
        </button>
      ))}
    </div>
  );
}
