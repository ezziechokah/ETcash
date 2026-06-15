import React, { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function ItemForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { register, handleSubmit, reset } = useForm();

  const { data: item } = useQuery({
    queryKey: ['item', id],
    queryFn: () => api.get(`/inventory/items/${id}/`).then(r => r.data),
  });

  useEffect(() => { if (item) reset(item); }, [item, reset]);

  const save = useMutation({
    mutationFn: d => api.put(`/inventory/items/${id}/`, {
      ...d,
      quantity_on_hand: Number(d.quantity_on_hand),
      unit_cost: Number(d.unit_cost),
      selling_price: Number(d.selling_price),
      reorder_level: Number(d.reorder_level),
    }),
    onSuccess: () => { toast.success('Saved'); navigate('/inventory'); },
  });

  if (!item) return null;
  return (
    <div className="space-y-6 max-w-xl">
      <PageHeader title={`Edit ${item.name}`}/>
      <form onSubmit={handleSubmit(d => save.mutate(d))} className="card space-y-3">
        <input className="input" {...register('sku')} />
        <input className="input" {...register('name')} />
        <input type="number" className="input" {...register('quantity_on_hand')} />
        <input type="number" className="input" {...register('unit_cost')} />
        <input type="number" className="input" {...register('selling_price')} />
        <button type="submit" className="btn-primary">Update</button>
      </form>
    </div>
  );
}
