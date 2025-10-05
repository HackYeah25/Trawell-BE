import { create } from 'zustand';

interface ToastMessage {
  id: string;
  title: string;
  description?: string;
  variant?: 'default' | 'destructive' | 'success';
}

interface UIStore {
  // Modals
  isCreateProjectModalOpen: boolean;
  isCreateTripModalOpen: boolean;
  selectedProjectForTrip: string | null;

  // Toasts
  toasts: ToastMessage[];

  // Navigation
  sidebarCollapsed: boolean;

  // Actions
  openCreateProjectModal: () => void;
  closeCreateProjectModal: () => void;
  openCreateTripModal: (projectId?: string) => void;
  closeCreateTripModal: () => void;
  toggleSidebar: () => void;
  addToast: (toast: Omit<ToastMessage, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useUIStore = create<UIStore>((set) => ({
  // Initial state
  isCreateProjectModalOpen: false,
  isCreateTripModalOpen: false,
  selectedProjectForTrip: null,
  toasts: [],
  sidebarCollapsed: false,

  // Actions
  openCreateProjectModal: () => set({ isCreateProjectModalOpen: true }),
  closeCreateProjectModal: () => set({ isCreateProjectModalOpen: false }),

  openCreateTripModal: (projectId) =>
    set({
      isCreateTripModalOpen: true,
      selectedProjectForTrip: projectId || null,
    }),

  closeCreateTripModal: () =>
    set({
      isCreateTripModalOpen: false,
      selectedProjectForTrip: null,
    }),

  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  addToast: (toast) =>
    set((state) => ({
      toasts: [...state.toasts, { ...toast, id: Math.random().toString(36) }],
    })),

  removeToast: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
