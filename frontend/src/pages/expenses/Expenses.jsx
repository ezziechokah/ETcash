import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, formatDate } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';

export default function Expenses() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ['expenses'],
    queryFn: () => api.get('/expenses/expenses/').then(r => r.data),
  });

  const columns = [
    { header: 'Date', accessorKey: 'expense_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Description', accessorKey: 'description' },
    { header: 'Vendor', accessorKey: 'vendor_name', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Category', accessorKey: 'category', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Tax', accessorKey: 'tax_rate', cell: ({ getValue }) => `${getValue()}%` },
    { header: 'Total', accessorKey: 'total_amount', cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Expenses" subtitle="Operating expenses with VAT / WHT"
        actions={<Link to="/expenses/new" className="btn-primary">Record expense</Link>}/>
      <div className="card">
        <DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}
          onRowClick={row => navigate(`/expenses/${row.id}/edit`)}/>
      </div>
    </div>
  );
}
