import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore.js';
import { useUiStore } from '../../store/uiStore.js';
import { clsx } from 'clsx';
import {
  HomeIcon, BookOpenIcon, DocumentTextIcon, CreditCardIcon,
  BuildingLibraryIcon, CubeIcon, FolderIcon, BuildingOffice2Icon,
  UsersIcon, ChartBarIcon, LightBulbIcon, Cog6ToothIcon,
  ChevronDownIcon, ChevronRightIcon, Bars3Icon
} from '@heroicons/react/24/outline';

const NAV = [
  { label:'Overview', items:[{ label:'Dashboard', icon:HomeIcon, to:'/dashboard' }]},
  { label:'Accounting', items:[
    { label:'Chart of Accounts', icon:BookOpenIcon,     to:'/accounting/chart-of-accounts' },
    { label:'Journal Entries',   icon:DocumentTextIcon, to:'/accounting/journal-entries' },
  ]},
  { label:'Sales', items:[
    { label:'Invoices',  icon:DocumentTextIcon, to:'/invoicing/invoices' },
    { label:'Customers', icon:UsersIcon,         to:'/invoicing/customers' },
  ]},
  { label:'Purchases', items:[
    { label:'Expenses', icon:CreditCardIcon,   to:'/expenses/list' },
    { label:'Bills',    icon:DocumentTextIcon, to:'/expenses/bills' },
    { label:'Vendors',  icon:UsersIcon,        to:'/expenses/vendors' },
  ]},
  { label:'Banking', items:[
    { label:'Bank Accounts',  icon:BuildingLibraryIcon, to:'/banking/accounts' },
    { label:'Reconciliation', icon:ChartBarIcon,        to:'/banking/reconciliation' },
    { label:'Import',         icon:DocumentTextIcon,    to:'/banking/import' },
  ]},
  { label:'Inventory', feature:'inventory', items:[
    { label:'Items & Stock',   icon:CubeIcon,     to:'/inventory' },
    { label:'Stock Movements', icon:ChartBarIcon, to:'/inventory/movements' },
  ]},
  { label:'Projects', feature:'projects', items:[
    { label:'All Projects', icon:FolderIcon,   to:'/projects' },
  ]},
  { label:'Entities', feature:'multi_entity', items:[
    { label:'Entities',      icon:BuildingOffice2Icon, to:'/entities' },
    { label:'Consolidation', icon:ChartBarIcon,        to:'/entities/consolidation' },
  ]},
  { label:'Payroll', feature:'payroll', items:[
    { label:'Employees',   icon:UsersIcon,        to:'/payroll' },
    { label:'Run Payroll', icon:DocumentTextIcon, to:'/payroll/run' },
  ]},
  { label:'Reports', items:[
    { label:'Profit & Loss',  icon:ChartBarIcon,     to:'/reports/profit-loss' },
    { label:'Balance Sheet',  icon:BookOpenIcon,     to:'/reports/balance-sheet' },
    { label:'Cash Flow',      icon:CreditCardIcon,   to:'/reports/cash-flow' },
    { label:'Tax Report',     icon:DocumentTextIcon, to:'/reports/tax' },
  ]},
  { label:'Intelligence', items:[
    { label:'Strategic Insights', icon:LightBulbIcon, to:'/insights' }
  ]},
];

function Group({ group, collapsed }) {
  const canAccess = useAuthStore(s => s.canAccess);
  const location  = useLocation();
  const [open, setOpen] = useState(true);
  if (group.feature && !canAccess(group.feature)) return null;
  const active = group.items.some(i => location.pathname.startsWith(i.to));

  if (collapsed) return (
    <div className="mb-1 space-y-0.5">
      {group.items.map(item => (
        <NavLink key={item.to+item.label} to={item.to} title={item.label}
          className={({isActive}) => clsx(
            'flex items-center justify-center w-10 h-10 mx-auto rounded-lg transition-colors',
            isActive ? 'bg-brand-600 text-white' : 'text-fg-muted hover:bg-surface-card hover:text-fg-secondary'
          )}>
          <item.icon className="w-5 h-5"/>
        </NavLink>
      ))}
    </div>
  );

  return (
    <div className="mb-2">
      <button onClick={() => setOpen(o => !o)}
        className={clsx('flex items-center justify-between w-full px-3 py-1.5 text-xs font-semibold uppercase tracking-wider rounded-md transition-colors',
          active ? 'text-brand-400' : 'text-fg-faint hover:text-fg-muted')}>
        <span>{group.label}</span>
        {open ? <ChevronDownIcon className="w-3 h-3"/> : <ChevronRightIcon className="w-3 h-3"/>}
      </button>
      {open && (
        <div className="mt-0.5 space-y-0.5">
          {group.items.map(item => (
            <NavLink key={item.to+item.label} to={item.to}
              className={({isActive}) => clsx(
                'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
                isActive ? 'bg-brand-600/20 text-brand-400 font-medium' : 'text-fg-muted hover:bg-surface-card hover:text-fg-secondary'
              )}>
              <item.icon className="w-4 h-4 flex-shrink-0"/>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Sidebar() {
  const open   = useUiStore(s => s.sidebarOpen);
  const toggle = useUiStore(s => s.toggleSidebar);
  const company = useAuthStore(s => s.company);
  const mode    = useAuthStore(s => s.mode);
  const modeLabel = { freelancer:'Freelancer', sme:'SME', multi_entity:'Multi-Entity' };
  const modeColor = { freelancer:'bg-green-900/50 text-green-400', sme:'bg-blue-900/50 text-blue-400', multi_entity:'bg-purple-900/50 text-purple-400' };

  return (
    <aside className={clsx(
      'fixed left-0 top-0 h-full bg-surface-card border-r border-surface-border flex flex-col transition-all duration-200 z-40',
      open ? 'w-64' : 'w-16'
    )}>
      <div className="flex items-center gap-3 px-4 py-4 border-b border-surface-border flex-shrink-0">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-sm">ET</span>
        </div>
        {open && (
          <div className="flex-1 min-w-0">
            <div className="font-bold text-fg text-sm">ETcash</div>
            {company && <div className="text-xs text-fg-muted truncate">{company.name}</div>}
          </div>
        )}
        <button onClick={toggle} className="text-fg-muted hover:text-fg-secondary transition-colors ml-auto flex-shrink-0">
          <Bars3Icon className="w-5 h-5"/>
        </button>
      </div>
      {open && mode && (
        <div className="px-4 py-2 flex-shrink-0">
          <span className={clsx('text-xs font-medium px-2 py-1 rounded-full', modeColor[mode])}>
            {modeLabel[mode]}
          </span>
        </div>
      )}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-1">
        {NAV.map(g => <Group key={g.label} group={g} collapsed={!open}/>)}
      </nav>
      <div className="border-t border-surface-border p-2 flex-shrink-0">
        <NavLink to="/settings"
          className={({isActive}) => clsx(
            'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors',
            isActive ? 'bg-brand-600/20 text-brand-400' : 'text-slate-400 hover:bg-surface-card hover:text-slate-200'
          )}>
          <Cog6ToothIcon className="w-4 h-4 flex-shrink-0"/>
          {open && <span>Settings</span>}
        </NavLink>
      </div>
    </aside>
  );
}
