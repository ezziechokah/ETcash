import numeral from 'numeral';
import { format, parseISO, isValid } from 'date-fns';

export const formatCurrency = (amount, currency = 'KES') => {
  if (amount === null || amount === undefined) return `${currency} 0.00`;
  return `${currency} ${numeral(amount).format('0,0.00')}`;
};

export const formatDate = (date, fmt = 'dd MMM yyyy') => {
  if (!date) return '—';
  try {
    const d = typeof date === 'string' ? parseISO(date) : date;
    return isValid(d) ? format(d, fmt) : String(date);
  } catch { return String(date); }
};

export const formatNumber  = v => numeral(v).format('0,0.00');
export const formatPercent = v => `${numeral(v).format('0.00')}%`;
export const formatInt     = v => numeral(v).format('0,0');

export const statusBadge = status => ({
  draft:'badge-gray', sent:'badge-blue', paid:'badge-green',
  overdue:'badge-red', partial:'badge-yellow', void:'badge-gray',
  posted:'badge-green', pending:'badge-yellow', approved:'badge-green',
  rejected:'badge-red', active:'badge-green', inactive:'badge-gray',
  reconciled:'badge-green', open:'badge-blue', closed:'badge-gray',
  'in_progress':'badge-yellow', completed:'badge-green', cancelled:'badge-red',
}[status] || 'badge-gray');
