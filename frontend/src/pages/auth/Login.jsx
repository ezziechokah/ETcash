import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../../store/authStore.js';
import { api } from '../../api/client.js';
import toast from 'react-hot-toast';

export default function Login() {
  const { register, handleSubmit, formState:{errors} } = useForm();
  const [loading, setLoading] = useState(false);
  const { setAuth, setCompany } = useAuthStore();
  const navigate = useNavigate();

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      const res = await api.post('/auth/login/', data);
      setAuth(res.data.user, res.data.token);
      const compRes = await api.get('/core/company/');
      if (compRes.data?.id) {
        setCompany(compRes.data);
        navigate('/dashboard');
      } else {
        navigate('/setup');
      }
    } catch (err) {
      toast.error(err.response?.data?.non_field_errors?.[0] || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-brand-600 flex items-center justify-center mx-auto mb-4 shadow-2xl">
            <span className="text-white font-bold text-2xl">ET</span>
          </div>
          <h1 className="text-3xl font-bold text-white">ETcash</h1>
          <p className="text-slate-400 mt-1">Kenya-first Financial System</p>
        </div>
        <div className="card">
          <h2 className="text-xl font-semibold text-white mb-6">Sign in</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="label">Username</label>
              <input className={`input ${errors.username?'input-error':''}`} placeholder="Enter username"
                {...register('username', { required:'Username is required' })}/>
              {errors.username && <p className="error-msg">{errors.username.message}</p>}
            </div>
            <div>
              <label className="label">Password</label>
              <input type="password" className={`input ${errors.password?'input-error':''}`} placeholder="Enter password"
                {...register('password', { required:'Password is required' })}/>
              {errors.password && <p className="error-msg">{errors.password.message}</p>}
            </div>
            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>
          <p className="text-center text-sm text-slate-400 mt-4">
            First time? <Link to="/setup" className="text-brand-400 hover:text-brand-300">Set up ETcash</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
