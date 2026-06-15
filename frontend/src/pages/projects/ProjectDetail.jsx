import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function ProjectDetail() {
  const { id } = useParams();
  const { data: p, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: () => api.get(`/projects/projects/${id}/`).then(r => r.data),
  });

  if (isLoading) return <div className="flex justify-center py-20"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/></div>;
  if (!p) return null;

  return (
    <div className="space-y-6">
      <PageHeader title={p.name} subtitle={p.code}
        actions={<Link to={`/projects/${id}/costing`} className="btn-primary">Job costing</Link>}/>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card-sm"><p className="text-xs text-slate-500">Budget</p><p className="text-lg font-mono text-white">{formatCurrency(p.budget)}</p></div>
        <div className="card-sm"><p className="text-xs text-slate-500">Spent</p><p className="text-lg font-mono text-white">{formatCurrency(p.total_costs)}</p></div>
        <div className="card-sm"><p className="text-xs text-slate-500">Remaining</p><p className={`text-lg font-mono ${Number(p.budget_remaining) < 0 ? 'text-red-400' : 'text-green-400'}`}>{formatCurrency(p.budget_remaining)}</p></div>
        <div className="card-sm"><p className="text-xs text-slate-500">Status</p><p><span className={statusBadge(p.status)}>{p.status}</span></p></div>
      </div>
      {p.notes && <div className="card text-slate-400 text-sm">{p.notes}</div>}
      <div className="card">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Recent costs</h3>
        {(p.costs || []).length === 0 ? <p className="text-slate-500 text-sm">No costs recorded — add via Job costing.</p> : (
          <table className="w-full text-sm">
            {(p.costs || []).map(c => (
              <tr key={c.id} className="border-b border-surface-border">
                <td className="py-2">{c.description}</td>
                <td className="py-2 text-slate-400">{c.category}</td>
                <td className="py-2 text-right font-mono">{formatCurrency(c.amount)}</td>
              </tr>
            ))}
          </table>
        )}
      </div>
      <Link to="/projects" className="text-brand-400 text-sm">← Projects</Link>
    </div>
  );
}
