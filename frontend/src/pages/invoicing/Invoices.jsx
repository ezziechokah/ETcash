import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, formatDate, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';

export default function Invoices() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const status = params.get('status');

  const { data, isLoading } = useQuery({
    queryKey: ['invoices', status],
    queryFn: () => api.get('/invoicing/invoices/', { params: status ? { status } : {} }).then(r => r.data),
  });
  const invoices = unwrapList(data);

  const columns = [
    { header: 'Invoice #', accessorKey: 'invoice_number',
      cell: ({ row }) => <span className="font-mono text-white">{row.original.invoice_number}</span> },
    { header: 'Customer', accessorKey: 'customer_name' },
    { header: 'Issue date', accessorKey: 'issue_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Due', accessorKey: 'due_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Amount', accessorKey: 'total_amount',
      cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
    { header: 'Status', accessorKey: 'status',
      cell: ({ getValue }) => <span className={statusBadge(getValue())}>{getValue()}</span> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Invoices" subtitle="Sales invoices and accounts receivable"
        actions={<Link to="/invoicing/invoices/new" className="btn-primary">New invoice</Link>}/>
      <div className="card">
        <DataTable data={invoices} columns={columns} isLoading={isLoading}
          onRowClick={row => navigate(`/invoicing/invoices/${row.id}`)}
          emptyMessage="No invoices yet."/>
      </div>
    </div>
  );
}
