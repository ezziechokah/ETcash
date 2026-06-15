import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function BankAccounts() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['bank-accounts'],
    queryFn: () => api.get('/banking/accounts/').then(r => r.data),
  });

  const save = useMutation({
    mutationFn: (payload) => api.post('/banking/accounts/', { ...payload, opening_balance: Number(payload.opening_balance || 0) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['bank-accounts'] }); toast.success('Account added'); setOpen(false); reset({}); },
    onError: () => toast.error('Save failed'),
  });

  const columns = [
    { header: 'Name', accessorKey: 'name', cell: ({ row, getValue }) => (
      <Link to={`/banking/accounts?id=${row.original.id}`} className="text-brand-400 hover:text-brand-300">{getValue()}</Link>
    )},
    { header: 'Bank', accessorKey: 'bank_name', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Account #', accessorKey: 'account_number', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Balance', accessorKey: 'balance', cell: ({ getValue }) => <span className="font-mono text-white">{formatCurrency(getValue())}</span> },
    { header: 'Unreconciled', accessorKey: 'unreconciled_count' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Bank Accounts" subtitle="Cash and bank balances"
        actions={<button type="button" className="btn-primary" onClick={() => { reset({ currency: 'KES', opening_balance: 0 }); setOpen(true); }}>Add account</button>}/>
      <div className="card">
        <DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="New bank account"
        footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <input className="input" placeholder="Account name *" {...register('name', { required: true })}/>
          <input className="input" placeholder="Bank name" {...register('bank_name')}/>
          <input className="input" placeholder="Account number" {...register('account_number')}/>
          <input type="number" className="input" placeholder="Opening balance" {...register('opening_balance')}/>
        </form>
      </Modal>
    </div>
  );
}
