import React from 'react';
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { useTheme } from '../hooks/useTheme.js';

const OPTIONS = [
  { value: 'light', label: 'Light', icon: SunIcon },
  { value: 'dark', label: 'Dark', icon: MoonIcon },
  { value: 'system', label: 'System', icon: ComputerDesktopIcon },
];

export default function ThemeToggle({ compact = false }) {
  const { preference, setPreference, syncTheme } = useTheme();

  const select = (value) => {
    setPreference(value);
    queueMicrotask(() => syncTheme());
  };

  if (compact) {
    const current = OPTIONS.find(o => o.value === preference) || OPTIONS[2];
    const next = OPTIONS[(OPTIONS.findIndex(o => o.value === preference) + 1) % OPTIONS.length];
    const Icon = current.icon;
    return (
      <button
        type="button"
        onClick={() => select(next.value)}
        className="text-fg-muted hover:text-fg-secondary transition-colors p-1 rounded-lg hover:bg-surface-card"
        title={`Theme: ${current.label} (click for ${next.label})`}
        aria-label={`Theme: ${current.label}`}
      >
        <Icon className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="inline-flex rounded-lg border border-surface-border p-1 bg-surface-card gap-1">
      {OPTIONS.map(({ value, label, icon: Icon }) => (
        <button
          key={value}
          type="button"
          onClick={() => select(value)}
          className={clsx(
            'flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
            preference === value
              ? 'bg-brand-600 text-white shadow-sm'
              : 'text-fg-muted hover:text-fg-secondary hover:bg-surface-border/50'
          )}
        >
          <Icon className="w-4 h-4" />
          {label}
        </button>
      ))}
    </div>
  );
}
