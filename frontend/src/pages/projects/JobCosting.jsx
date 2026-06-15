import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function JobCosting() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { register, handleSubmit, reset } = useForm();

  const { data: p } = useQuery({ queryKey: ['project', id], queryFn: () => api.get(`/projects/projects/${id}/`).then(r => r.data) });

  const save = useMutation({
    mutationFn: d => api.post('/projects/costs/', { ...d, project: Number(id), amount: Number(d.amount) }),
    onSuccess: () => { toast.success('Cost added'); reset({}); qc.invalidateQueries({ queryKey: ['project', id] }); },
  });

  return (
    <div className="space-y-6 max-w-xl">
      <PageHeader title="Job costing" subtitle={p?.name}/>
      <form onSubmit={handleSubmit(d => save.mutate(d))} className="card space-y-3">
        <input type="date" className="input" {...register('cost_date', { required: true })} defaultValue={new Date().toISOString().slice(0, 10)}/>
        <input className="input" placeholder="Category" {...register('category')}/>
        <input className="input" placeholder="Description *" {...register('description', { required: true })}/>
        <input type="number" className="input" placeholder="Amount *" {...register('amount', { required: true })}/>
        <button type="submit" className="btn-primary">Add cost</button>
      </form>
      {p && <p className="text-sm text-slate-400">Total spent: <span className="font-mono text-white">{formatCurrency(p.total_costs)}</span> / {formatCurrency(p.budget)}</p>}
    </div>
  );
}
