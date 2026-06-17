import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { api } from '../../api/client.js';
import { useAuthStore } from '../../store/authStore.js';
import toast from 'react-hot-toast';
import { CheckCircleIcon } from '@heroicons/react/24/outline';

const MODES = [
  { value:'freelancer',   label:'Freelancer',   desc:'Solo business — invoices, expenses, basic reports',
    features:['Invoicing & AR','Expense tracking','Bank reconciliation','P&L + Balance Sheet','Tax reports'] },
  { value:'sme',          label:'SME',           desc:'Small/medium business — full accounting + operations', recommended:true,
    features:['Everything in Freelancer','Inventory + COGS','Projects & job costing','Payroll (Kenya tax)','Strategic insights'] },
  { value:'multi_entity', label:'Multi-Entity',  desc:'Group of companies — consolidation & intercompany',
    features:['Everything in SME','Multiple entities','Intercompany transactions','Consolidated reporting','Eliminations'] },
];

export default function Setup() {
  const { register, handleSubmit, formState:{errors} } = useForm({ defaultValues:{ fy_start_month:1 } });
  const [mode, setMode]       = useState('sme');
  const [loading, setLoading] = useState(false);
  const { setAuth, setCompany } = useAuthStore();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/setup/', { ...data, mode });
      setAuth(res.data.user, res.data.token);
      setCompany(res.data.company);
      toast.success('ETcash is ready!');
      navigate('/dashboard');
    } catch (err) {
      const msg = err.response?.data;
      if (typeof msg === 'string') toast.error(msg);
      else if (msg?.detail) toast.error(msg.detail);
      else toast.error('Setup failed — check all fields');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-4">
      <div className="w-full max-w-3xl">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-4 shadow-2xl">
            <span className="text-white font-bold text-2xl">ET</span>
          </div>
          <h1 className="text-3xl font-bold text-fg">Set up ETcash</h1>
          <p className="text-fg-muted mt-1">Kenya-first Financial System — one-time setup</p>
        </div>
        <div className="card">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <div>
              <h3 className="text-base font-semibold text-fg mb-4 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center font-bold">1</span>
                Admin Account
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Username *</label>
                  <input className={`input ${errors.username?'input-error':''}`} placeholder="admin"
                    {...register('username',{required:'Required',minLength:{value:3,message:'Min 3 characters'}})}/>
                  {errors.username && <p className="error-msg">{errors.username.message}</p>}
                </div>
                <div>
                  <label className="label">Email *</label>
                  <input type="email" className={`input ${errors.email?'input-error':''}`} placeholder="admin@company.co.ke"
                    {...register('email',{required:'Required'})}/>
                  {errors.email && <p className="error-msg">{errors.email.message}</p>}
                </div>
                <div>
                  <label className="label">Password *</label>
                  <input type="password" className={`input ${errors.password?'input-error':''}`} placeholder="Min 8 characters"
                    {...register('password',{required:'Required',minLength:{value:8,message:'Min 8 characters'}})}/>
                  {errors.password && <p className="error-msg">{errors.password.message}</p>}
                </div>
                <div>
                  <label className="label">Full Name</label>
                  <input className="input" placeholder="John Doe" {...register('full_name')}/>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-base font-semibold text-fg mb-4 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center font-bold">2</span>
                Company Details
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <label className="label">Company Name *</label>
                  <input className={`input ${errors.company_name?'input-error':''}`} placeholder="Acme Kenya Ltd"
                    {...register('company_name',{required:'Required'})}/>
                  {errors.company_name && <p className="error-msg">{errors.company_name.message}</p>}
                </div>
                <div>
                  <label className="label">KRA PIN</label>
                  <input className="input" placeholder="P051234567X" {...register('kra_pin')}/>
                </div>
                <div>
                  <label className="label">Phone</label>
                  <input className="input" placeholder="+254 700 000000" {...register('phone')}/>
                </div>
                <div>
                  <label className="label">Financial Year Start</label>
                  <select className="input" {...register('fy_start_month')}>
                    {['January','February','March','April','May','June','July','August','September','October','November','December'].map((m,i) =>
                      <option key={m} value={i+1}>{m}</option>)}
                  </select>
                </div>
              </div>
            </div>
            <div>
              <h3 className="text-base font-semibold text-fg mb-4 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-brand-600 text-white text-xs flex items-center justify-center font-bold">3</span>
                Installation Mode
              </h3>
              <div className="grid grid-cols-3 gap-4">
                {MODES.map(m => (
                  <button type="button" key={m.value} onClick={() => setMode(m.value)}
                    className={`relative p-4 rounded-xl border-2 text-left transition-all ${mode===m.value?'border-brand-500 bg-brand-600/10':'border-surface-border hover:border-surface-muted'}`}>
                    {m.recommended && <span className="absolute -top-2 left-3 text-xs bg-brand-600 text-white px-2 py-0.5 rounded-full font-medium">Recommended</span>}
                    <div className="font-semibold text-fg text-sm mb-1">{m.label}</div>
                    <div className="text-xs text-fg-muted mb-3">{m.desc}</div>
                    <ul className="space-y-1">
                      {m.features.map(f => (
                        <li key={f} className="flex items-center gap-1.5 text-xs text-fg-secondary">
                          <CheckCircleIcon className="w-3 h-3 text-brand-400 flex-shrink-0"/>{f}
                        </li>
                      ))}
                    </ul>
                  </button>
                ))}
              </div>
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-3 text-base">
              {loading ? 'Setting up ETcash…' : 'Create ETcash'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
