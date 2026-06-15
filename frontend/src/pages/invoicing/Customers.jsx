import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Customers() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [edit, setEdit] = useState(null);
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['customers'],
    queryFn: () => api.get('/invoicing/customers/').then(r => r.data),
  });
  const customers = unwrapList(data);

  const save = useMutation({
    mutationFn: (payload) => edit
      ? api.put(`/invoicing/customers/${edit.id}/`, payload)
      : api.post('/invoicing/customers/', payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['customers'] });
      toast.success(edit ? 'Customer updated' : 'Customer added');
      setOpen(false);
      setEdit(null);
      reset({});
    },
    onError: () => toast.error('Could not save customer'),
  });

  const openCreate = () => { setEdit(null); reset({ name: '', email: '', phone: '', kra_pin: '' }); setOpen(true); };
  const openEdit = (row) => { setEdit(row); reset(row); setOpen(true); };

  const columns = [
    { header: 'Name', accessorKey: 'name' },
    { header: 'Email', accessorKey: 'email', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Phone', accessorKey: 'phone', cell: ({ getValue }) => getValue() || '—' },
    { header: 'KRA PIN', accessorKey: 'kra_pin', cell: ({ getValue }) => getValue() || '—' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Customers" subtitle="Clients for invoicing and AR"
        actions={<button type="button" className="btn-primary" onClick={openCreate}>Add customer</button>}/>
      <div className="card">
        <DataTable data={customers} columns={columns} isLoading={isLoading}
          onRowClick={openEdit} emptyMessage="No customers yet."/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title={edit ? 'Edit customer' : 'New customer'}
        footer={<>
          <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>Cancel</button>
          <button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>
            {save.isPending ? 'Saving…' : 'Save'}
          </button>
        </>}>
        <form className="space-y-4" onSubmit={handleSubmit(d => save.mutate(d))}>
          <div>
            <label className="label">Name *</label>
            <input className={`input ${errors.name ? 'input-error' : ''}`} {...register('name', { required: true })}/>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Email</label>
              <input type="email" className="input" {...register('email')}/>
            </div>
            <div>
              <label className="label">Phone</label>
              <input className="input" {...register('phone')}/>
            </div>
          </div>
          <div>
            <label className="label">KRA PIN</label>
            <input className="input" placeholder="P051234567X" {...register('kra_pin')}/>
          </div>
        </form>
      </Modal>
    </div>
  );
}
