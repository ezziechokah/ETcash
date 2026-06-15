import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore.js';
import AppShell from './components/layout/AppShell.jsx';

const spin = (
  <div className="flex items-center justify-center h-64">
    <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
  </div>
);

const Login           = lazy(() => import('./pages/auth/Login.jsx'));
const Setup           = lazy(() => import('./pages/auth/Setup.jsx'));
const Dashboard       = lazy(() => import('./pages/dashboard/Dashboard.jsx'));
const ChartOfAccounts = lazy(() => import('./pages/accounting/ChartOfAccounts.jsx'));
const JournalEntries  = lazy(() => import('./pages/accounting/JournalEntries.jsx'));
const JournalForm     = lazy(() => import('./pages/accounting/JournalForm.jsx'));
const Invoices        = lazy(() => import('./pages/invoicing/Invoices.jsx'));
const InvoiceForm     = lazy(() => import('./pages/invoicing/InvoiceForm.jsx'));
const InvoiceDetail   = lazy(() => import('./pages/invoicing/InvoiceDetail.jsx'));
const Customers       = lazy(() => import('./pages/invoicing/Customers.jsx'));
const Expenses        = lazy(() => import('./pages/expenses/Expenses.jsx'));
const ExpenseForm     = lazy(() => import('./pages/expenses/ExpenseForm.jsx'));
const Bills           = lazy(() => import('./pages/expenses/Bills.jsx'));
const Vendors         = lazy(() => import('./pages/expenses/Vendors.jsx'));
const BankAccounts    = lazy(() => import('./pages/banking/BankAccounts.jsx'));
const Reconciliation  = lazy(() => import('./pages/banking/Reconciliation.jsx'));
const BankImport      = lazy(() => import('./pages/banking/BankImport.jsx'));
const Inventory       = lazy(() => import('./pages/inventory/Inventory.jsx'));
const ItemForm        = lazy(() => import('./pages/inventory/ItemForm.jsx'));
const StockMovements  = lazy(() => import('./pages/inventory/StockMovements.jsx'));
const Projects        = lazy(() => import('./pages/projects/Projects.jsx'));
const ProjectDetail   = lazy(() => import('./pages/projects/ProjectDetail.jsx'));
const JobCosting      = lazy(() => import('./pages/projects/JobCosting.jsx'));
const Entities        = lazy(() => import('./pages/entities/Entities.jsx'));
const Consolidation   = lazy(() => import('./pages/entities/Consolidation.jsx'));
const Payroll         = lazy(() => import('./pages/payroll/Payroll.jsx'));
const PayrollRun      = lazy(() => import('./pages/payroll/PayrollRun.jsx'));
const ProfitLoss      = lazy(() => import('./pages/reports/ProfitLoss.jsx'));
const BalanceSheet    = lazy(() => import('./pages/reports/BalanceSheet.jsx'));
const CashFlow        = lazy(() => import('./pages/reports/CashFlow.jsx'));
const TaxReport       = lazy(() => import('./pages/reports/TaxReport.jsx'));
const Settings        = lazy(() => import('./pages/settings/Settings.jsx'));
const Insights        = lazy(() => import('./pages/insights/StrategicInsights.jsx'));

function Guard({ children }) {
  return useAuthStore(s => s.isAuthenticated())
    ? children : <Navigate to="/login" replace />;
}

function Feature({ f, children }) {
  return useAuthStore(s => s.canAccess(f))
    ? children : <Navigate to="/dashboard" replace />;
}

export default function AppRoutes() {
  return (
    <Suspense fallback={spin}>
      <Routes>
        <Route path="/login" element={<Login/>}/>
        <Route path="/setup" element={<Setup/>}/>
        <Route path="/" element={<Guard><AppShell/></Guard>}>
          <Route index element={<Navigate to="/dashboard" replace/>}/>
          <Route path="dashboard" element={<Dashboard/>}/>
          <Route path="accounting/chart-of-accounts" element={<ChartOfAccounts/>}/>
          <Route path="accounting/journal-entries"   element={<JournalEntries/>}/>
          <Route path="accounting/journal-entries/new" element={<JournalForm/>}/>
          <Route path="accounting/journal-entries/:id" element={<JournalForm/>}/>
          <Route path="invoicing/invoices"          element={<Invoices/>}/>
          <Route path="invoicing/invoices/new"      element={<InvoiceForm/>}/>
          <Route path="invoicing/invoices/:id"      element={<InvoiceDetail/>}/>
          <Route path="invoicing/invoices/:id/edit" element={<InvoiceForm/>}/>
          <Route path="invoicing/customers"         element={<Customers/>}/>
          <Route path="expenses/list"    element={<Expenses/>}/>
          <Route path="expenses/new"     element={<ExpenseForm/>}/>
          <Route path="expenses/:id/edit" element={<ExpenseForm/>}/>
          <Route path="expenses/bills"   element={<Bills/>}/>
          <Route path="expenses/vendors" element={<Vendors/>}/>
          <Route path="banking/accounts"       element={<BankAccounts/>}/>
          <Route path="banking/reconciliation" element={<Reconciliation/>}/>
          <Route path="banking/import"         element={<BankImport/>}/>
          <Route path="inventory"           element={<Feature f="inventory"><Inventory/></Feature>}/>
          <Route path="inventory/items/new" element={<Feature f="inventory"><ItemForm/></Feature>}/>
          <Route path="inventory/items/:id" element={<Feature f="inventory"><ItemForm/></Feature>}/>
          <Route path="inventory/movements" element={<Feature f="inventory"><StockMovements/></Feature>}/>
          <Route path="projects"             element={<Feature f="projects"><Projects/></Feature>}/>
          <Route path="projects/:id"         element={<Feature f="projects"><ProjectDetail/></Feature>}/>
          <Route path="projects/:id/costing" element={<Feature f="job_costing"><JobCosting/></Feature>}/>
          <Route path="entities"              element={<Feature f="multi_entity"><Entities/></Feature>}/>
          <Route path="entities/consolidation" element={<Feature f="consolidation"><Consolidation/></Feature>}/>
          <Route path="payroll"     element={<Feature f="payroll"><Payroll/></Feature>}/>
          <Route path="payroll/run" element={<Feature f="payroll"><PayrollRun/></Feature>}/>
          <Route path="reports/profit-loss"   element={<ProfitLoss/>}/>
          <Route path="reports/balance-sheet" element={<BalanceSheet/>}/>
          <Route path="reports/cash-flow"     element={<CashFlow/>}/>
          <Route path="reports/tax"           element={<TaxReport/>}/>
          <Route path="insights" element={<Insights/>}/>
          <Route path="settings" element={<Settings/>}/>
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace/>}/>
      </Routes>
    </Suspense>
  );
}
