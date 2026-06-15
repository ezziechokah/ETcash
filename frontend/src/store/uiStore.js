import { create } from 'zustand';

export const useUiStore = create(set => ({
  sidebarOpen: true,
  toggleSidebar: () => set(s => ({ sidebarOpen: !s.sidebarOpen })),
  activeModal: null, modalData: null,
  openModal:  (name, data = null) => set({ activeModal: name, modalData: data }),
  closeModal: ()                  => set({ activeModal: null, modalData: null }),
}));
