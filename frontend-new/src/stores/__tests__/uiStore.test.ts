/**
 * UI Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import { useUIStore } from '../uiStore';

// Reset store between tests
beforeEach(() => {
  act(() => {
    useUIStore.getState().resetUI();
  });
});

describe('uiStore', () => {
  describe('initial state', () => {
    it('should have default panel states', () => {
      const { result } = renderHook(() => useUIStore());
      expect(result.current.leftPanelOpen).toBe(true);
      expect(result.current.rightPanelOpen).toBe(true);
      expect(result.current.rightPanelTab).toBe('filter');
      expect(result.current.filterDrawerOpen).toBe(false);
    });

    it('should have default layout', () => {
      const { result } = renderHook(() => useUIStore());
      expect(result.current.layout).toBe('horizontal');
      expect(result.current.theme).toBe('light');
      expect(result.current.zoomLevel).toBe(1);
    });

    it('should have no active modal', () => {
      const { result } = renderHook(() => useUIStore());
      expect(result.current.activeModal).toBeNull();
      expect(result.current.modalProps).toEqual({});
    });
  });

  describe('panel actions', () => {
    it('toggleLeftPanel should toggle left panel', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleLeftPanel();
      });
      expect(result.current.leftPanelOpen).toBe(false);

      act(() => {
        result.current.toggleLeftPanel();
      });
      expect(result.current.leftPanelOpen).toBe(true);
    });

    it('setLeftPanelOpen should set panel state', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setLeftPanelOpen(false);
      });
      expect(result.current.leftPanelOpen).toBe(false);
    });

    it('toggleRightPanel should toggle right panel', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleRightPanel();
      });
      expect(result.current.rightPanelOpen).toBe(false);

      act(() => {
        result.current.toggleRightPanel();
      });
      expect(result.current.rightPanelOpen).toBe(true);
    });

    it('setRightPanelTab should change tab', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setRightPanelTab('variants');
      });
      expect(result.current.rightPanelTab).toBe('variants');

      act(() => {
        result.current.setRightPanelTab('activity');
      });
      expect(result.current.rightPanelTab).toBe('activity');
    });

    it('toggleFilterDrawer should toggle drawer', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.toggleFilterDrawer();
      });
      expect(result.current.filterDrawerOpen).toBe(true);

      act(() => {
        result.current.toggleFilterDrawer();
      });
      expect(result.current.filterDrawerOpen).toBe(false);
    });
  });

  describe('layout actions', () => {
    it('setLayout should change layout', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setLayout('vertical');
      });
      expect(result.current.layout).toBe('vertical');
    });

    it('setTheme should change theme', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setTheme('dark');
      });
      expect(result.current.theme).toBe('dark');
    });
  });

  describe('zoom actions', () => {
    it('setZoom should set zoom level', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setZoom(1.5);
      });
      expect(result.current.zoomLevel).toBe(1.5);
    });

    it('setZoom should clamp to valid range', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setZoom(10); // Above max
      });
      expect(result.current.zoomLevel).toBe(3);

      act(() => {
        result.current.setZoom(0.01); // Below min
      });
      expect(result.current.zoomLevel).toBe(0.1);
    });

    it('zoomIn should increase zoom by 20%', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.zoomIn();
      });
      expect(result.current.zoomLevel).toBeCloseTo(1.2);
    });

    it('zoomOut should decrease zoom by ~17%', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.zoomOut();
      });
      expect(result.current.zoomLevel).toBeCloseTo(0.833, 2);
    });

    it('zoomIn should not exceed max zoom', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setZoom(2.9);
        result.current.zoomIn();
      });
      expect(result.current.zoomLevel).toBe(3);
    });

    it('zoomOut should not go below min zoom', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setZoom(0.15);
        result.current.zoomOut();
      });
      expect(result.current.zoomLevel).toBeCloseTo(0.125);
    });

    it('resetZoom should reset to 1', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.setZoom(2);
        result.current.resetZoom();
      });
      expect(result.current.zoomLevel).toBe(1);
    });
  });

  describe('modal actions', () => {
    it('openModal should set modal and props', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.openModal('confirm-delete', { itemId: '123', itemName: 'Test' });
      });

      expect(result.current.activeModal).toBe('confirm-delete');
      expect(result.current.modalProps).toEqual({ itemId: '123', itemName: 'Test' });
    });

    it('openModal without props should use empty object', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.openModal('settings');
      });

      expect(result.current.activeModal).toBe('settings');
      expect(result.current.modalProps).toEqual({});
    });

    it('closeModal should clear modal state', () => {
      const { result } = renderHook(() => useUIStore());

      act(() => {
        result.current.openModal('confirm-delete', { itemId: '123' });
        result.current.closeModal();
      });

      expect(result.current.activeModal).toBeNull();
      expect(result.current.modalProps).toEqual({});
    });
  });

  describe('resetUI', () => {
    it('should reset all UI state to defaults', () => {
      const { result } = renderHook(() => useUIStore());

      // Change various states
      act(() => {
        result.current.toggleLeftPanel();
        result.current.toggleRightPanel();
        result.current.setRightPanelTab('variants');
        result.current.setLayout('vertical');
        result.current.setZoom(2);
        result.current.openModal('test-modal');
      });

      // Reset
      act(() => {
        result.current.resetUI();
      });

      // Verify all reset
      expect(result.current.leftPanelOpen).toBe(true);
      expect(result.current.rightPanelOpen).toBe(true);
      expect(result.current.rightPanelTab).toBe('filter');
      expect(result.current.layout).toBe('horizontal');
      expect(result.current.zoomLevel).toBe(1);
      expect(result.current.activeModal).toBeNull();
    });
  });
});
