/**
 * devTrace - Frontend function tracing for DevConsole
 * 
 * Usage:
 *   import { trace } from '../utils/devTrace';
 *   
 *   function MyComponent() {
 *     trace('MyComponent.render', { props });
 *     ...
 *   }
 * 
 *   // Or wrap a function:
 *   const fetchData = traced('fetchData', async (id) => {
 *     return await api.get(id);
 *   });
 */

import { devConsoleLog } from '../components/DevConsole';

/**
 * Log a trace event to DevConsole
 */
export function trace(name: string, data?: unknown): void {
    if (process.env.NODE_ENV !== 'development') return;
    devConsoleLog('info', name, 'called', data);
}

/**
 * Wrap a function with tracing
 */
export function traced<T extends (...args: unknown[]) => unknown>(
    name: string,
    fn: T
): T {
    if (process.env.NODE_ENV !== 'development') return fn;

    return ((...args: Parameters<T>) => {
        const start = performance.now();
        trace(`${name} [ENTER]`, { args: args.slice(0, 3) });

        try {
            const result = fn(...args);

            // Handle promises
            if (result instanceof Promise) {
                return result
                    .then((val) => {
                        const duration = (performance.now() - start).toFixed(2);
                        trace(`${name} [EXIT]`, { duration: `${duration}ms`, result: String(val).slice(0, 100) });
                        return val;
                    })
                    .catch((err) => {
                        const duration = (performance.now() - start).toFixed(2);
                        trace(`${name} [ERROR]`, { duration: `${duration}ms`, error: String(err) });
                        throw err;
                    });
            }

            const duration = (performance.now() - start).toFixed(2);
            trace(`${name} [EXIT]`, { duration: `${duration}ms` });
            return result;
        } catch (err) {
            const duration = (performance.now() - start).toFixed(2);
            trace(`${name} [ERROR]`, { duration: `${duration}ms`, error: String(err) });
            throw err;
        }
    }) as T;
}

export default { trace, traced };
