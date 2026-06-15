import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../../api/client.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import ReportPeriodFilter from '../../components/ReportPeriodFilter.jsx';
import StatCard from '../../components/StatCard.jsx';
import { BanknotesIcon } from '@heroicons/react/24/outline';

function FlowList({ title, items, negative }) {
  return (
    <div>
      <h4 className="text-xs font-semibold text-slate-500 uppercase mb-2">{title}</h4>
      <ul className="space-y-2">
        {(items || []).map(item => (
          <li key={item.label} className="flex justify-between text-sm">
            <span className="text-slate-400">{item.label}</span>
            <span className={`font-mono ${negative ? 'text-red-400' : 'text-green-400'}`}>
              {negative ? '−' : '+'}{formatCurrency(item.amount)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function CashFlow() {
  const y = new Date().getFullYear();
  const [from, setFrom] = useState(`${y}-01-01`);
  const [to, setTo] = useState(`${y}-12-31`);

  const { data, isLoading } = useQuery({
    queryKey: ['cash-flow-report', from, to],
    queryFn: () => api.get('/reports/cash-flow/', { params: { from, to } }).then(r => r.data),
  });

  const op = data?.operating;

  return (
    <div className="space-y-6">
      <PageHeader title="Cash Flow" subtitle="Operating cash movements for the period"/>
      <ReportPeriodFilter from={from} to={to} onFrom={setFrom} onTo={setTo}/>
      {isLoading ? (
        <div className="flex justify-center py-16">
          <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/>
        </div>
      ) : data && op && (
        <>
          <StatCard title="Net change in cash" value={formatCurrency(data.net_change_in_cash)}
            icon={BanknotesIcon} color={Number(op.net) >= 0 ? 'green' : 'red'}/>
          <div className="card grid grid-cols-1 md:grid-cols-2 gap-8">
            <FlowList title="Cash inflows" items={op.inflows}/>
            <FlowList title="Cash outflows" items={op.outflows} negative/>
          </div>
          <div className="card flex justify-between text-sm font-semibold">
            <span className="text-slate-300">Net operating cash flow</span>
            <span className={`font-mono ${Number(op.net) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatCurrency(op.net)}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
