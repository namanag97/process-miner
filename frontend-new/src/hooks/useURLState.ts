/**
 * useURLState - Hook to sync state with URL search params
 * Enables bookmarkable/shareable state for filters, selections, etc.
 */

import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

type URLStateValue = string | number | boolean | null | undefined;
type URLState = Record<string, URLStateValue>;

/**
 * Parse a URL param value back to its original type
 */
function parseValue(value: string | null, defaultValue: URLStateValue): URLStateValue {
  if (value === null || value === undefined) {
    return defaultValue;
  }
  
  // Boolean
  if (value === 'true') return true;
  if (value === 'false') return false;
  
  // Number
  if (typeof defaultValue === 'number') {
    const num = parseFloat(value);
    return isNaN(num) ? defaultValue : num;
  }
  
  // String
  return value;
}

/**
 * Serialize a value for URL storage
 */
function serializeValue(value: URLStateValue): string | undefined {
  if (value === null || value === undefined) {
    return undefined;
  }
  return String(value);
}

export interface UseURLStateOptions {
  /** Replace history instead of pushing (default: false) */
  replace?: boolean;
  /** Clear other params not in defaults (default: false) */
  exclusive?: boolean;
}

/**
 * Hook to sync state with URL search params
 * 
 * @example
 * ```tsx
 * const [state, setState] = useURLState({
 *   tab: 'performance',
 *   page: 1,
 *   showFilters: false,
 * });
 * 
 * // Access state
 * console.log(state.tab); // 'performance'
 * 
 * // Update state (also updates URL)
 * setState({ tab: 'rework' });
 * setState({ page: 2, showFilters: true });
 * ```
 */
export function useURLState<T extends URLState>(
  defaults: T,
  options: UseURLStateOptions = {}
): [T, (updates: Partial<T>) => void] {
  const [searchParams, setSearchParams] = useSearchParams();
  const { replace = false } = options;

  // Parse current URL state with defaults
  const state = useMemo(() => {
    const result = { ...defaults };
    
    for (const key of Object.keys(defaults)) {
      const urlValue = searchParams.get(key);
      result[key as keyof T] = parseValue(urlValue, defaults[key]) as T[keyof T];
    }
    
    return result;
  }, [searchParams, defaults]);

  // Update URL state
  const setState = useCallback(
    (updates: Partial<T>) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          
          for (const [key, value] of Object.entries(updates)) {
            const serialized = serializeValue(value);
            const defaultValue = serializeValue(defaults[key]);
            
            if (serialized === undefined || serialized === defaultValue) {
              // Remove if undefined or matches default (keep URL clean)
              next.delete(key);
            } else {
              next.set(key, serialized);
            }
          }
          
          return next;
        },
        { replace }
      );
    },
    [setSearchParams, defaults, replace]
  );

  return [state, setState];
}

/**
 * Helper to get a single URL param with type safety
 */
export function useURLParam<T extends URLStateValue>(
  key: string,
  defaultValue: T
): [T, (value: T) => void] {
  const [state, setState] = useURLState({ [key]: defaultValue });
  
  const setValue = useCallback(
    (value: T) => setState({ [key]: value } as Partial<{ [x: string]: T }>),
    [key, setState]
  );
  
  return [state[key] as T, setValue];
}
