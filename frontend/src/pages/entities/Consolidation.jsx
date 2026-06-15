import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import StatCard from '../../components/StatCard.jsx';
import { ChartBarIcon } from '@heroicons/react/24/outline';

export default function Consolidation() {
  const { data, isLoading } = useQuery({
    queryKey: ['consolidation'],
    queryFn: () => api.get('/entities/consolidation/').then(r => r.data),
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Consolidation" subtitle="Group-level financial summary"/>
      {isLoading ? <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/></div> : data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <StatCard title="Group revenue" value={formatCurrency(data.total_revenue)} icon={ChartBarIcon} color="green"/>
            <StatCard title="Group expenses" value={formatCurrency(data.total_expenses)} icon={ChartBarIcon} color="red"/>
            <StatCard title="Consolidated net" value={formatCurrency(data.consolidated_net)} icon={ChartBarIcon} color="purple"/>
          </div>
          <div className="card overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="table-header border-b border-surface-border">
                  <th className="text-left py-2">Entity</th>
                  <th className="text-right py-2">Revenue</th>
                  <th className="text-right py-2">Expenses</th>
                  <th className="text-right py-2">Net</th>
                </tr>
              </thead>
              <tbody>
                {(data.entities || []).map(e => (
                  <tr key={e.entity_id} className="border-b border-surface-border">
                    <td className="py-2"><span className="font-mono text-slate-500 mr-2">{e.entity_code}</span>{e.entity_name}</td>
                    <td className="py-2 text-right font-mono">{formatCurrency(e.revenue)}</td>
                    <td className="py-2 text-right font-mono">{formatCurrency(e.expenses)}</td>
                    <td className="py-2 text-right font-mono text-white">{formatCurrency(e.net)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
