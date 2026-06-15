import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Inventory() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: () => api.get('/inventory/items/').then(r => r.data),
  });

  const save = useMutation({
    mutationFn: d => api.post('/inventory/items/', { ...d, quantity_on_hand: Number(d.quantity_on_hand || 0), unit_cost: Number(d.unit_cost || 0), selling_price: Number(d.selling_price || 0), reorder_level: Number(d.reorder_level || 0) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['items'] }); toast.success('Item added'); setOpen(false); reset({}); },
    onError: () => toast.error('Save failed'),
  });

  const columns = [
    { header: 'SKU', accessorKey: 'sku', cell: ({ getValue }) => <span className="font-mono text-white">{getValue()}</span> },
    { header: 'Name', accessorKey: 'name' },
    { header: 'On hand', accessorKey: 'quantity_on_hand' },
    { header: 'Unit cost', accessorKey: 'unit_cost', cell: ({ getValue }) => formatCurrency(getValue()) },
    { header: 'Stock value', accessorKey: 'stock_value', cell: ({ getValue }) => formatCurrency(getValue()) },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Inventory" subtitle="Items, stock levels, and valuation"
        actions={<>
          <Link to="/inventory/movements" className="btn-secondary">Movements</Link>
          <button type="button" className="btn-primary" onClick={() => { reset({ unit: 'each' }); setOpen(true); }}>Add item</button>
        </>}/>
      <div className="card">
        <DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}
          onRowClick={row => navigate(`/inventory/items/${row.id}`)}/>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="New item"
        footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="grid grid-cols-2 gap-3">
          <input className="input" placeholder="SKU *" {...register('sku', { required: true })}/>
          <input className="input col-span-2" placeholder="Name *" {...register('name', { required: true })}/>
          <input type="number" className="input" placeholder="Qty on hand" {...register('quantity_on_hand')}/>
          <input type="number" className="input" placeholder="Unit cost" {...register('unit_cost')}/>
          <input type="number" className="input" placeholder="Selling price" {...register('selling_price')}/>
          <input type="number" className="input" placeholder="Reorder level" {...register('reorder_level')}/>
        </form>
      </Modal>
    </div>
  );
}
