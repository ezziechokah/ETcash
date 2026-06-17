import { useEffect } from 'react';
import { useThemeStore } from '../store/themeStore.js';

export function useThemeInit() {
  const syncTheme = useThemeStore(s => s.syncTheme);
  const preference = useThemeStore(s => s.preference);

  useEffect(() => {
    syncTheme();
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const onChange = () => {
      if (useThemeStore.getState().preference === 'system') {
        useThemeStore.getState().syncTheme();
      }
    };
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, [syncTheme, preference]);
}

export function useTheme() {
  const { preference, resolved, setPreference, syncTheme } = useThemeStore();
  return { preference, resolved, setPreference, syncTheme };
}
