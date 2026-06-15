import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import StatCard from '../../components/StatCard.jsx';
import { DocumentTextIcon, BanknotesIcon } from '@heroicons/react/24/outline';
import Papa from 'papaparse';
import { saveAs } from 'file-saver';

function periodParams(from, to) {
  const p = {};
  if (from) p.from = from;
  if (to) p.to = to;
  return p;
}

export default function TaxReport() {
  const y = new Date().getFullYear();
  const [from, setFrom] = useState(`${y}-01-01`);
  const [to, setTo] = useState(`${y}-12-31`);

  const { data: vat, isLoading: vatLoading } = useQuery({
    queryKey: ['vat-report', from, to],
    queryFn: () => api.get('/tax/vat-report/', { params: periodParams(from, to) }).then(r => r.data),
  });

  const { data: wht, isLoading: whtLoading } = useQuery({
    queryKey: ['wht-report', from, to],
    queryFn: () => api.get('/tax/wht-report/', { params: periodParams(from, to) }).then(r => r.data),
  });

  const downloadVatExport = () => {
    if (!vat) return;
    const rows = [
      {
        type: 'output',
        label: 'Output VAT (sales)',
        invoice_count: vat.output?.invoice_count || 0,
        taxable_amount: vat.output?.taxable_amount || 0,
        vat_amount: vat.output?.vat_amount || 0,
      },
      {
        type: 'input',
        label: 'Input VAT (purchases)',
        expense_count: vat.input?.expense_count || 0,
        taxable_amount: vat.input?.taxable_amount || 0,
        vat_amount: vat.input?.vat_amount || 0,
      },
      {
        type: 'net',
        label: 'Net VAT payable',
        taxable_amount: '',
        vat_amount: vat.net_vat_payable,
      },
    ];
    const csv = Papa.unparse(rows, { columns: ['type', 'label', 'invoice_count', 'expense_count', 'taxable_amount', 'vat_amount'] });
    saveAs(new Blob([csv], { type: 'text/csv;charset=utf-8;' }), `etcash-vat-export-${from}-${to}.csv`);
  };

  const downloadWhtExport = () => {
    if (!wht) return;
    const rows = (wht.breakdown || []).map(row => ({
      rate: `${row.rate}%`,
      label: row.label,
      transactions: row.count,
      gross_amount: row.gross_amount,
      wht_amount: row.wht_amount,
    }));
    const footer = [{ rate: 'TOTAL', label: 'Total WHT', transactions: '', gross_amount: '', wht_amount: wht.total_wht }];
    const csv = Papa.unparse([...rows, ...footer], { columns: ['rate', 'label', 'transactions', 'gross_amount', 'wht_amount'] });
    saveAs(new Blob([csv], { type: 'text/csv;charset=utf-8;' }), `etcash-wht-export-${from}-${to}.csv`);
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Tax Report" subtitle="Kenya VAT 16% and Withholding Tax (KRA-ready summaries)"/>
      <div className="card flex flex-wrap gap-4 items-end">
        <div>
          <label className="label">From</label>
          <input type="date" className="input" value={from} onChange={e => setFrom(e.target.value)}/>
        </div>
        <div>
          <label className="label">To</label>
          <input type="date" className="input" value={to} onChange={e => setTo(e.target.value)}/>
        </div>
      </div>

      <section className="space-y-4">
        <div className="flex flex-wrap justify-between items-center gap-3">
          <h2 className="text-lg font-semibold text-white">VAT (16%)</h2>
          <button type="button" className="btn-secondary" onClick={downloadVatExport} disabled={!vat || vatLoading}>Download KRA VAT export</button>
        </div>
        {vatLoading ? <div className="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full"/> : vat && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatCard title="Output VAT (Sales)" value={formatCurrency(vat.output?.vat_amount)} icon={DocumentTextIcon} color="green"/>
              <StatCard title="Input VAT (Purchases)" value={formatCurrency(vat.input?.vat_amount)} icon={BanknotesIcon} color="blue"/>
              <StatCard title="Net VAT Payable" value={formatCurrency(vat.net_vat_payable)} icon={DocumentTextIcon} color="purple"/>
            </div>
            <div className="card overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-header border-b border-surface-border">
                    <th className="text-left py-2">Item</th>
                    <th className="text-right py-2">Taxable base</th>
                    <th className="text-right py-2">Tax</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-surface-border">
                    <td className="py-2">Taxable sales ({vat.output?.invoice_count} invoices)</td>
                    <td className="text-right font-mono">{formatCurrency(vat.output?.taxable_amount)}</td>
                    <td className="text-right font-mono text-green-400">{formatCurrency(vat.output?.vat_amount)}</td>
                  </tr>
                  <tr>
                    <td className="py-2">Taxable purchases ({vat.input?.expense_count} expenses)</td>
                    <td className="text-right font-mono">{formatCurrency(vat.input?.taxable_amount)}</td>
                    <td className="text-right font-mono text-blue-400">{formatCurrency(vat.input?.vat_amount)}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>

      <section className="space-y-4">
        <div className="flex flex-wrap justify-between items-center gap-3">
          <h2 className="text-lg font-semibold text-white">Withholding Tax</h2>
          <button type="button" className="btn-secondary" onClick={downloadWhtExport} disabled={!wht || whtLoading}>Download KRA WHT export</button>
        </div>
        {whtLoading ? <div className="animate-spin w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full"/> : wht && (
          <>
            <StatCard title="Total WHT" value={formatCurrency(wht.total_wht)} icon={DocumentTextIcon} color="yellow"/>
            <div className="card overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="table-header border-b border-surface-border">
                    <th className="text-left py-2">Rate</th>
                    <th className="text-right py-2">Transactions</th>
                    <th className="text-right py-2">Gross</th>
                    <th className="text-right py-2">WHT</th>
                  </tr>
                </thead>
                <tbody>
                  {(wht.breakdown || []).map(row => (
                    <tr key={row.rate} className="border-b border-surface-border">
                      <td className="py-2 text-slate-200">{row.label}</td>
                      <td className="text-right">{row.count}</td>
                      <td className="text-right font-mono">{formatCurrency(row.gross_amount)}</td>
                      <td className="text-right font-mono text-yellow-400">{formatCurrency(row.wht_amount)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
