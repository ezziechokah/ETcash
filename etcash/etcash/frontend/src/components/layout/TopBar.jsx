import React, { Fragment } from 'react';
import { useAuthStore } from '../../store/authStore.js';
import { useNavigate } from 'react-router-dom';
import { BellIcon, UserCircleIcon, ArrowRightOnRectangleIcon } from '@heroicons/react/24/outline';
import { Menu, Transition } from '@headlessui/react';
import { api } from '../../api/client.js';

export default function TopBar() {
  const { user, currentEntity, logout } = useAuthStore();
  const navigate = useNavigate();
  const handleLogout = async () => {
    try { await api.post('/auth/logout/'); } catch {}
    logout();
    navigate('/login');
  };
  return (
    <header className="h-14 bg-surface-card border-b border-surface-border flex items-center px-6 gap-4 flex-shrink-0">
      {currentEntity && (
        <div className="text-sm text-slate-400">
          <span className="text-slate-500">Entity: </span>
          <span className="text-slate-200 font-medium">{currentEntity.name}</span>
        </div>
      )}
      <div className="flex-1"/>
      <div className="text-xs text-slate-500 hidden md:block">FY {new Date().getFullYear()}</div>
      <button className="text-slate-400 hover:text-slate-200 transition-colors">
        <BellIcon className="w-5 h-5"/>
      </button>
      <Menu as="div" className="relative">
        <Menu.Button className="flex items-center gap-2 text-slate-400 hover:text-slate-200 transition-colors">
          <UserCircleIcon className="w-6 h-6"/>
          <span className="text-sm hidden md:block">{user?.username}</span>
        </Menu.Button>
        <Transition as={Fragment}
          enter="transition ease-out duration-100" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
          leave="transition ease-in duration-75"  leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
          <Menu.Items className="absolute right-0 mt-2 w-52 bg-surface-card border border-surface-border rounded-xl shadow-xl z-50 py-1 focus:outline-none">
            <div className="px-4 py-3 border-b border-surface-border">
              <p className="text-sm font-medium text-slate-200">{user?.username}</p>
              <p className="text-xs text-slate-400">{user?.email}</p>
            </div>
            <Menu.Item>{({ active }) => (
              <button onClick={handleLogout}
                className={`flex items-center gap-2 w-full px-4 py-2 text-sm transition-colors ${active ? 'bg-surface-border text-red-400' : 'text-slate-400'}`}>
                <ArrowRightOnRectangleIcon className="w-4 h-4"/>Sign out
              </button>
            )}</Menu.Item>
          </Menu.Items>
        </Transition>
      </Menu>
    </header>
  );
}
