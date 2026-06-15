import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Projects() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({ queryKey: ['projects'], queryFn: () => api.get('/projects/projects/').then(r => r.data) });

  const save = useMutation({
    mutationFn: d => api.post('/projects/projects/', { ...d, budget: Number(d.budget || 0) }),
    onSuccess: (res) => { qc.invalidateQueries({ queryKey: ['projects'] }); toast.success('Project created'); setOpen(false); navigate(`/projects/${res.data.id}`); },
  });

  const columns = [
    { header: 'Code', accessorKey: 'code' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'Client', accessorKey: 'client_name', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Budget', accessorKey: 'budget', cell: ({ getValue }) => formatCurrency(getValue()) },
    { header: 'Spent', accessorKey: 'total_costs', cell: ({ getValue }) => formatCurrency(getValue()) },
    { header: 'Remaining', accessorKey: 'budget_remaining', cell: ({ getValue }) => <span className={Number(getValue()) < 0 ? 'text-red-400' : ''}>{formatCurrency(getValue())}</span> },
    { header: 'Status', accessorKey: 'status', cell: ({ getValue }) => <span className={statusBadge(getValue())}>{getValue()}</span> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Projects" subtitle="Track budgets and job costs"
        actions={<button type="button" className="btn-primary" onClick={() => { reset({ status: 'in_progress' }); setOpen(true); }}>New project</button>}/>
      <div className="card"><DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading} onRowClick={r => navigate(`/projects/${r.id}`)}/></div>
      <Modal open={open} onClose={() => setOpen(false)} title="New project" footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Create</button>}>
        <form className="space-y-3">
          <input className="input" placeholder="Code *" {...register('code', { required: true })}/>
          <input className="input" placeholder="Name *" {...register('name', { required: true })}/>
          <input className="input" placeholder="Client" {...register('client_name')}/>
          <input type="number" className="input" placeholder="Budget" {...register('budget')}/>
        </form>
      </Modal>
    </div>
  );
}
