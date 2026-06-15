import React from 'react';

export default function ReportPeriodFilter({ from, to, onFrom, onTo, showAsOf, asOf, onAsOf }) {
  return (
    <div className="card flex flex-wrap gap-4 items-end">
      <div>
        <label className="label">From</label>
        <input type="date" className="input" value={from} onChange={e => onFrom(e.target.value)}/>
      </div>
      <div>
        <label className="label">To</label>
        <input type="date" className="input" value={to} onChange={e => onTo(e.target.value)}/>
      </div>
      {showAsOf && (
        <div>
          <label className="label">As of</label>
          <input type="date" className="input" value={asOf} onChange={e => onAsOf(e.target.value)}/>
        </div>
      )}
    </div>
  );
}
