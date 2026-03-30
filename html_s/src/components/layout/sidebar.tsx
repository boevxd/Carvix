'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuth } from '@/contexts/auth-context';
import { useLocale } from '@/contexts/locale-context';
import {
  LayoutDashboard, Wrench, ClipboardList, Bell, HeadphonesIcon,
  Truck, BarChart3, Users, Settings, LogOut, ChevronLeft, Menu, X,
  Shield, Map, Calendar, Package, Activity, FileText,
} from 'lucide-react';

interface SidebarProps {
  role?: 'driver' | 'dispatcher' | 'admin';
}

export function Sidebar({ role = 'driver' }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const { user, logout } = useAuth();
  const { t } = useLocale();

  const navItems = {
    driver: [
      { href: '/dashboard', label: t('nav.overview'), icon: LayoutDashboard },
      { href: '/dashboard/requests/new', label: t('nav.new_request'), icon: Wrench },
      { href: '/dashboard/requests', label: t('nav.my_requests'), icon: ClipboardList },
      { href: '/dashboard/notifications', label: t('nav.notifications'), icon: Bell },
      { href: '/dashboard/support', label: t('nav.support'), icon: HeadphonesIcon },
      { href: '/dashboard/settings', label: t('nav.settings'), icon: Settings },
    ],
    dispatcher: [
      { href: '/dispatcher', label: t('nav.dispatcher_panel'), icon: LayoutDashboard },
      { href: '/dispatcher/vehicles', label: t('nav.transport'), icon: Truck },
      { href: '/dispatcher/map', label: t('map.title'), icon: Map },
      { href: '/dispatcher/calendar', label: t('calendar.title'), icon: Calendar },
      { href: '/dispatcher/parts', label: t('parts.title'), icon: Package },
      { href: '/dispatcher/activity', label: t('activity.title'), icon: Activity },
      { href: '/dispatcher/settings', label: t('nav.settings'), icon: Settings },
    ],
    admin: [
      { href: '/admin', label: t('nav.analytics'), icon: BarChart3 },
      { href: '/admin/vehicles', label: t('nav.transport'), icon: Truck },
      { href: '/admin/map', label: t('map.title'), icon: Map },
      { href: '/admin/calendar', label: t('calendar.title'), icon: Calendar },
      { href: '/admin/parts', label: t('parts.title'), icon: Package },
      { href: '/admin/activity', label: t('activity.title'), icon: Activity },
      { href: '/admin/reports', label: t('export.title'), icon: FileText },
      { href: '/admin/settings', label: t('nav.settings'), icon: Settings },
    ],
  };

  const items = navItems[role];
  const roleLabels = {
    driver: t('role.driver'),
    dispatcher: t('role.dispatcher'),
    admin: t('role.admin'),
  };

  const nameParts = user?.full_name?.split(' ') ?? [];
  const initials = nameParts.length >= 2
    ? nameParts[0].charAt(0) + nameParts[1].charAt(0)
    : nameParts[0]?.charAt(0) ?? 'ФК';

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={cn('flex items-center gap-3 px-4 h-16 border-b border-white/[0.06]', collapsed && 'justify-center px-0')}>
        <img src="/logo-carvix.png" alt="Carvix" className="w-8 h-8 rounded-lg object-cover flex-shrink-0" />
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-bold text-white tracking-tight">Carvix</span>
            <span className="text-[10px] text-slate-500 uppercase tracking-wider">{t('nav.fleet_mgmt')}</span>
          </div>
        )}
      </div>

      {/* Role badge */}
      {!collapsed && (
        <div className="px-4 pt-4 pb-2">
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.06]">
            <Shield size={14} className="text-brand-400" />
            <span className="text-xs font-medium text-slate-400">{roleLabels[role]}</span>
          </div>
        </div>
      )}

      {/* Nav links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {items.map((item, i) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={i}
              href={item.href}
              onClick={() => setMobileOpen(false)}
              className={cn(
                isActive ? 'sidebar-link-active' : 'sidebar-link',
                collapsed && 'justify-center px-0',
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon size={18} className="flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="px-3 pb-4 space-y-1 border-t border-white/[0.06] pt-4">
        {!collapsed && user && (
          <div className="flex items-center gap-3 px-3 py-2.5 mb-2">
            <div className="w-8 h-8 rounded-full bg-brand-600/20 flex items-center justify-center text-xs font-bold text-brand-400">
              {initials}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-medium text-white truncate">{user.full_name}</span>
              <span className="text-xs text-slate-500 truncate">{user.email}</span>
            </div>
          </div>
        )}
        <button onClick={logout} className="sidebar-link w-full">
          <LogOut size={18} className="flex-shrink-0" />
          {!collapsed && <span>{t('nav.logout')}</span>}
        </button>
      </div>

      {/* Collapse toggle — desktop only */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="hidden lg:flex items-center justify-center h-10 border-t border-white/[0.06] text-slate-500 hover:text-white transition-colors"
      >
        <ChevronLeft size={16} className={cn('transition-transform', collapsed && 'rotate-180')} />
      </button>
    </div>
  );

  return (
    <>
      {/* Mobile toggle */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-slate-900 text-white shadow-lg"
      >
        <Menu size={20} />
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40 bg-black/50" onClick={() => setMobileOpen(false)}>
          <div
            className="w-64 h-full bg-slate-900 shadow-sidebar animate-slide-in-left"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white"
            >
              <X size={20} />
            </button>
            {sidebarContent}
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <aside
        className={cn(
          'hidden lg:flex flex-col bg-slate-900 border-r border-white/[0.06] transition-all duration-300 flex-shrink-0',
          collapsed ? 'w-16' : 'w-64',
        )}
      >
        {sidebarContent}
      </aside>
    </>
  );
}
