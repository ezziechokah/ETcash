import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

function Block({ title, rows, total, accent }) {
  return (
    <div className="card">
      <h3 className={`text-sm font-semibold mb-4 ${accent}`}>{title}</h3>
      <table className="w-full text-sm">
        <tbody>
          {(rows || []).map(r => (
            <tr key={r.code + r.name} className="border-b border-surface-border">
              <td className="py-2 font-mono text-xs text-slate-500 w-16">{r.code}</td>
              <td className="py-2 text-slate-200">{r.name}</td>
              <td className="py-2 text-right font-mono">{formatCurrency(r.amount)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="font-semibold border-t border-surface-border">
            <td colSpan={2} className="py-3">Total {title}</td>
            <td className="py-3 text-right font-mono text-white">{formatCurrency(total)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

export default function BalanceSheet() {
  const today = new Date().toISOString().slice(0, 10);
  const [asOf, setAsOf] = useState(today);

  const { data, isLoading } = useQuery({
    queryKey: ['balance-sheet', asOf],
    queryFn: () => api.get('/reports/balance-sheet/', { params: { as_of: asOf } }).then(r => r.data),
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Balance Sheet" subtitle="Assets, liabilities, and equity"/>
      <div className="card">
        <label className="label">As of date</label>
        <input type="date" className="input max-w-xs" value={asOf} onChange={e => setAsOf(e.target.value)}/>
      </div>
      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/>
        </div>
      ) : data && (
        <>
          {data.balanced
            ? <p className="text-green-400 text-sm">Books balance (assets = liabilities + equity)</p>
            : <p className="text-yellow-400 text-sm">Retained earnings adjusted to balance the sheet</p>}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Block title="Assets" rows={data.assets} total={data.total_assets} accent="text-blue-400"/>
            <Block title="Liabilities" rows={data.liabilities} total={data.total_liabilities} accent="text-red-400"/>
            <Block title="Equity" rows={data.equity} total={data.total_equity} accent="text-purple-400"/>
          </div>
        </>
      )}
    </div>
  );
}
