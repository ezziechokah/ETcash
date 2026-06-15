import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, formatDate } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';

export default function Reconciliation() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ['bank-transactions'],
    queryFn: () => api.get('/banking/transactions/').then(r => r.data),
  });
  const txns = unwrapList(data).filter(t => !t.reconciled);

  const reconcile = useMutation({
    mutationFn: (id) => api.post(`/banking/transactions/${id}/reconcile/`, { reconciled: true }),
    onSuccess: () => { toast.success('Reconciled'); qc.invalidateQueries({ queryKey: ['bank-transactions'] }); },
  });

  const columns = [
    { header: 'Date', accessorKey: 'transaction_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Description', accessorKey: 'description' },
    { header: 'Type', accessorKey: 'txn_type' },
    { header: 'Amount', accessorKey: 'amount', cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
    { header: '', id: 'act', cell: ({ row }) => (
      <button type="button" className="btn-primary text-xs py-1" onClick={() => reconcile.mutate(row.original.id)}>Match</button>
    )},
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Reconciliation" subtitle="Match unreconciled bank transactions"/>
      <div className="card">
        <DataTable data={txns} columns={columns} isLoading={isLoading} emptyMessage="All transactions reconciled."/>
      </div>
    </div>
  );
}
