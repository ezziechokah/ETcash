import React, { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { useAuthStore } from '../../store/authStore.js';
import { MONTHS } from '../../utils/constants.js';
import PageHeader from '../../components/PageHeader.jsx';

const MODE_LABEL = { freelancer: 'Freelancer', sme: 'SME', multi_entity: 'Multi-Entity' };

export default function Settings() {
  const qc = useQueryClient();
  const { setCompany, company } = useAuthStore();
  const { register, handleSubmit, reset } = useForm();

  const { data } = useQuery({
    queryKey: ['company'],
    queryFn: () => api.get('/core/company/').then(r => r.data),
  });

  useEffect(() => { if (data?.id) reset(data); }, [data, reset]);

  const save = useMutation({
    mutationFn: d => api.patch('/core/company/', d),
    onSuccess: (res) => {
      setCompany(res.data);
      qc.invalidateQueries({ queryKey: ['company'] });
      toast.success('Settings saved');
    },
    onError: () => toast.error('Could not save'),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Settings" subtitle="Company profile and preferences"/>
      <form onSubmit={handleSubmit(d => save.mutate(d))} className="card space-y-4">
        <div>
          <label className="label">Company name</label>
          <input className="input" {...register('name', { required: true })}/>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label">KRA PIN</label>
            <input className="input" {...register('kra_pin')}/>
          </div>
          <div>
            <label className="label">Phone</label>
            <input className="input" {...register('phone')}/>
          </div>
        </div>
        <div>
          <label className="label">Financial year starts</label>
          <select className="input" {...register('fy_start_month')}>
            {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Installation mode</label>
          <p className="text-sm text-slate-400 mt-1">{MODE_LABEL[company?.mode] || data?.mode} — set at install time</p>
        </div>
        <button type="submit" className="btn-primary" disabled={save.isPending}>{save.isPending ? 'Saving…' : 'Save changes'}</button>
      </form>
    </div>
  );
}
