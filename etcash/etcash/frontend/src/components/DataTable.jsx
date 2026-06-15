import React, { useState } from 'react';
import {
  useReactTable, getCoreRowModel, getSortedRowModel,
  getFilteredRowModel, getPaginationRowModel, flexRender
} from '@tanstack/react-table';
import { ChevronUpIcon, ChevronDownIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

export default function DataTable({ data=[], columns, isLoading=false, pageSize=25, emptyMessage='No records found.', onRowClick }) {
  const [sorting, setSorting]   = useState([]);
  const [globalFilter, setGF]   = useState('');
  const table = useReactTable({
    data, columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGF,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize } }
  });

  if (isLoading) return (
    <div className="flex items-center justify-center py-16">
      <div className="w-8 h-8 border-2 border-surface-border border-t-brand-500 rounded-full animate-spin"/>
    </div>
  );

  return (
    <div>
      <div className="mb-3">
        <input className="input max-w-xs" placeholder="Search…"
          value={globalFilter} onChange={e => setGF(e.target.value)}/>
      </div>
      <div className="overflow-x-auto rounded-xl border border-surface-border">
        <table className="w-full">
          <thead className="bg-surface-card">
            {table.getHeaderGroups().map(hg => (
              <tr key={hg.id}>
                {hg.headers.map(h => (
                  <th key={h.id}
                    className={clsx('px-4 py-3 text-left table-header', h.column.getCanSort() && 'cursor-pointer select-none hover:text-slate-200')}
                    onClick={h.column.getToggleSortingHandler()}>
                    <div className="flex items-center gap-1">
                      {flexRender(h.column.columnDef.header, h.getContext())}
                      {h.column.getIsSorted()==='asc'  && <ChevronUpIcon   className="w-3 h-3"/>}
                      {h.column.getIsSorted()==='desc' && <ChevronDownIcon className="w-3 h-3"/>}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length === 0
              ? <tr><td colSpan={columns.length} className="text-center py-16 text-slate-500">{emptyMessage}</td></tr>
              : table.getRowModel().rows.map(row => (
                <tr key={row.id} className={clsx('table-row', onRowClick && 'cursor-pointer')}
                  onClick={() => onRowClick?.(row.original)}>
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-4 py-3 text-sm text-slate-300">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            }
          </tbody>
        </table>
      </div>
      <div className="flex items-center justify-between mt-3 text-sm text-slate-400">
        <span>{table.getFilteredRowModel().rows.length} record{table.getFilteredRowModel().rows.length!==1?'s':''}</span>
        <div className="flex items-center gap-2">
          <button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()} className="p-1 rounded hover:bg-surface-card disabled:opacity-30">
            <ChevronLeftIcon className="w-4 h-4"/>
          </button>
          <span>Page {table.getState().pagination.pageIndex+1} of {Math.max(1,table.getPageCount())}</span>
          <button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()} className="p-1 rounded hover:bg-surface-card disabled:opacity-30">
            <ChevronRightIcon className="w-4 h-4"/>
          </button>
        </div>
      </div>
    </div>
  );
}
