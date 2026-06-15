import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

const emptyLine = () => ({ account: '', description: '', debit: '', credit: '' });

export default function JournalForm() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const navigate = useNavigate();
  const { register, handleSubmit, reset } = useForm();
  const [lines, setLines] = useState([emptyLine(), { account: '', description: '', debit: '', credit: '' }]);

  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => api.get('/accounting/accounts/').then(r => unwrapList(r.data)),
  });

  const { data: entry, isLoading } = useQuery({
    queryKey: ['journal-entry', id],
    queryFn: () => api.get(`/accounting/journal-entries/${id}/`).then(r => r.data),
    enabled: isEdit,
  });

  useEffect(() => {
    if (entry) {
      reset({
        entry_date: entry.entry_date,
        reference: entry.reference || '',
        description: entry.description,
        status: entry.status,
      });
      setLines(entry.lines.map(l => ({
        account: l.account,
        description: l.description || '',
        debit: l.debit || '',
        credit: l.credit || '',
      })));
    } else if (!isEdit) {
      reset({ entry_date: new Date().toISOString().slice(0, 10), reference: '', description: '', status: 'draft' });
    }
  }, [entry, isEdit, reset]);

  const totalDebit = lines.reduce((s, l) => s + Number(l.debit || 0), 0);
  const totalCredit = lines.reduce((s, l) => s + Number(l.credit || 0), 0);
  const balanced = Math.abs(totalDebit - totalCredit) < 0.01;

  const save = useMutation({
    mutationFn: (payload) => isEdit
      ? api.put(`/accounting/journal-entries/${id}/`, payload)
      : api.post('/accounting/journal-entries/', payload),
    onSuccess: () => {
      toast.success(isEdit ? 'Entry updated' : 'Entry created');
      navigate('/accounting/journal-entries');
    },
    onError: (e) => toast.error(e.response?.data?.detail || JSON.stringify(e.response?.data) || 'Save failed'),
  });

  const onSubmit = (data) => {
    if (!balanced) { toast.error('Debits must equal credits'); return; }
    save.mutate({
      ...data,
      lines: lines.filter(l => l.account).map(l => ({
        account: Number(l.account),
        description: l.description,
        debit: Number(l.debit || 0),
        credit: Number(l.credit || 0),
      })),
    });
  };

  if (isEdit && isLoading) return (
    <div className="flex justify-center py-20">
      <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
    </div>
  );

  return (
    <div className="space-y-6 max-w-4xl">
      <PageHeader title={isEdit ? 'Edit journal entry' : 'New journal entry'}/>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="card grid grid-cols-2 gap-4">
          <div>
            <label className="label">Date</label>
            <input type="date" className="input" {...register('entry_date', { required: true })}/>
          </div>
          <div>
            <label className="label">Reference</label>
            <input className="input" {...register('reference')}/>
          </div>
          <div className="col-span-2">
            <label className="label">Description *</label>
            <input className="input" {...register('description', { required: true })}/>
          </div>
        </div>
        <div className="card">
          <div className="flex justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-300">Lines</h3>
            <button type="button" className="btn-ghost text-xs" onClick={() => setLines([...lines, emptyLine()])}>
              <PlusIcon className="w-4 h-4"/> Add line
            </button>
          </div>
          {lines.map((line, i) => (
            <div key={i} className="grid grid-cols-12 gap-2 mb-2 items-end">
              <div className="col-span-4">
                <select className="input" value={line.account}
                  onChange={e => { const n = [...lines]; n[i].account = e.target.value; setLines(n); }}>
                  <option value="">Account</option>
                  {(accounts || []).map(a => <option key={a.id} value={a.id}>{a.code} — {a.name}</option>)}
                </select>
              </div>
              <div className="col-span-3">
                <input className="input" placeholder="Memo" value={line.description}
                  onChange={e => { const n = [...lines]; n[i].description = e.target.value; setLines(n); }}/>
              </div>
              <div className="col-span-2">
                <input type="number" min="0" step="0.01" className="input" placeholder="Debit" value={line.debit}
                  onChange={e => { const n = [...lines]; n[i].debit = e.target.value; n[i].credit = ''; setLines(n); }}/>
              </div>
              <div className="col-span-2">
                <input type="number" min="0" step="0.01" className="input" placeholder="Credit" value={line.credit}
                  onChange={e => { const n = [...lines]; n[i].credit = e.target.value; n[i].debit = ''; setLines(n); }}/>
              </div>
              <div className="col-span-1">
                {lines.length > 2 && (
                  <button type="button" onClick={() => setLines(lines.filter((_, j) => j !== i))} className="text-red-400">
                    <TrashIcon className="w-4 h-4"/>
                  </button>
                )}
              </div>
            </div>
          ))}
          <div className={`mt-4 text-sm text-right ${balanced ? 'text-green-400' : 'text-red-400'}`}>
            Debit {formatCurrency(totalDebit)} · Credit {formatCurrency(totalCredit)}
            {!balanced && ' — Not balanced'}
          </div>
        </div>
        <div className="flex gap-3">
          <button type="submit" className="btn-primary" disabled={!balanced || save.isPending}>Save</button>
          <button type="button" className="btn-secondary" onClick={() => navigate('/accounting/journal-entries')}>Cancel</button>
        </div>
      </form>
    </div>
  );
}
