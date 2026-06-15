import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import { formatCurrency } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';
import DataTable from '../../components/DataTable.jsx';
import Modal from '../../components/Modal.jsx';

export default function Payroll() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();

  const { data, isLoading } = useQuery({ queryKey: ['employees'], queryFn: () => api.get('/payroll/employees/').then(r => r.data) });

  const save = useMutation({
    mutationFn: d => api.post('/payroll/employees/', { ...d, basic_salary: Number(d.basic_salary) }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['employees'] }); toast.success('Employee added'); setOpen(false); reset({}); },
  });

  const columns = [
    { header: '#', accessorKey: 'employee_number' },
    { header: 'Name', accessorKey: 'full_name' },
    { header: 'KRA PIN', accessorKey: 'kra_pin', cell: ({ getValue }) => getValue() || '—' },
    { header: 'Salary', accessorKey: 'basic_salary', cell: ({ getValue }) => formatCurrency(getValue()) },
  ];

  return (
    <div className="space-y-6">
      <PageHeader title="Employees" subtitle="Kenya payroll — PAYE, NSSF, NHIF"
        actions={<>
          <Link to="/payroll/run" className="btn-secondary">Run payroll</Link>
          <button type="button" className="btn-primary" onClick={() => setOpen(true)}>Add employee</button>
        </>}/>
      <div className="card"><DataTable data={unwrapList(data)} columns={columns} isLoading={isLoading}/></div>
      <Modal open={open} onClose={() => setOpen(false)} title="New employee" footer={<button type="button" className="btn-primary" onClick={handleSubmit(d => save.mutate(d))}>Save</button>}>
        <form className="space-y-3">
          <input className="input" placeholder="Employee # *" {...register('employee_number', { required: true })}/>
          <input className="input" placeholder="Full name *" {...register('full_name', { required: true })}/>
          <input className="input" placeholder="KRA PIN" {...register('kra_pin')}/>
          <input type="number" className="input" placeholder="Basic salary *" {...register('basic_salary', { required: true })}/>
          <input className="input" placeholder="Bank account" {...register('bank_account')}/>
        </form>
      </Modal>
    </div>
  );
}
