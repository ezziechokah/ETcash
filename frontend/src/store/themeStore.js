import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/** @typedef {'light' | 'dark' | 'system'} ThemePreference */

export const useThemeStore = create(persist(
  (set, get) => ({
    /** @type {ThemePreference} */
    preference: 'system',
    /** Resolved theme applied to the DOM — 'light' or 'dark' */
    resolved: 'dark',

    setPreference: (preference) => {
      set({ preference });
      queueMicrotask(() => get().syncTheme());
    },

    applyResolved: (resolved) => {
      set({ resolved });
      const root = document.documentElement;
      root.classList.toggle('dark', resolved === 'dark');
      root.style.colorScheme = resolved;
    },

    resolveTheme: () => {
      const { preference } = get();
      if (preference === 'system') {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      return preference;
    },

    syncTheme: () => {
      get().applyResolved(get().resolveTheme());
    },
  }),
  { name: 'etcash-theme', partialize: s => ({ preference: s.preference }) }
));
