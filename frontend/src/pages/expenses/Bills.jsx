import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, formatDate, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Bills() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data: vendors } = useQuery({
    queryKey: ['vendors'],
    queryFn: () => api.get('/expenses/vendors/').then(r => unwrapList(r.data)),
  });
  const { data, isLoading } = useQuery({
    queryKey: ['bills'],
    queryFn: () => api.get('/expenses/bills/').then(r => r.data),
  });

  const save = useMutation({
    mutationFn: (payload) => api.post('/expenses/bills/', {
      ...payload,
      vendor: Number(payload.vendor),
      subtotal: Number(payload.subtotal),
      tax_amount: Number(payload.tax_amount || 0),
      total_amount: Number(payload.total_amount),
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['bills'] }); toast.success('Bill added'); setOpen(false); reset({}); },
    onError: () => toast.error('Could not save bill'),
  });

  const columns = [
    { header: 'Bill #', accessorKey: 'bill_number' },
    { header: 'Vendor', accessorKey: 'vendor_name' },
    { header: 'Due', accessorKey: 'due_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Total', accessorKey: 'total_amount', cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
    { header: 'Status', accessorKey: 'status', cell: ({ getValue }) => <span className={statusBadge(getValue())}>{getValue()}</span> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Bills" subtitle="Vendor bills (AP)"
        actions={<button type="button" className="btn-primary" onClick={() => { reset({ status: 'open' }); setOpen(true); }}>Add bill</button>}/>
      <div className="card">
        <DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="New bill"
        footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <select className="input" {...register('vendor', { required: true })}>
            <option value="">Vendor</option>
            {(vendors || []).map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
          <input className="input" placeholder="Bill number" {...register('bill_number', { required: true })}/>
          <div className="grid grid-cols-2 gap-2">
            <input type="date" className="input" {...register('issue_date', { required: true })}/>
            <input type="date" className="input" {...register('due_date', { required: true })}/>
          </div>
          <input type="number" className="input" placeholder="Subtotal" {...register('subtotal', { required: true })}/>
          <input type="number" className="input" placeholder="VAT amount" {...register('tax_amount')}/>
          <input type="number" className="input" placeholder="Total" {...register('total_amount', { required: true })}/>
        </form>
      </Modal>
    </div>
  );
}
