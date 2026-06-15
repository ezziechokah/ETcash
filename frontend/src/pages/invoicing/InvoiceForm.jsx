import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { TAX_RATES } from '../../utils/constants.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

const emptyLine = () => ({ description: '', quantity: 1, unit_price: 0, tax_rate: 16 });

function lineTotal(line) {
  const sub = Number(line.quantity || 0) * Number(line.unit_price || 0);
  const tax = sub * (Number(line.tax_rate || 0) / 100);
  return sub + tax;
}

export default function InvoiceForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { register, handleSubmit, reset, watch } = useForm();
  const [lines, setLines] = useState([emptyLine()]);

  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: () => api.get('/invoicing/customers/').then(r => unwrapList(r.data)),
  });

  const { data: invoice, isLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => api.get(`/invoicing/invoices/${id}/`).then(r => r.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (invoice) {
      reset({
        customer: invoice.customer,
        issue_date: invoice.issue_date,
        due_date: invoice.due_date,
        status: invoice.status,
        notes: invoice.notes || '',
      });
      setLines(invoice.lines?.length ? invoice.lines : [emptyLine()]);
    } else if (!isEdit) {
      const today = new Date().toISOString().slice(0, 10);
      reset({ issue_date: today, due_date: today, status: 'draft', notes: '' });
    }
  }, [invoice, isEdit, reset]);

  const save = useMutation({
    mutationFn: (payload) => isEdit
      ? api.put(`/invoicing/invoices/${id}/`, payload)
      : api.post('/invoicing/invoices/', payload),
    onSuccess: (res) => {
      toast.success(isEdit ? 'Invoice updated' : 'Invoice created');
      navigate(`/invoicing/invoices/${res.data.id}`);
    },
    onError: (err) => toast.error(err.response?.data?.detail || 'Could not save invoice'),
  });

  const onSubmit = (data) => {
    if (!lines.length || !lines[0].description) {
      toast.error('Add at least one line item');
      return;
    }
    save.mutate({
      ...data,
      customer: Number(data.customer),
      lines: lines.map(l => ({
        description: l.description,
        quantity: Number(l.quantity),
        unit_price: Number(l.unit_price),
        tax_rate: Number(l.tax_rate),
      })),
    });
  };

  const grandTotal = lines.reduce((s, l) => s + lineTotal(l), 0);

  if (isEdit && isLoading) return (
    <div className="flex justify-center py-20">
      <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
    </div>
  );

  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader title={isEdit ? 'Edit invoice' : 'New invoice'} subtitle="VAT 16% applied per line by default"/>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="card grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="label">Customer *</label>
            <select className="input" {...register('customer', { required: true })}>
              <option value="">Select customer</option>
              {(customers || []).map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="label">Issue date</label>
            <input type="date" className="input" {...register('issue_date', { required: true })}/>
          </div>
          <div>
            <label className="label">Due date</label>
            <input type="date" className="input" {...register('due_date', { required: true })}/>
          </div>
          <div>
            <label className="label">Status</label>
            <select className="input" {...register('status')}>
              {['draft','sent','partial','paid','overdue','void'].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="col-span-2">
            <label className="label">Notes</label>
            <textarea className="input" rows={2} {...register('notes')}/>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-300">Line items</h3>
            <button type="button" className="btn-ghost text-xs" onClick={() => setLines([...lines, emptyLine()])}>
              <PlusIcon className="w-4 h-4"/> Add line
            </button>
          </div>
          <div className="space-y-3">
            {lines.map((line, i) => (
              <div key={i} className="grid grid-cols-12 gap-2 items-end border-b border-surface-border pb-3">
                <div className="col-span-5">
                  <label className="label">Description</label>
                  <input className="input" value={line.description}
                    onChange={e => { const n = [...lines]; n[i].description = e.target.value; setLines(n); }}/>
                </div>
                <div className="col-span-2">
                  <label className="label">Qty</label>
                  <input type="number" min="0" step="0.01" className="input" value={line.quantity}
                    onChange={e => { const n = [...lines]; n[i].quantity = e.target.value; setLines(n); }}/>
                </div>
                <div className="col-span-2">
                  <label className="label">Unit price</label>
                  <input type="number" min="0" step="0.01" className="input" value={line.unit_price}
                    onChange={e => { const n = [...lines]; n[i].unit_price = e.target.value; setLines(n); }}/>
                </div>
                <div className="col-span-2">
                  <label className="label">Tax</label>
                  <select className="input" value={line.tax_rate}
                    onChange={e => { const n = [...lines]; n[i].tax_rate = e.target.value; setLines(n); }}>
                    {TAX_RATES.filter(t => t.value === 0 || t.value === 16).map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div className="col-span-1 flex flex-col items-end gap-1">
                  <span className="text-xs font-mono text-slate-300">{formatCurrency(lineTotal(line))}</span>
                  {lines.length > 1 && (
                    <button type="button" className="text-red-400 hover:text-red-300" onClick={() => setLines(lines.filter((_, j) => j !== i))}>
                      <TrashIcon className="w-4 h-4"/>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-end mt-4 text-lg font-semibold text-white">
            Total: <span className="font-mono ml-2">{formatCurrency(grandTotal)}</span>
          </div>
        </div>

        <div className="flex gap-3">
          <button type="submit" className="btn-primary" disabled={save.isPending}>
            {save.isPending ? 'Saving…' : isEdit ? 'Update invoice' : 'Create invoice'}
          </button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/invoicing/invoices')}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
