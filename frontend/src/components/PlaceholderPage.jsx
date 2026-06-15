import React from 'react';
import PageHeader from './PageHeader.jsx';
import { WrenchScrewdriverIcon } from '@heroicons/react/24/outline';

export default function PlaceholderPage({ title, description }) {
  return (
    <div className="space-y-6">
      <PageHeader title={title} subtitle={description} />
      <div className="card flex flex-col items-center justify-center py-20 text-center">
        <div className="w-14 h-14 rounded-2xl bg-brand-600/20 flex items-center justify-center mb-4">
          <WrenchScrewdriverIcon className="w-7 h-7 text-brand-400" />
        </div>
        <p className="text-slate-300 font-medium">Module scaffolded</p>
        <p className="text-slate-500 text-sm mt-2 max-w-md">
          Navigation and API wiring are in place. Full screens for this area are next on the build list.
        </p>
      </div>
    </div>
  );
}
