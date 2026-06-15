import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

const TYPES = ['asset','liability','equity','income','expense'];

export default function ChartOfAccounts() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => api.get('/accounting/accounts/').then(r => r.data),
  });
  const accounts = unwrapList(data);

  const save = useMutation({
    mutationFn: (payload) => api.post('/accounting/accounts/', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['accounts'] });
      toast.success('Account added');
      setOpen(false);
      reset({});
    },
    onError: () => toast.error('Could not add account'),
  });

  const columns = [
    { header: 'Code', accessorKey: 'code', cell: ({ getValue }) => <span className="font-mono text-white">{getValue()}</span> },
    { header: 'Name', accessorKey: 'name' },
    { header: 'Type', accessorKey: 'account_type', cell: ({ getValue }) => <span className="badge-blue">{getValue()}</span> },
    { header: 'Balance', accessorKey: 'balance',
      cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Chart of Accounts" subtitle="General ledger accounts (Kenya SME template)"
        actions={<button type="button" className="btn-primary" onClick={() => { reset({ code:'', name:'', account_type:'expense', description:'' }); setOpen(true); }}>Add account</button>}/>
      <div className="card">
        <DataTable data={accounts} columns={columns} isLoading={isLoading} emptyMessage="No accounts."/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="New account"
        footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-4" onSubmit={handleSubmit(d => save.mutate(d))}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Code *</label>
              <input className={`input ${errors.code?'input-error':''}`} {...register('code',{required:true})}/>
            </div>
            <div>
              <label className="label">Type *</label>
              <select className="input" {...register('account_type',{required:true})}>
                {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          </div>
          <div>
            <label className="label">Name *</label>
            <input className={`input ${errors.name?'input-error':''}`} {...register('name',{required:true})}/>
          </div>
          <div>
            <label className="label">Description</label>
            <input className="input" {...register('description')}/>
          </div>
        </form>
      </Modal>
    </div>
  );
}
