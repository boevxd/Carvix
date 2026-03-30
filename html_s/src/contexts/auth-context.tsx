'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { auth as apiAuth, setToken, removeToken, ApiUser } from '@/lib/api';

interface AuthContextType {
  user: ApiUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  updateProfile: (data: Partial<ApiUser>) => void;
  changePassword: (currentPassword: string, newPassword: string) => Promise<{ success: boolean; error?: string }>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<ApiUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refreshUser = useCallback(async () => {
    try {
      const me = await apiAuth.me();
      setUser(me);
    } catch {
      removeToken();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const token = typeof window !== 'undefined' ? localStorage.getItem('carvix_token') : null;
    if (token) {
      refreshUser().finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [refreshUser]);

  const login = useCallback(async (username: string, password: string) => {
    try {
      const res = await apiAuth.login(username, password);
      setToken(res.access_token);
      setUser(res.user);

      const roleMap: Record<string, string> = {
        'admin': '/admin',
        'Администратор': '/admin',
        'dispatcher': '/dispatcher',
        'Диспетчер': '/dispatcher',
        'driver': '/dashboard',
        'Пользователь': '/dashboard',
        'mechanic': '/dashboard',
        'Механик': '/dashboard',
        'analyst': '/admin',
        'Аналитик': '/admin',
        'director': '/admin',
        'Директор': '/admin',
      };
      const href = roleMap[res.user.role_name] || '/dashboard';
      router.push(href);
      return { success: true };
    } catch (e: any) {
      return { success: false, error: e.message || 'Неверный логин или пароль' };
    }
  }, [router]);

  const logout = useCallback(() => {
    removeToken();
    setUser(null);
    router.push('/login');
  }, [router]);

  const updateProfile = useCallback((data: Partial<ApiUser>) => {
    if (user) setUser({ ...user, ...data });
  }, [user]);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    try {
      await apiAuth.changePassword(currentPassword, newPassword);
      return { success: true };
    } catch (e: any) {
      return { success: false, error: e.message };
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, updateProfile, changePassword, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
