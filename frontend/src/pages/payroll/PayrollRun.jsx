import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function PayrollRun() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [detail, setDetail] = useState(null);

  const { data, isLoading } = useQuery({ queryKey: ['payroll-runs'], queryFn: () => api.get('/payroll/runs/').then(r => r.data) });

  const create = useMutation({
    mutationFn: () => api.post('/payroll/runs/', { period_month: month, period_year: year }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['payroll-runs'] }); toast.success('Payroll run created'); setOpen(false); },
    onError: (e) => toast.error(e.response?.data?.detail || 'Failed'),
  });

  const process = useMutation({
    mutationFn: id => api.post(`/payroll/runs/${id}/process/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['payroll-runs'] }); toast.success('Payroll processed'); },
  });

  const columns = [
    { header: 'Period', accessorKey: 'period_label' },
    { header: 'Status', accessorKey: 'status' },
    { header: 'Gross', accessorKey: 'total_gross', cell: ({ getValue }) => formatCurrency(getValue()) },
    { header: 'Net', accessorKey: 'total_net', cell: ({ getValue }) => formatCurrency(getValue()) },
    { header: '', id: 'act', cell: ({ row }) => (
      <div className="flex gap-2">
        {row.original.status === 'draft' && (
          <button type="button" className="btn-primary text-xs py-1" onClick={e => { e.stopPropagation(); process.mutate(row.original.id); }}>Process</button>
        )}
        <button type="button" className="btn-ghost text-xs" onClick={e => { e.stopPropagation(); api.get(`/payroll/runs/${row.original.id}/`).then(r => setDetail(r.data)); }}>View</button>
      </div>
    )},
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Run Payroll" actions={<button type="button" className="btn-primary" onClick={() => setOpen(true)}>New run</button>}/>
      <div className="card"><DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/></div>
      <Modal open={open} onClose={() => setOpen(false)} title="New payroll run" footer={<button type="button" className="btn-primary" onClick={() => create.mutate()}>Create</button>}>
        <div className="flex gap-4">
          <div><label className="label">Month</label><input type="number" min={1} max={12} className="input" value={month} onChange={e => setMonth(Number(e.target.value))}/></div>
          <div><label className="label">Year</label><input type="number" className="input" value={year} onChange={e => setYear(Number(e.target.value))}/></div>
        </div>
      </Modal>
      <Modal open={!!detail} onClose={() => setDetail(null)} title={detail?.period_label} size="lg">
        {detail?.payslips?.length ? (
          <table className="w-full text-sm">
            <thead><tr className="table-header"><th>Name</th><th className="text-right">Gross</th><th className="text-right">NSSF</th><th className="text-right">NHIF</th><th className="text-right">PAYE</th><th className="text-right">Net</th></tr></thead>
            <tbody>
              {detail.payslips.map(s => (
                <tr key={s.id} className="border-b border-surface-border">
                  <td className="py-2">{s.employee_name}</td>
                  <td className="text-right font-mono">{formatCurrency(s.gross)}</td>
                  <td className="text-right font-mono text-slate-400">{formatCurrency(s.nssf)}</td>
                  <td className="text-right font-mono text-slate-400">{formatCurrency(s.nhif)}</td>
                  <td className="text-right font-mono text-slate-400">{formatCurrency(s.paye)}</td>
                  <td className="text-right font-mono text-white">{formatCurrency(s.net)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : <p className="text-slate-500">Process the run to generate payslips.</p>}
      </Modal>
    </div>
  );
}
