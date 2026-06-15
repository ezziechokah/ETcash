import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../../api/client.js';
import PageHeader from '../../components/PageHeader.jsx';
import { ExclamationTriangleIcon, LightBulbIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

const styles = {
  danger: { box: 'border-red-800/50 bg-red-900/10', icon: 'text-red-400' },
  warning: { box: 'border-yellow-800/50 bg-yellow-900/10', icon: 'text-yellow-400' },
  success: { box: 'border-green-800/50 bg-green-900/10', icon: 'text-green-400' },
  info: { box: 'border-brand-800/50 bg-brand-900/10', icon: 'text-brand-400' },
};

function InsightIcon({ severity }) {
  if (severity === 'danger' || severity === 'warning') return <ExclamationTriangleIcon className={`w-5 h-5 flex-shrink-0 ${styles[severity]?.icon}`}/>;
  if (severity === 'success') return <CheckCircleIcon className={`w-5 h-5 flex-shrink-0 ${styles.success.icon}`}/>;
  return <LightBulbIcon className={`w-5 h-5 flex-shrink-0 ${styles.info.icon}`}/>;
}

export default function StrategicInsights() {
  const { data, isLoading } = useQuery({
    queryKey: ['insights'],
    queryFn: () => api.get('/tax/insights/').then(r => r.data),
  });

  const insights = data?.insights || [];

  return (
    <div className="space-y-6">
      <PageHeader title="Strategic Insights" subtitle="Rules-based alerts from your live books"/>
      {isLoading ? (
        <div className="flex justify-center py-16"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"/></div>
      ) : (
        <div className="space-y-4">
          {insights.map((ins, i) => (
            <div key={i} className={`flex gap-4 p-5 rounded-xl border ${styles[ins.severity]?.box || styles.info.box}`}>
              <InsightIcon severity={ins.severity}/>
              <div>
                <p className="font-semibold text-slate-200">{ins.title}</p>
                <p className="text-sm text-slate-400 mt-1">{ins.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="card text-sm text-slate-400">
        <p>Quick links: <Link to="/reports/tax" className="text-brand-400">Tax report</Link> · <Link to="/reports/profit-loss" className="text-brand-400">P&amp;L</Link> · <Link to="/invoicing/invoices" className="text-brand-400">Invoices</Link></p>
      </div>
    </div>
  );
}
