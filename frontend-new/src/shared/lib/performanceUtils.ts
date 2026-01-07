/**
 * Performance Utilities
 *
 * Provides debounce, throttle, and other performance optimization utilities
 * for graph visualization and high-frequency event handling.
 */

/**
 * Creates a debounced function that delays invoking func until after wait milliseconds
 * have elapsed since the last time the debounced function was invoked.
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean; maxWait?: number } = {}
): T & { cancel: () => void; flush: () => void } {
  const { leading = false, trailing = true, maxWait } = options;

  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let maxTimeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;
  let lastThis: unknown = null;
  let result: ReturnType<T> | undefined;
  let lastCallTime: number | undefined;
  let lastInvokeTime = 0;

  function invokeFunc(time: number): ReturnType<T> {
    const args = lastArgs!;
    const thisArg = lastThis;
    lastArgs = null;
    lastThis = null;
    lastInvokeTime = time;
    result = func.apply(thisArg, args) as ReturnType<T>;
    return result;
  }

  function startTimer(pendingFunc: () => void, wait: number): ReturnType<typeof setTimeout> {
    return setTimeout(pendingFunc, wait);
  }

  function cancelTimer(id: ReturnType<typeof setTimeout> | null): void {
    if (id !== null) {
      clearTimeout(id);
    }
  }

  function leadingEdge(time: number): ReturnType<T> | undefined {
    lastInvokeTime = time;
    timeoutId = startTimer(timerExpired, wait);
    return leading ? invokeFunc(time) : result;
  }

  function remainingWait(time: number): number {
    const timeSinceLastCall = time - (lastCallTime || 0);
    const timeSinceLastInvoke = time - lastInvokeTime;
    const timeWaiting = wait - timeSinceLastCall;

    return maxWait !== undefined
      ? Math.min(timeWaiting, maxWait - timeSinceLastInvoke)
      : timeWaiting;
  }

  function shouldInvoke(time: number): boolean {
    const timeSinceLastCall = time - (lastCallTime || 0);
    const timeSinceLastInvoke = time - lastInvokeTime;

    return (
      lastCallTime === undefined ||
      timeSinceLastCall >= wait ||
      timeSinceLastCall < 0 ||
      (maxWait !== undefined && timeSinceLastInvoke >= maxWait)
    );
  }

  function timerExpired(): void {
    const time = Date.now();
    if (shouldInvoke(time)) {
      return trailingEdge(time);
    }
    timeoutId = startTimer(timerExpired, remainingWait(time));
  }

  function trailingEdge(time: number): ReturnType<T> | undefined {
    timeoutId = null;

    if (trailing && lastArgs) {
      return invokeFunc(time);
    }
    lastArgs = null;
    lastThis = null;
    return result;
  }

  function cancel(): void {
    cancelTimer(timeoutId);
    cancelTimer(maxTimeoutId);
    lastInvokeTime = 0;
    lastArgs = null;
    lastCallTime = undefined;
    lastThis = null;
    timeoutId = null;
    maxTimeoutId = null;
  }

  function flush(): ReturnType<T> | undefined {
    if (timeoutId === null) {
      return result;
    }
    return trailingEdge(Date.now());
  }

  function debounced(this: unknown, ...args: Parameters<T>): ReturnType<T> | undefined {
    const time = Date.now();
    const isInvoking = shouldInvoke(time);

    lastArgs = args;
    lastThis = this;
    lastCallTime = time;

    if (isInvoking) {
      if (timeoutId === null) {
        return leadingEdge(lastCallTime);
      }
      if (maxWait !== undefined) {
        timeoutId = startTimer(timerExpired, wait);
        return invokeFunc(lastCallTime);
      }
    }
    if (timeoutId === null) {
      timeoutId = startTimer(timerExpired, wait);
    }
    return result;
  }

  debounced.cancel = cancel;
  debounced.flush = flush;

  return debounced as T & { cancel: () => void; flush: () => void };
}

/**
 * Creates a throttled function that only invokes func at most once per every wait milliseconds.
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number,
  options: { leading?: boolean; trailing?: boolean } = {}
): T & { cancel: () => void } {
  const { leading = true, trailing = true } = options;

  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  let lastArgs: Parameters<T> | null = null;
  let lastThis: unknown = null;
  let result: ReturnType<T> | undefined;
  let lastCallTime = 0;

  function invokeFunc(): ReturnType<T> {
    const args = lastArgs!;
    const thisArg = lastThis;
    lastArgs = null;
    lastThis = null;
    lastCallTime = Date.now();
    result = func.apply(thisArg, args) as ReturnType<T>;
    return result;
  }

  function trailingCall(): void {
    timeoutId = null;
    if (trailing && lastArgs) {
      invokeFunc();
    }
  }

  function cancel(): void {
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    lastArgs = null;
    lastThis = null;
    lastCallTime = 0;
  }

  function throttled(this: unknown, ...args: Parameters<T>): ReturnType<T> | undefined {
    const now = Date.now();
    const remaining = wait - (now - lastCallTime);

    lastArgs = args;
    lastThis = this;

    if (remaining <= 0 || remaining > wait) {
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
        timeoutId = null;
      }
      if (leading || lastCallTime !== 0) {
        return invokeFunc();
      }
      lastCallTime = now;
    }

    if (timeoutId === null && trailing) {
      timeoutId = setTimeout(trailingCall, remaining > 0 ? remaining : wait);
    }

    return result;
  }

  throttled.cancel = cancel;

  return throttled as T & { cancel: () => void };
}

/**
 * RequestAnimationFrame-based throttle for smooth visual updates
 */
export function rafThrottle<T extends (...args: unknown[]) => unknown>(
  func: T
): T & { cancel: () => void } {
  let rafId: number | null = null;
  let lastArgs: Parameters<T> | null = null;
  let lastThis: unknown = null;

  function invokeFunc(): void {
    rafId = null;
    if (lastArgs) {
      func.apply(lastThis, lastArgs);
      lastArgs = null;
      lastThis = null;
    }
  }

  function cancel(): void {
    if (rafId !== null) {
      cancelAnimationFrame(rafId);
      rafId = null;
    }
    lastArgs = null;
    lastThis = null;
  }

  function throttled(this: unknown, ...args: Parameters<T>): void {
    lastArgs = args;
    lastThis = this;

    if (rafId === null) {
      rafId = requestAnimationFrame(invokeFunc);
    }
  }

  throttled.cancel = cancel;

  return throttled as T & { cancel: () => void };
}

/**
 * Batches multiple calls into a single execution in the next microtask
 */
export function batchCalls<T extends (...args: unknown[]) => unknown>(
  func: T
): T & { flush: () => void } {
  let pending = false;
  let lastArgs: Parameters<T> | null = null;
  let lastThis: unknown = null;

  function flush(): void {
    if (pending && lastArgs) {
      pending = false;
      const args = lastArgs;
      const thisArg = lastThis;
      lastArgs = null;
      lastThis = null;
      func.apply(thisArg, args);
    }
  }

  function batched(this: unknown, ...args: Parameters<T>): void {
    lastArgs = args;
    lastThis = this;

    if (!pending) {
      pending = true;
      queueMicrotask(flush);
    }
  }

  batched.flush = flush;

  return batched as T & { flush: () => void };
}

/**
 * Simple memoization for expensive calculations
 */
export function memoize<T extends (...args: unknown[]) => unknown>(
  func: T,
  resolver?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();

  function memoized(this: unknown, ...args: Parameters<T>): ReturnType<T> {
    const key = resolver ? resolver(...args) : JSON.stringify(args);

    if (cache.has(key)) {
      return cache.get(key)!;
    }

    const result = func.apply(this, args) as ReturnType<T>;
    cache.set(key, result);
    return result;
  }

  return memoized as T;
}

/**
 * LRU Cache with configurable max size
 */
export class LRUCache<K, V> {
  private cache: Map<K, V>;
  private maxSize: number;

  constructor(maxSize: number = 100) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }

  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }
    // Move to end (most recently used)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    return value;
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Delete oldest (first) entry
      const firstKey = this.cache.keys().next().value;
      if (firstKey !== undefined) {
        this.cache.delete(firstKey);
      }
    }
    this.cache.set(key, value);
  }

  has(key: K): boolean {
    return this.cache.has(key);
  }

  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  get size(): number {
    return this.cache.size;
  }
}

/**
 * Visibility detection utility for page visibility API
 */
export function createVisibilityObserver(
  onVisible: () => void,
  onHidden: () => void
): { start: () => void; stop: () => void } {
  let isListening = false;

  function handleVisibilityChange(): void {
    if (document.hidden) {
      onHidden();
    } else {
      onVisible();
    }
  }

  return {
    start: () => {
      if (!isListening) {
        document.addEventListener('visibilitychange', handleVisibilityChange);
        isListening = true;
      }
    },
    stop: () => {
      if (isListening) {
        document.removeEventListener('visibilitychange', handleVisibilityChange);
        isListening = false;
      }
    },
  };
}

/**
 * Intersection observer utility for viewport detection
 */
export function createViewportObserver(
  element: Element,
  onEnterViewport: () => void,
  onLeaveViewport: () => void,
  options: IntersectionObserverInit = {}
): { disconnect: () => void } {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          onEnterViewport();
        } else {
          onLeaveViewport();
        }
      });
    },
    { threshold: 0.1, ...options }
  );

  observer.observe(element);

  return {
    disconnect: () => observer.disconnect(),
  };
}

/**
 * Performance measurement utility
 */
export function measurePerformance<T>(
  name: string,
  func: () => T
): { result: T; duration: number } {
  const start = performance.now();
  const result = func();
  const duration = performance.now() - start;

  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  }

  return { result, duration };
}

/**
 * Async performance measurement utility
 */
export async function measurePerformanceAsync<T>(
  name: string,
  func: () => Promise<T>
): Promise<{ result: T; duration: number }> {
  const start = performance.now();
  const result = await func();
  const duration = performance.now() - start;

  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${name}: ${duration.toFixed(2)}ms`);
  }

  return { result, duration };
}
