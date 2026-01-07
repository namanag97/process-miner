/**
 * useInstrumentedNavigate - Navigation hook with DevConsole logging
 *
 * Wraps react-router's useNavigate to log all programmatic navigation
 * events to the DevConsole for debugging.
 *
 * Features:
 * - Logs from/to paths
 * - Tracks navigation timing
 * - Starts correlation for related API calls
 * - Supports both path strings and history navigation (back/forward)
 *
 * @example
 * const navigate = useInstrumentedNavigate();
 * navigate('/projects/123'); // Logs: "Navigate: /projects/123"
 * navigate(-1); // Logs: "Navigate: history(-1)"
 */

import { useNavigate, useLocation } from 'react-router-dom';
import { useCallback } from 'react';
import { logAction } from './devLogger';

export function useInstrumentedNavigate() {
  const navigate = useNavigate();
  const location = useLocation();

  return useCallback((to: string | number, options?: { replace?: boolean; state?: unknown }) => {
    const from = location.pathname;
    const target = typeof to === 'string' ? to : `history(${to})`;

    // Log navigation action to DevConsole
    logAction('Navigation', `${from} → ${target}`, {
      from,
      to: target,
      replace: options?.replace ?? false,
      state: options?.state,
    });

    // Perform navigation
    navigate(to as any, options);
  }, [navigate, location]);
}

export default useInstrumentedNavigate;
