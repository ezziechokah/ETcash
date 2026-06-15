import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { unwrapList } from '../../utils/api.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function BankImport() {
  const qc = useQueryClient();
  const [accountId, setAccountId] = useState('');
  const [csv, setCsv] = useState('');

  const { data: accounts } = useQuery({
    queryKey: ['bank-accounts'],
    queryFn: () => api.get('/banking/accounts/').then(r => unwrapList(r.data)),
  });

  const importTxns = useMutation({
    mutationFn: async () => {
      const lines = csv.trim().split('\n').slice(1);
      for (const line of lines) {
        const [date, desc, amount, type] = line.split(',').map(s => s.trim());
        if (!date) continue;
        await api.post('/banking/transactions/', {
          account: Number(accountId),
          transaction_date: date,
          description: desc || 'Imported',
          amount: Math.abs(Number(amount)),
          txn_type: type?.toLowerCase() === 'debit' ? 'debit' : 'credit',
          reference: 'import',
        });
      }
    },
    onSuccess: () => { toast.success('Transactions imported'); setCsv(''); qc.invalidateQueries({ queryKey: ['bank-transactions'] }); },
    onError: () => toast.error('Import failed — use: date,description,amount,type'),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Bank Import" subtitle="CSV format: date,description,amount,type (credit/debit)"/>
      <div className="card space-y-4">
        <div>
          <label className="label">Bank account</label>
          <select className="input" value={accountId} onChange={e => setAccountId(e.target.value)}>
            <option value="">Select account</option>
            {(accounts || []).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">CSV data</label>
          <textarea className="input font-mono text-xs" rows={10} value={csv} onChange={e => setCsv(e.target.value)}
            placeholder={'date,description,amount,type\n2026-05-01,M-Pesa deposit,50000,credit'}/>
        </div>
        <button type="button" className="btn-primary" disabled={!accountId || !csv || importTxns.isPending}
          onClick={() => importTxns.mutate()}>
          {importTxns.isPending ? 'Importing…' : 'Import'}
        </button>
      </div>
    </div>
  );
}
