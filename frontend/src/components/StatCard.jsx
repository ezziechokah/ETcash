import React from 'react';
import { clsx } from 'clsx';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

const colors = {
  blue:   'bg-blue-900/30 text-blue-400',
  green:  'bg-green-900/30 text-green-400',
  red:    'bg-red-900/30 text-red-400',
  yellow: 'bg-yellow-900/30 text-yellow-400',
  purple: 'bg-purple-900/30 text-purple-400',
};

export default function StatCard({ title, value, subtitle, trend, trendLabel, icon:Icon, color='blue' }) {
  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-sm text-slate-400">{title}</p>
          <p className="text-2xl font-bold text-white mt-1 truncate">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
          {trend !== undefined && (
            <div className={clsx('flex items-center gap-1 mt-2 text-xs font-medium', trend>=0?'text-green-400':'text-red-400')}>
              {trend>=0 ? <ArrowUpIcon className="w-3 h-3"/> : <ArrowDownIcon className="w-3 h-3"/>}
              <span>{Math.abs(trend)}% {trendLabel}</span>
            </div>
          )}
        </div>
        {Icon && <div className={clsx('p-3 rounded-xl flex-shrink-0 ml-4', colors[color])}><Icon className="w-6 h-6"/></div>}
      </div>
    </div>
  );
}
