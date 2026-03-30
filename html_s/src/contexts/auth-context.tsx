'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DBUser, seedDB, authenticateUser, registerUser, getSessionUser, setSession, clearSession, updateUser, updateUserNotificationPrefs } from '@/lib/db';
import { UserRole } from '@/types';

interface AuthContextType {
  user: DBUser | null;
  loading: boolean;
  login: (email: string, password: string) => { success: boolean; error?: string };
  loginAsRole: (role: UserRole) => void;
  register: (data: { firstName: string; lastName: string; email: string; phone: string; role: UserRole; password: string }) => { success: boolean; error?: string };
  logout: () => void;
  updateProfile: (data: Partial<Omit<DBUser, 'id'>>) => boolean;
  updateNotifPrefs: (prefs: DBUser['notificationPrefs']) => void;
  changePassword: (currentPassword: string, newPassword: string) => { success: boolean; error?: string };
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<DBUser | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    seedDB();
    const sessionUser = getSessionUser();
    setUser(sessionUser);
    setLoading(false);
  }, []);

  const login = useCallback((email: string, password: string) => {
    const found = authenticateUser(email, password);
    if (!found) return { success: false, error: 'auth.error.invalid' };
    setSession(found.id);
    setUser(found);
    return { success: true };
  }, []);

  const loginAsRole = useCallback((role: UserRole) => {
    const emailMap: Record<UserRole, string> = {
      driver: 'driver@fleet.ru',
      dispatcher: 'dispatcher@fleet.ru',
      admin: 'admin@fleet.ru',
    };
    const passMap: Record<UserRole, string> = {
      driver: 'driver123',
      dispatcher: 'dispatcher123',
      admin: 'admin123',
    };
    const found = authenticateUser(emailMap[role], passMap[role]);
    if (found) {
      setSession(found.id);
      setUser(found);
      const hrefMap: Record<UserRole, string> = {
        driver: '/dashboard',
        dispatcher: '/dispatcher',
        admin: '/admin',
      };
      router.push(hrefMap[role]);
    }
  }, [router]);

  const register = useCallback((data: { firstName: string; lastName: string; email: string; phone: string; role: UserRole; password: string }) => {
    const result = registerUser(data);
    if (result.success && result.user) {
      setSession(result.user.id);
      setUser(result.user);
    }
    return { success: result.success, error: result.error };
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
    router.push('/login');
  }, [router]);

  const updateProfile = useCallback((data: Partial<Omit<DBUser, 'id'>>) => {
    if (!user) return false;
    const updated = updateUser(user.id, data);
    if (updated) {
      setUser(updated);
      return true;
    }
    return false;
  }, [user]);

  const updateNotifPrefs = useCallback((prefs: DBUser['notificationPrefs']) => {
    if (!user) return;
    updateUserNotificationPrefs(user.id, prefs);
    setUser({ ...user, notificationPrefs: prefs });
  }, [user]);

  const changePassword = useCallback((currentPassword: string, newPassword: string) => {
    if (!user) return { success: false, error: 'No user' };
    if (user.password !== currentPassword) return { success: false, error: 'settings.password.error' };
    const updated = updateUser(user.id, { password: newPassword });
    if (updated) {
      setUser(updated);
      return { success: true };
    }
    return { success: false, error: 'Unknown error' };
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, loading, login, loginAsRole, register, logout, updateProfile, updateNotifPrefs, changePassword }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
