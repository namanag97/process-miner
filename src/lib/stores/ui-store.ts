import { create } from 'zustand';

interface UIState {
    // Sidebar state
    sidebarOpen: boolean;
    toggleSidebar: () => void;
    openSidebar: () => void;
    closeSidebar: () => void;

    // Theme state
    theme: 'light' | 'dark' | 'system';
    setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>((set) => ({
    // Sidebar
    sidebarOpen: false,
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    openSidebar: () => set({ sidebarOpen: true }),
    closeSidebar: () => set({ sidebarOpen: false }),

    // Theme
    theme: 'system',
    setTheme: (theme) => set({ theme }),
}));
