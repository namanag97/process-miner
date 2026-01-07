/**
 * UI Store
 *
 * Manages UI state for panels, modals, and layout preferences.
 * Persists layout preferences to localStorage.
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export type RightPanelTab = 'filter' | 'variants' | 'activity' | 'edge';
export type Layout = 'horizontal' | 'vertical';
export type Theme = 'light' | 'dark' | 'system';

export interface UIState {
  // Panel state
  leftPanelOpen: boolean;
  rightPanelOpen: boolean;
  rightPanelTab: RightPanelTab;
  filterDrawerOpen: boolean;

  // Layout preferences
  layout: Layout;
  theme: Theme;

  // Zoom state
  zoomLevel: number;

  // Modal state
  activeModal: string | null;
  modalProps: Record<string, unknown>;

  // Actions - Panels
  toggleLeftPanel: () => void;
  setLeftPanelOpen: (open: boolean) => void;
  toggleRightPanel: () => void;
  setRightPanelOpen: (open: boolean) => void;
  setRightPanelTab: (tab: RightPanelTab) => void;
  toggleFilterDrawer: () => void;
  setFilterDrawerOpen: (open: boolean) => void;

  // Actions - Layout
  setLayout: (layout: Layout) => void;
  setTheme: (theme: Theme) => void;

  // Actions - Zoom
  setZoom: (level: number) => void;
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;

  // Actions - Modal
  openModal: (modalId: string, props?: Record<string, unknown>) => void;
  closeModal: () => void;

  // Reset
  resetUI: () => void;
}

const initialState = {
  leftPanelOpen: true,
  rightPanelOpen: true,
  rightPanelTab: 'filter' as RightPanelTab,
  filterDrawerOpen: false,
  layout: 'horizontal' as Layout,
  theme: 'light' as Theme,
  zoomLevel: 1,
  activeModal: null,
  modalProps: {},
};

export const useUIStore = create<UIState>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        // Panel actions
        toggleLeftPanel: () =>
          set(
            (state) => ({ leftPanelOpen: !state.leftPanelOpen }),
            false,
            'ui/toggleLeftPanel'
          ),

        setLeftPanelOpen: (open) =>
          set({ leftPanelOpen: open }, false, 'ui/setLeftPanelOpen'),

        toggleRightPanel: () =>
          set(
            (state) => ({ rightPanelOpen: !state.rightPanelOpen }),
            false,
            'ui/toggleRightPanel'
          ),

        setRightPanelOpen: (open) =>
          set({ rightPanelOpen: open }, false, 'ui/setRightPanelOpen'),

        setRightPanelTab: (tab) =>
          set({ rightPanelTab: tab }, false, 'ui/setRightPanelTab'),

        toggleFilterDrawer: () =>
          set(
            (state) => ({ filterDrawerOpen: !state.filterDrawerOpen }),
            false,
            'ui/toggleFilterDrawer'
          ),

        setFilterDrawerOpen: (open) =>
          set({ filterDrawerOpen: open }, false, 'ui/setFilterDrawerOpen'),

        // Layout actions
        setLayout: (layout) => set({ layout }, false, 'ui/setLayout'),

        setTheme: (theme) => set({ theme }, false, 'ui/setTheme'),

        // Zoom actions
        setZoom: (level) =>
          set(
            { zoomLevel: Math.max(0.1, Math.min(3, level)) },
            false,
            'ui/setZoom'
          ),

        zoomIn: () =>
          set(
            (state) => ({ zoomLevel: Math.min(3, state.zoomLevel * 1.2) }),
            false,
            'ui/zoomIn'
          ),

        zoomOut: () =>
          set(
            (state) => ({ zoomLevel: Math.max(0.1, state.zoomLevel / 1.2) }),
            false,
            'ui/zoomOut'
          ),

        resetZoom: () => set({ zoomLevel: 1 }, false, 'ui/resetZoom'),

        // Modal actions
        openModal: (modalId, props = {}) =>
          set(
            { activeModal: modalId, modalProps: props },
            false,
            'ui/openModal'
          ),

        closeModal: () =>
          set({ activeModal: null, modalProps: {} }, false, 'ui/closeModal'),

        // Reset
        resetUI: () => set(initialState, false, 'ui/reset'),
      }),
      {
        name: 'lumina-ui-store',
        // Only persist layout preferences, not transient panel state
        partialize: (state) => ({
          layout: state.layout,
          theme: state.theme,
        }),
      }
    ),
    { name: 'UIStore' }
  )
);
