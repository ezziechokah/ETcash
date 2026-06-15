import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatDate } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function StockMovements() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data: items } = useQuery({ queryKey: ['items'], queryFn: () => api.get('/inventory/items/').then(r => unwrapList(r.data)) });
  const { data, isLoading } = useQuery({ queryKey: ['movements'], queryFn: () => api.get('/inventory/movements/').then(r => r.data) });

  const save = useMutation({
    mutationFn: d => api.post('/inventory/movements/', { ...d, item: Number(d.item), quantity: Number(d.quantity) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['movements', 'items'] }); toast.success('Movement recorded'); setOpen(false); reset({}); },
  });

  const columns = [
    { header: 'Date', accessorKey: 'movement_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Item', accessorKey: 'item_name' },
    { header: 'Type', accessorKey: 'movement_type' },
    { header: 'Qty', accessorKey: 'quantity' },
    { header: 'Ref', accessorKey: 'reference' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Stock Movements" actions={<button type="button" className="btn-primary" onClick={() => { reset({ movement_type: 'in', movement_date: new Date().toISOString().slice(0, 10) }); setOpen(true); }}>Record movement</button>}/>
      <div className="card"><DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/></div>
      <Modal open={open} onClose={() => setOpen(false)} title="Stock movement" footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <select className="input" {...register('item', { required: true })}><option value="">Item</option>{(items||[]).map(i => <option key={i.id} value={i.id}>{i.sku} — {i.name}</option>)}</select>
          <input type="date" className="input" {...register('movement_date', { required: true })}/>
          <select className="input" {...register('movement_type')}><option value="in">Stock in</option><option value="out">Stock out</option><option value="adjust">Adjustment</option></select>
          <input type="number" className="input" placeholder="Quantity" {...register('quantity', { required: true })}/>
          <input className="input" placeholder="Reference" {...register('reference')}/>
        </form>
      </Modal>
    </div>
  );
}
