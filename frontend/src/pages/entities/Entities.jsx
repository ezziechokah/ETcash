import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Entities() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['entities'],
    queryFn: () => api.get('/entities/list/').then(r => r.data),
  });

  const save = useMutation({
    mutationFn: d => api.post('/entities/list/', d),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['entities'] }); toast.success('Entity added'); setOpen(false); reset({}); },
  });

  const columns = [
    { header: 'Code', accessorKey: 'code' },
    { header: 'Name', accessorKey: 'name' },
    { header: 'KRA PIN', accessorKey: 'kra_pin', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Currency', accessorKey: 'currency' },
    { header: 'Default', accessorKey: 'is_default', cell: ({ getValue }) => getValue() ? 'Yes' : '—' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Entities" subtitle="Legal entities in your group"
        actions={<button type="button" className="btn-primary" onClick={() => { reset({ currency: 'KES' }); setOpen(true); }}>Add entity</button>}/>
      <div className="card"><DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/></div>
      <Modal open={open} onClose={() => setOpen(false)} title="New entity" footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <input className="input" placeholder="Code *" {...register('code', { required: true })}/>
          <input className="input" placeholder="Name *" {...register('name', { required: true })}/>
          <input className="input" placeholder="KRA PIN" {...register('kra_pin')}/>
        </form>
      </Modal>
    </div>
  );
}
