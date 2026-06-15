import React, { Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { clsx } from 'clsx';

const sizes = { sm:'max-w-md', md:'max-w-2xl', lg:'max-w-4xl', xl:'max-w-6xl' };

export default function Modal({ open, onClose, title, children, size='md', footer }) {
  return (
    <Transition appear show={open} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child as={Fragment}
          enter="ease-out duration-200" enterFrom="opacity-0" enterTo="opacity-100"
          leave="ease-in duration-150" leaveFrom="opacity-100" leaveTo="opacity-0">
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm"/>
        </Transition.Child>
        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child as={Fragment}
              enter="ease-out duration-200" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100"
              leave="ease-in duration-150" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
              <Dialog.Panel className={clsx('w-full bg-surface-card border border-surface-border rounded-2xl shadow-2xl', sizes[size])}>
                <div className="flex items-center justify-between px-6 py-4 border-b border-surface-border">
                  <Dialog.Title className="text-lg font-semibold text-white">{title}</Dialog.Title>
                  <button onClick={onClose} className="text-slate-400 hover:text-slate-200 transition-colors">
                    <XMarkIcon className="w-5 h-5"/>
                  </button>
                </div>
                <div className="p-6">{children}</div>
                {footer && <div className="px-6 py-4 border-t border-surface-border flex justify-end gap-3">{footer}</div>}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
}
