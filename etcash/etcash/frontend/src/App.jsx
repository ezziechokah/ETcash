import React, { useEffect, useState } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { initApiClient } from './api/client.js';
import AppRoutes from './routes.jsx';

function Splash() {
  return (
    <div className="fixed inset-0 bg-surface flex flex-col items-center justify-center gap-6">
      <div className="w-20 h-20 rounded-2xl bg-brand-600 flex items-center justify-center shadow-2xl">
        <span className="text-white font-bold text-3xl">ET</span>
      </div>
      <div className="text-center">
        <h1 className="text-3xl font-bold text-white">ETcash</h1>
        <p className="text-slate-400 mt-1 text-sm">Kenya-first Financial System</p>
      </div>
      <div className="flex gap-1.5">
        {[0,1,2].map(i => (
          <div key={i} className="w-2 h-2 rounded-full bg-brand-500 animate-bounce"
            style={{ animationDelay: `${i*0.15}s` }}/>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [ready, setReady] = useState(false);
  useEffect(() => { initApiClient().then(() => setReady(true)); }, []);
  if (!ready) return <Splash />;
  return <BrowserRouter><AppRoutes /></BrowserRouter>;
}
