import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(persist(
  (set, get) => ({
    user: null, token: null, company: null,
    mode: null, currentEntity: null,
    setAuth: (user, token) => {
      localStorage.setItem('etcash_token', token);
      set({ user, token });
    },
    setCompany: (company) => set({ company, mode: company?.mode }),
    setCurrentEntity: (entity) => {
      localStorage.setItem('etcash_entity', entity?.id ?? '');
      set({ currentEntity: entity });
    },
    logout: () => {
      localStorage.removeItem('etcash_token');
      localStorage.removeItem('etcash_entity');
      set({ user: null, token: null, company: null, mode: null, currentEntity: null });
    },
    isAuthenticated: () => !!get().token,
    canAccess: (feature) => {
      const mode = get().mode;
      const map = {
        inventory:     ['sme','multi_entity'],
        projects:      ['sme','multi_entity'],
        job_costing:   ['sme','multi_entity'],
        payroll:       ['sme','multi_entity'],
        multi_entity:  ['multi_entity'],
        consolidation: ['multi_entity'],
      };
      return map[feature] ? map[feature].includes(mode) : true;
    }
  }),
  { name: 'etcash-auth', partialize: s => ({ user: s.user, token: s.token, company: s.company, mode: s.mode }) }
));
