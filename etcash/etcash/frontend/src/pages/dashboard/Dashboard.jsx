import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../../api/client.js';
import { useAuthStore } from '../../store/authStore.js';
import PageHeader from '../../components/PageHeader.jsx';
import StatCard from '../../components/StatCard.jsx';
import { formatCurrency, formatDate, statusBadge } from '../../utils/format.js';
import { AreaChart, Area, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { BanknotesIcon, DocumentTextIcon, CreditCardIcon, ChartBarIcon, ExclamationTriangleIcon, LightBulbIcon } from '@heroicons/react/24/outline';

const COLORS = ['#3b82f6','#22c55e','#f59e0b','#ef4444','#8b5cf6','#06b6d4'];

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-surface-card border border-surface-border rounded-lg p-3 text-xs shadow-xl">
      <p className="text-slate-300 font-medium mb-1">{label}</p>
      {payload.map((p,i) => <p key={i} style={{color:p.color}}>{p.name}: {formatCurrency(p.value)}</p>)}
    </div>
  );
};

export default function Dashboard() {
  const { company } = useAuthStore();
  const { data: stats } = useQuery({ queryKey:['dashboard-stats'], queryFn:() => api.get('/reports/dashboard/').then(r=>r.data), refetchInterval:60000 });
  const { data: cashflow } = useQuery({ queryKey:['dashboard-cashflow'], queryFn:() => api.get('/reports/cashflow-chart/').then(r=>r.data) });
  const { data: insights } = useQuery({ queryKey:['dashboard-insights'], queryFn:() => api.get('/tax/insights/').then(r=>r.data) });
  const { data: recentInvoices } = useQuery({ queryKey:['dashboard-invoices'], queryFn:() => api.get('/invoicing/invoices/?ordering=-created_at').then(r=>r.data) });

  const s   = stats   || {};
  const cf  = cashflow?.monthly || [];
  const ins = insights?.insights || [];
  const invoices = Array.isArray(recentInvoices) ? recentInvoices : recentInvoices?.results || [];

  return (
    <div className="space-y-6">
      <PageHeader title={`Welcome back${company ? `, ${company.name}` : ''}`} subtitle={`Financial overview · ${formatDate(new Date())}`}/>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Cash Position"    value={formatCurrency(s.cash_position)}  icon={BanknotesIcon}    color="blue"   trend={s.cash_trend}   trendLabel="vs last month"/>
        <StatCard title="Receivables (AR)" value={formatCurrency(s.total_ar)}       icon={DocumentTextIcon} color="green"  trend={s.ar_trend}     trendLabel="vs last month"/>
        <StatCard title="Payables (AP)"    value={formatCurrency(s.total_ap)}       icon={CreditCardIcon}   color="yellow" trend={s.ap_trend}     trendLabel="vs last month"/>
        <StatCard title="Net Profit (MTD)" value={formatCurrency(s.net_profit_mtd)} icon={ChartBarIcon}     color="purple" trend={s.profit_trend} trendLabel="vs last month"/>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Cash Flow — Last 6 Months</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={cf} margin={{top:5,right:5,left:5,bottom:5}}>
              <defs>
                <linearGradient id="inGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="outGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155"/>
              <XAxis dataKey="month" tick={{fill:'#94a3b8',fontSize:11}} axisLine={false} tickLine={false}/>
              <YAxis tick={{fill:'#94a3b8',fontSize:11}} axisLine={false} tickLine={false} tickFormatter={v=>`${(v/1000).toFixed(0)}k`}/>
              <Tooltip content={<ChartTooltip/>}/>
              <Area type="monotone" dataKey="inflow"  name="Inflow"  stroke="#3b82f6" fill="url(#inGrad)"  strokeWidth={2}/>
              <Area type="monotone" dataKey="outflow" name="Outflow" stroke="#ef4444" fill="url(#outGrad)" strokeWidth={2}/>
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Expenses by Category</h3>
          {(s.expense_breakdown||[]).length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={s.expense_breakdown||[]} dataKey="amount" nameKey="category" cx="50%" cy="50%" outerRadius={65} innerRadius={35}>
                    {(s.expense_breakdown||[]).map((_,i) => <Cell key={i} fill={COLORS[i%COLORS.length]}/>)}
                  </Pie>
                  <Tooltip formatter={v=>formatCurrency(v)} contentStyle={{background:'#1e293b',border:'1px solid #334155',borderRadius:8}}/>
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1 mt-2">
                {(s.expense_breakdown||[]).slice(0,4).map((item,i) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full flex-shrink-0" style={{background:COLORS[i%COLORS.length]}}/>
                      <span className="text-slate-400 truncate max-w-24">{item.category}</span>
                    </div>
                    <span className="font-mono text-slate-200">{formatCurrency(item.amount)}</span>
                  </div>
                ))}
              </div>
            </>
          ) : <div className="flex items-center justify-center h-40 text-slate-500 text-sm">No expense data yet</div>}
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-300">Recent Invoices</h3>
            <Link to="/invoicing/invoices" className="text-xs text-brand-400 hover:text-brand-300">View all →</Link>
          </div>
          <div>
            {invoices.slice(0,5).map(inv => (
              <Link key={inv.id} to={`/invoicing/invoices/${inv.id}`}
                className="flex items-center justify-between py-2.5 border-b border-surface-border last:border-0 hover:bg-surface-card/30 -mx-2 px-2 rounded transition-colors">
                <div className="min-w-0">
                  <p className="text-sm text-slate-200 font-medium truncate">{inv.invoice_number}</p>
                  <p className="text-xs text-slate-400">{inv.customer_name} · Due {formatDate(inv.due_date)}</p>
                </div>
                <div className="text-right ml-4 flex-shrink-0">
                  <p className="text-sm font-medium text-white font-mono">{formatCurrency(inv.total_amount)}</p>
                  <span className={statusBadge(inv.status)}>{inv.status}</span>
                </div>
              </Link>
            ))}
            {invoices.length === 0 && (
              <div className="text-center py-8 text-slate-500 text-sm">
                No invoices yet. <Link to="/invoicing/invoices/new" className="text-brand-400 hover:text-brand-300">Create one →</Link>
              </div>
            )}
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-slate-300">Strategic Insights</h3>
            <Link to="/insights" className="text-xs text-brand-400 hover:text-brand-300">View all →</Link>
          </div>
          <div className="space-y-3">
            {ins.slice(0,4).map((insight,i) => {
              const colors = { danger:'border-red-800/50 bg-red-900/10', warning:'border-yellow-800/50 bg-yellow-900/10', success:'border-green-800/50 bg-green-900/10', info:'border-brand-800/50 bg-brand-900/10' };
              const iconColors = { danger:'text-red-400', warning:'text-yellow-400', success:'text-green-400', info:'text-brand-400' };
              return (
                <div key={i} className={`flex gap-3 p-3 rounded-lg border ${colors[insight.severity]||colors.info}`}>
                  {insight.severity==='warning'||insight.severity==='danger'
                    ? <ExclamationTriangleIcon className={`w-4 h-4 flex-shrink-0 mt-0.5 ${iconColors[insight.severity]}`}/>
                    : <LightBulbIcon className={`w-4 h-4 flex-shrink-0 mt-0.5 ${iconColors[insight.severity]||iconColors.info}`}/>}
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-200">{insight.title}</p>
                    <p className="text-xs text-slate-400 mt-0.5 line-clamp-2">{insight.message}</p>
                  </div>
                </div>
              );
            })}
            {ins.length === 0 && <div className="text-center py-8 text-slate-500 text-sm">Add more transactions to generate insights</div>}
          </div>
        </div>
      </div>
      {s.overdue_invoices > 0 && (
        <div className="flex items-center gap-4 p-4 rounded-xl border border-red-800/50 bg-red-900/10">
          <ExclamationTriangleIcon className="w-5 h-5 text-red-400 flex-shrink-0"/>
          <div className="flex-1">
            <p className="text-sm font-medium text-red-300">{s.overdue_invoices} overdue invoice{s.overdue_invoices!==1?'s':''} totalling {formatCurrency(s.overdue_amount)}</p>
            <p className="text-xs text-slate-400 mt-0.5">Follow up with customers to improve cash flow</p>
          </div>
          <Link to="/invoicing/invoices?status=overdue" className="btn-danger text-xs py-1.5 px-3 flex-shrink-0">View Overdue</Link>
        </div>
      )}
    </div>
  );
}
