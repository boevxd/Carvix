'use client';

import React from 'react';
import { cn } from '@/lib/utils';

/* ───────────────── Button ───────────────── */
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  className,
  children,
  ...props
}: ButtonProps) {
  const base =
    'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none';
  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700 focus:ring-brand-500 shadow-sm',
    secondary: 'bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-500 shadow-sm',
    outline: 'border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 focus:ring-brand-500',
    ghost: 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white focus:ring-slate-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm',
  };
  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-4 py-2.5 gap-2',
    lg: 'text-sm px-6 py-3 gap-2',
  };

  return (
    <button className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </button>
  );
}

/* ───────────────── Badge ───────────────── */
interface BadgeProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}

export function Badge({ children, className, variant = 'default' }: BadgeProps) {
  const variants = {
    default: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700',
    success: 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 border-emerald-200 dark:border-emerald-800',
    warning: 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800',
    danger: 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800',
    info: 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}

/* ───────────────── Card ───────────────── */
interface CardProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function Card({ children, className, padding = 'md' }: CardProps) {
  const paddings = {
    none: '',
    sm: 'p-4',
    md: 'p-5',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(
        'bg-white dark:bg-slate-900 rounded-xl border border-slate-200/60 dark:border-slate-700/60 shadow-card',
        paddings[padding],
        className,
      )}
    >
      {children}
    </div>
  );
}

/* ───────────────── Input ───────────────── */
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s/g, '-');
    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'input-field',
            error && 'border-red-300 focus:border-red-500 focus:ring-red-500/20',
            className,
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
        {hint && !error && <p className="text-xs text-slate-400">{hint}</p>}
      </div>
    );
  },
);
Input.displayName = 'Input';

/* ───────────────── Textarea ───────────────── */
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ label, error, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s/g, '-');
    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={inputId} className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={cn(
            'input-field min-h-[100px] resize-y',
            error && 'border-red-300 focus:border-red-500 focus:ring-red-500/20',
            className,
          )}
          {...props}
        />
        {error && <p className="text-xs text-red-600">{error}</p>}
      </div>
    );
  },
);
Textarea.displayName = 'Textarea';

/* ───────────────── Select ───────────────── */
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
}

export function Select({ label, error, options, placeholder, className, id, ...props }: SelectProps) {
  const inputId = id || label?.toLowerCase().replace(/\s/g, '-');
  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={inputId} className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          {label}
        </label>
      )}
      <select id={inputId} className={cn('input-field', className)} {...props}>
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  );
}

/* ───────────────── MetricCard ───────────────── */
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number | { value: number; positive: boolean };
  changeLabel?: string;
  icon: React.ReactNode;
  iconBg?: string;
}

export function MetricCard({ title, value, change, changeLabel, icon, iconBg = 'bg-brand-50' }: MetricCardProps) {
  const changeValue = typeof change === 'object' ? change.value : change;
  const isPositive = typeof change === 'object' ? change.positive : (change !== undefined ? change >= 0 : true);

  return (
    <div className="metric-card">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">{value}</p>
          {change !== undefined && (
            <div className="flex items-center gap-1.5">
              <span
                className={cn(
                  'text-xs font-semibold',
                  isPositive ? 'text-emerald-600' : 'text-red-600',
                )}
              >
                {isPositive ? '+' : ''}
                {changeValue}%
              </span>
              {changeLabel && <span className="text-xs text-slate-400">{changeLabel}</span>}
            </div>
          )}
        </div>
        <div className={cn('p-2.5 rounded-lg', iconBg)}>{icon}</div>
      </div>
    </div>
  );
}

/* ───────────────── EmptyState ───────────────── */
interface EmptyStateProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="text-slate-300 dark:text-slate-600 mb-4">{icon}</div>
      <h3 className="text-base font-semibold text-slate-900 dark:text-white mb-1">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm mb-6">{description}</p>
      {action}
    </div>
  );
}

/* ───────────────── StatusDot ───────────────── */
export function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    active: 'bg-emerald-500',
    maintenance: 'bg-amber-500',
    repair: 'bg-red-500',
    inactive: 'bg-slate-400',
    online: 'bg-emerald-500',
    offline: 'bg-slate-400',
  };

  return (
    <span className="relative flex h-2.5 w-2.5">
      <span
        className={cn(
          'absolute inline-flex h-full w-full rounded-full opacity-40 animate-ping',
          colors[status] || 'bg-slate-400',
          status === 'inactive' && 'animate-none',
        )}
      />
      <span className={cn('relative inline-flex rounded-full h-2.5 w-2.5', colors[status] || 'bg-slate-400')} />
    </span>
  );
}
