import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
    // Sidebar state
    sidebarOpen: boolean;
    sidebarCollapsed: boolean;
    toggleSidebar: () => void;
    openSidebar: () => void;
    closeSidebar: () => void;
    toggleSidebarCollapse: () => void;
    setSidebarCollapsed: (collapsed: boolean) => void;

    // Log panel state
    logPanelOpen: boolean;
    logPanelHeight: number;
    toggleLogPanel: () => void;
    setLogPanelOpen: (open: boolean) => void;
    setLogPanelHeight: (height: number) => void;

    // Theme state
    theme: 'light' | 'dark' | 'system';
    setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

export const useUIStore = create<UIState>()(
    persist(
        (set) => ({
            // Sidebar
            sidebarOpen: false,
            sidebarCollapsed: false,
            toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
            openSidebar: () => set({ sidebarOpen: true }),
            closeSidebar: () => set({ sidebarOpen: false }),
            toggleSidebarCollapse: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
            setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

            // Log panel
            logPanelOpen: false,
            logPanelHeight: 200,
            toggleLogPanel: () => set((state) => ({ logPanelOpen: !state.logPanelOpen })),
            setLogPanelOpen: (open) => set({ logPanelOpen: open }),
            setLogPanelHeight: (height) => set({ logPanelHeight: height }),

            // Theme
            theme: 'system',
            setTheme: (theme) => set({ theme }),
        }),
        {
            name: 'ui-preferences',
            partialize: (state) => ({
                sidebarCollapsed: state.sidebarCollapsed,
                logPanelHeight: state.logPanelHeight,
                theme: state.theme,
            }),
        }
    )
);
