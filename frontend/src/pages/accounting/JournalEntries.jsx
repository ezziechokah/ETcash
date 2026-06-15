import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency, formatDate, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';

export default function JournalEntries() {
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['journal-entries'],
    queryFn: () => api.get('/accounting/journal-entries/').then(r => r.data),
  });
  const entries = unwrapList(data);

  const postEntry = useMutation({
    mutationFn: (id) => api.post(`/accounting/journal-entries/${id}/post_entry/`),
    onSuccess: () => { toast.success('Entry posted'); qc.invalidateQueries({ queryKey: ['journal-entries'] }); },
    onError: (e) => toast.error(e.response?.data?.detail || 'Could not post'),
  });

  const columns = [
    { header: 'Date', accessorKey: 'entry_date', cell: ({ getValue }) => formatDate(getValue()) },
    { header: 'Reference', accessorKey: 'reference', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Description', accessorKey: 'description' },
    { header: 'Debit', accessorKey: 'total_debit', cell: ({ getValue }) => <span className="font-mono">{formatCurrency(getValue())}</span> },
    { header: 'Lines', accessorKey: 'line_count' },
    { header: 'Status', accessorKey: 'status', cell: ({ getValue }) => <span className={statusBadge(getValue())}>{getValue()}</span> },
    { header: '', id: 'actions', cell: ({ row }) => row.original.status === 'draft' ? (
      <button type="button" className="btn-ghost text-xs" onClick={e => { e.stopPropagation(); postEntry.mutate(row.original.id); }}>Post</button>
    ) : null },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Journal Entries" subtitle="Double-entry bookkeeping"
        actions={<Link to="/accounting/journal-entries/new" className="btn-primary">New entry</Link>}/>
      <div className="card">
        <DataTable data={entries} columns={columns} isLoading={isLoading}
          onRowClick={row => navigate(`/accounting/journal-entries/${row.id}`)}
          emptyMessage="No journal entries yet."/>
      </div>
    </div>
  );
}
