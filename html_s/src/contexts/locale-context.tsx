'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Locale, t as translate } from '@/lib/i18n';
import { getSettings, saveSettings } from '@/lib/db';

interface LocaleContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

const LocaleContext = createContext<LocaleContextType>({
  locale: 'ru',
  setLocale: () => {},
  t: (key: string) => key,
});

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>('ru');

  useEffect(() => {
    const settings = getSettings();
    setLocaleState(settings.locale);
  }, []);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    saveSettings({ locale: l });
    document.documentElement.lang = l;
  }, []);

  const t = useCallback((key: string) => translate(key, locale), [locale]);

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  );
}

export function useLocale(): LocaleContextType {
  return useContext(LocaleContext);
}
