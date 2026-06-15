import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import ReportPeriodFilter from '../../components/ReportPeriodFilter.jsx';
import StatCard from '../../components/StatCard.jsx';
import { ChartBarIcon } from '@heroicons/react/24/outline';

function Section({ title, rows, total, color }) {
  return (
    <div className="card">
      <h3 className="text-sm font-semibold text-slate-300 mb-4">{title}</h3>
      <table className="w-full text-sm">
        <tbody>
          {(rows || []).map(r => (
            <tr key={r.code + r.name} className="border-b border-surface-border">
              <td className="py-2 text-slate-400 font-mono text-xs w-20">{r.code}</td>
              <td className="py-2 text-slate-200">{r.name}</td>
              <td className="py-2 text-right font-mono text-white">{formatCurrency(r.amount)}</td>
            </tr>
          ))}
          {(!rows || rows.length === 0) && (
            <tr><td colSpan={3} className="py-6 text-center text-slate-500">No activity in this period</td></tr>
          )}
        </tbody>
        <tfoot>
          <tr className="border-t border-surface-border font-semibold">
            <td colSpan={2} className="py-3 text-slate-300">Total</td>
            <td className={`py-3 text-right font-mono ${color}`}>{formatCurrency(total)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

export default function ProfitLoss() {
  const y = new Date().getFullYear();
  const [from, setFrom] = useState(`${y}-01-01`);
  const [to, setTo] = useState(`${y}-12-31`);

  const { data, isLoading } = useQuery({
    queryKey: ['profit-loss', from, to],
    queryFn: () => api.get('/reports/profit-loss/', { params: { from, to } }).then(r => r.data),
  });

  return (
    <div className="space-y-6">
      <PageHeader title="Profit & Loss" subtitle="Income statement for the selected period"/>
      <ReportPeriodFilter from={from} to={to} onFrom={setFrom} onTo={setTo}/>
      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/>
        </div>
      ) : data && (
        <>
          <StatCard title="Net profit" value={formatCurrency(data.net_profit)} icon={ChartBarIcon}
            color={Number(data.net_profit) >= 0 ? 'green' : 'red'}/>
          <Section title="Revenue" rows={data.revenue} total={data.total_revenue} color="text-green-400"/>
          <Section title="Expenses" rows={data.expenses} total={data.total_expenses} color="text-red-400"/>
        </>
      )}
    </div>
  );
}
