import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { TAX_RATES, PAYMENT_METHODS } from '../../utils/constants.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function ExpenseForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { register, handleSubmit, reset, watch } = useForm();
  const amount = watch('amount');
  const taxRate = watch('tax_rate');

  const { data: vendors } = useQuery({
    queryKey: ['vendors'],
    queryFn: () => api.get('/expenses/vendors/').then(r => unwrapList(r.data)),
  });

  const { data: expense, isLoading } = useQuery({
    queryKey: ['expense', id],
    queryFn: () => api.get(`/expenses/expenses/${id}/`).then(r => r.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (expense) reset(expense);
    else reset({
      expense_date: new Date().toISOString().slice(0, 10),
      tax_rate: 16,
      payment_method: 'mpesa',
      amount: '',
      description: '',
      category: '',
    });
  }, [expense, reset]);

  const taxPreview = amount && taxRate
    ? (Number(amount) * Number(taxRate) / 100).toFixed(2)
    : '0.00';

  const save = useMutation({
    mutationFn: (payload) => isEdit
      ? api.put(`/expenses/expenses/${id}/`, payload)
      : api.post('/expenses/expenses/', payload),
    onSuccess: () => { toast.success('Expense saved'); navigate('/expenses/list'); },
    onError: () => toast.error('Could not save expense'),
  });

  const onSubmit = (data) => {
    save.mutate({
      ...data,
      vendor: data.vendor ? Number(data.vendor) : null,
      amount: Number(data.amount),
      tax_rate: Number(data.tax_rate),
    });
  };

  if (isEdit && isLoading) return (
    <div className="flex justify-center py-20">
      <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
    </div>
  );

  return (
    <div className="space-y-6 max-w-xl">
      <PageHeader title={isEdit ? 'Edit expense' : 'Record expense'}/>
      <form onSubmit={handleSubmit(onSubmit)} className="card space-y-4">
        <div>
          <label className="label">Date</label>
          <input type="date" className="input" {...register('expense_date', { required: true })}/>
        </div>
        <div>
          <label className="label">Description *</label>
          <input className="input" {...register('description', { required: true })}/>
        </div>
        <div>
          <label className="label">Vendor</label>
          <select className="input" {...register('vendor')}>
            <option value="">None</option>
            {(vendors || []).map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Amount (excl. tax) *</label>
            <input type="number" step="0.01" className="input" {...register('amount', { required: true })}/>
          </div>
          <div>
            <label className="label">Tax rate</label>
            <select className="input" {...register('tax_rate')}>
              {TAX_RATES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
            <p className="text-xs text-slate-500 mt-1">Tax amount: KES {taxPreview}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">Category</label>
            <input className="input" {...register('category')}/>
          </div>
          <div>
            <label className="label">Payment</label>
            <select className="input" {...register('payment_method')}>
              {PAYMENT_METHODS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="label">Reference</label>
          <input className="input" placeholder="M-Pesa code, receipt #" {...register('reference')}/>
        </div>
        <div className="flex gap-3 pt-2">
          <button type="submit" className="btn-primary" disabled={save.isPending}>Save</button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/expenses/list')}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
