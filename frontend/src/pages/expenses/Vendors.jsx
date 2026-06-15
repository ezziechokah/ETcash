import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Vendors() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState(null);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['vendors'],
    queryFn: () => api.get('/expenses/vendors/').then(r => r.data),
  });

  const save = useMutation({
    mutationFn: (payload) => edit
      ? api.put(`/expenses/vendors/${edit.id}/`, payload)
      : api.post('/expenses/vendors/', payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['vendors'] }); toast.success('Saved'); setOpen(false); setEdit(null); reset({}); },
    onError: () => toast.error('Save failed'),
  });

  const columns = [
    { header: 'Name', accessorKey: 'name' },
    { header: 'Email', accessorKey: 'email', cell: ({ getValue }) => getValue() || '—' },
    { header: 'KRA PIN', accessorKey: 'kra_pin', cell: ({ getValue }) => getValue() || '—' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Vendors" actions={<button type="button" className="btn-primary" onClick={() => { setEdit(null); reset({}); setOpen(true); }}>Add vendor</button>}/>
      <div className="card">
        <DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading} onRowClick={row => { setEdit(row); reset(row); setOpen(true); }}/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title={edit ? 'Edit vendor' : 'New vendor'}
        footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <input className="input" placeholder="Name *" {...register('name', { required: true })}/>
          <input className="input" placeholder="Email" {...register('email')}/>
          <input className="input" placeholder="KRA PIN" {...register('kra_pin')}/>
        </form>
      </Modal>
    </div>
  );
}
