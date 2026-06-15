import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar.jsx';
import TopBar from './TopBar.jsx';
import { useUiStore } from '../../store/uiStore.js';

export default function AppShell() {
  const open = useUiStore(s => s.sidebarOpen);
  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <Sidebar/>
      <div
        className="flex flex-col flex-1 overflow-hidden transition-all duration-200"
        style={{ marginLeft: open ? '16rem' : '4rem' }}
      >
        <TopBar/>
        <main className="flex-1 overflow-y-auto p-6 bg-surface">
          <Outlet/>
        </main>
      </div>
    </div>
  );
}
