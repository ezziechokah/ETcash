import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';
import toast from 'react-hot-toast';
import { api } from '../../api/client.js';
import { formatCurrency, formatDate, statusBadge } from '../../utils/format.js';
import PageHeader from '../../components/PageHeader.jsx';

export default function InvoiceDetail() {
  const { id } = useParams();
  const qc = useQueryClient();
  const { data: inv, isLoading } = useQuery({
    queryKey: ['invoice', id],
    queryFn: () => api.get(`/invoicing/invoices/${id}/`).then(r => r.data),
  });

  if (isLoading) return (
    <div className="flex justify-center py-20">
      <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
    </div>
  );
  const setStatus = useMutation({
    mutationFn: status => api.patch(`/invoicing/invoices/${id}/`, { status }),
    onSuccess: () => { toast.success('Status updated'); qc.invalidateQueries({ queryKey: ['invoice', id] }); },
  });

  const downloadPdf = () => {
    const doc = new jsPDF({ unit: 'pt', format: 'a4' });
    doc.setFontSize(18);
    doc.text('Invoice', 40, 50);
    doc.setFontSize(12);
    doc.text(`Invoice #: ${inv.invoice_number}`, 40, 80);
    doc.text(`Customer: ${inv.customer_name}`, 40, 100);
    doc.text(`Issue date: ${formatDate(inv.issue_date)}`, 40, 120);
    doc.text(`Due date: ${formatDate(inv.due_date)}`, 40, 140);
    doc.text(`Status: ${inv.status}`, 40, 160);

    autoTable(doc, {
      startY: 190,
      head: [['Description', 'Qty', 'Unit price', 'VAT %', 'Total']],
      body: (inv.lines || []).map(line => [
        line.description,
        line.quantity,
        formatCurrency(line.unit_price),
        `${line.tax_rate}%`,
        formatCurrency(line.line_total),
      ]),
      styles: { fontSize: 10, cellPadding: 6 },
      headStyles: { fillColor: [28, 46, 102] },
      alternateRowStyles: { fillColor: [245, 245, 245] },
    });

    const finalY = doc.lastAutoTable.finalY || 240;
    doc.setFontSize(12);
    doc.text(`Subtotal: ${formatCurrency(inv.subtotal)}`, 400, finalY + 40, { align: 'right' });
    doc.text(`VAT: ${formatCurrency(inv.tax_amount)}`, 400, finalY + 60, { align: 'right' });
    doc.setFontSize(14);
    doc.text(`Total: ${formatCurrency(inv.total_amount)}`, 400, finalY + 90, { align: 'right' });

    doc.save(`${inv.invoice_number || 'invoice'}.pdf`);
  };

  if (!inv) return <p className="text-slate-400">Invoice not found.</p>;

  return (
    <div className="space-y-6 max-w-3xl">
      <PageHeader title={inv.invoice_number} subtitle={inv.customer_name}
        actions={
          <div className="flex gap-2 flex-wrap">
            <button type="button" className="btn-secondary" onClick={downloadPdf}>Download PDF</button>
            {inv.status === 'sent' && <button type="button" className="btn-secondary" onClick={() => setStatus.mutate('paid')}>Mark paid</button>}
            {inv.status === 'draft' && <button type="button" className="btn-secondary" onClick={() => setStatus.mutate('sent')}>Mark sent</button>}
            <Link to={`/invoicing/invoices/${id}/edit`} className="btn-primary">Edit</Link>
          </div>
        }/>
      <div className="card space-y-4">
        <div className="flex flex-wrap gap-6 text-sm">
          <div><span className="text-slate-500">Issue date</span><p className="text-white">{formatDate(inv.issue_date)}</p></div>
          <div><span className="text-slate-500">Due date</span><p className="text-white">{formatDate(inv.due_date)}</p></div>
          <div><span className="text-slate-500">Status</span><p><span className={statusBadge(inv.status)}>{inv.status}</span></p></div>
        </div>
        {inv.notes && <p className="text-slate-400 text-sm border-t border-surface-border pt-4">{inv.notes}</p>}
      </div>
      <div className="card">
        <table className="w-full text-sm">
          <thead>
            <tr className="table-header border-b border-surface-border">
              <th className="text-left py-2">Description</th>
              <th className="text-right py-2">Qty</th>
              <th className="text-right py-2">Price</th>
              <th className="text-right py-2">VAT</th>
              <th className="text-right py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {(inv.lines || []).map(l => (
              <tr key={l.id} className="border-b border-surface-border">
                <td className="py-2 text-slate-200">{l.description}</td>
                <td className="py-2 text-right font-mono">{l.quantity}</td>
                <td className="py-2 text-right font-mono">{formatCurrency(l.unit_price)}</td>
                <td className="py-2 text-right text-slate-400">{l.tax_rate}%</td>
                <td className="py-2 text-right font-mono text-white">{formatCurrency(l.line_total)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="mt-4 pt-4 border-t border-surface-border space-y-1 text-sm text-right">
          <p className="text-slate-400">Subtotal: <span className="font-mono text-slate-200">{formatCurrency(inv.subtotal)}</span></p>
          <p className="text-slate-400">VAT: <span className="font-mono text-slate-200">{formatCurrency(inv.tax_amount)}</span></p>
          <p className="text-lg font-semibold text-white">Total: <span className="font-mono">{formatCurrency(inv.total_amount)}</span></p>
        </div>
      </div>
      <Link to="/invoicing/invoices" className="text-brand-400 text-sm hover:text-brand-300">← Back to invoices</Link>
    </div>
  );
}
