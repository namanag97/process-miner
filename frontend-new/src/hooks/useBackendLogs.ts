/**
 * Enhanced hook for backend observability with real-time metrics
 * 
 * Features:
 * - SSE connection with auto-reconnect
 * - Real-time system metrics (CPU, memory, RPS)
 * - Circuit breaker status tracking
 * - Performance breakdown for API calls
 */
import { useEffect, useRef, useCallback, useState } from 'react';
import { devConsoleLog } from '../components/DevConsole';

// =============================================================================
// Types
// =============================================================================

interface BackendLogEntry {
  id: string;
  timestamp: string;
  level: 'info' | 'api-req' | 'api-res' | 'error' | 'action' | 'state' | 'metric' | 'perf' | 'circuit';
  source: string;
  message: string;
  data?: Record<string, unknown>;
  duration?: number;
  status?: number;
  request_id?: string;
  tags?: string[];
  timing?: {
    db_ms?: number;
    pm4py_ms?: number;
    serialize_ms?: number;
  };
}

interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  memory_mb: number;
  active_requests: number;
  requests_per_second: number;
  avg_response_time_ms: number;
  error_rate_percent: number;
  circuit_breakers: Record<string, string>;
}

interface HeartbeatMessage {
  type: 'heartbeat';
  timestamp: string;
  metrics: SystemMetrics;
  recent_errors: number;
  slow_requests: number;
}

export interface BackendObservability {
  connected: boolean;
  metrics: SystemMetrics | null;
  lastHeartbeat: Date | null;
  circuitBreakers: Record<string, 'closed' | 'open' | 'half_open'>;
  errorCount: number;
  slowRequests: number;
}

// =============================================================================
// Global State for Metrics (shared across components)
// =============================================================================

let globalMetrics: SystemMetrics | null = null;
let globalListeners: Set<() => void> = new Set();

function notifyMetricsListeners() {
  globalListeners.forEach(fn => fn());
}

export function getGlobalMetrics(): SystemMetrics | null {
  return globalMetrics;
}

export function subscribeToMetrics(listener: () => void): () => void {
  globalListeners.add(listener);
  return () => globalListeners.delete(listener);
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook that connects to backend SSE stream and provides observability data.
 * 
 * @example
 * const { connected, metrics, circuitBreakers } = useBackendLogs();
 * 
 * // Show real-time RPS
 * {metrics?.requests_per_second} req/s
 * 
 * // Show circuit breaker status
 * {circuitBreakers.pm4py === 'open' && <Alert type="warning" />}
 */
export function useBackendLogs(enabled: boolean = true): BackendObservability {
  const eventSourceRef = useRef<EventSource | null>(null);
  const seenIdsRef = useRef<Set<string>>(new Set());
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttempts = useRef(0);

  const defaultState: BackendObservability = {
    connected: false,
    metrics: null,
    lastHeartbeat: null,
    circuitBreakers: {},
    errorCount: 0,
    slowRequests: 0,
  };

  const [state, setState] = useState<BackendObservability>(defaultState);

  const connect = useCallback(() => {
    // Only in development
    if (process.env.NODE_ENV !== 'development') {
      return;
    }

    // Close existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    // Clear reconnect timeout
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8001';
      const source = new EventSource(`${apiUrl}/api/v1/dev/logs/stream`);
      eventSourceRef.current = source;

      // Handle log messages
      source.onmessage = (event) => {
        try {
          const log: BackendLogEntry = JSON.parse(event.data);
          
          // Deduplicate
          if (seenIdsRef.current.has(log.id)) {
            return;
          }
          seenIdsRef.current.add(log.id);
          
          // Trim seen IDs set
          if (seenIdsRef.current.size > 500) {
            const entries = Array.from(seenIdsRef.current);
            seenIdsRef.current = new Set(entries.slice(-250));
          }

          // Map circuit breaker logs to state level for DevConsole
          const level = log.level === 'circuit' ? 'state' : 
                       log.level === 'perf' ? 'info' :
                       log.level as 'info' | 'api-req' | 'api-res' | 'error' | 'action' | 'state';

          // Enrich data with timing breakdown
          const enrichedData = {
            ...log.data,
            ...(log.timing && {
              '⏱️ Timing': log.timing,
            }),
            ...(log.tags && log.tags.length > 0 && {
              '🏷️ Tags': log.tags,
            }),
          };

          devConsoleLog(
            level,
            log.source,
            log.message,
            Object.keys(enrichedData).length > 0 ? enrichedData : undefined,
            {
              duration: log.duration,
              status: log.status,
            }
          );
        } catch (err) {
          console.error('[BackendLogs] Failed to parse log:', err);
        }
      };

      // Handle heartbeat events
      source.addEventListener('heartbeat', (event) => {
        try {
          const heartbeat: HeartbeatMessage = JSON.parse((event as MessageEvent).data);
          
          globalMetrics = heartbeat.metrics;
          notifyMetricsListeners();
          
          setState(prev => ({
            ...prev,
            connected: true,
            metrics: heartbeat.metrics,
            lastHeartbeat: new Date(),
            circuitBreakers: heartbeat.metrics.circuit_breakers as Record<string, 'closed' | 'open' | 'half_open'>,
            errorCount: heartbeat.recent_errors,
            slowRequests: heartbeat.slow_requests,
          }));

          // Log circuit breaker alerts
          Object.entries(heartbeat.metrics.circuit_breakers).forEach(([name, state]) => {
            if (state === 'open') {
              devConsoleLog(
                'error',
                `BE Circuit:${name}`,
                `🔴 Circuit OPEN - Service degraded`,
                { circuit: name, state }
              );
            }
          });

          // Log high error rate
          if (heartbeat.metrics.error_rate_percent > 10) {
            devConsoleLog(
              'error',
              'BE Metrics',
              `⚠️ High error rate: ${heartbeat.metrics.error_rate_percent.toFixed(1)}%`,
              { metrics: heartbeat.metrics }
            );
          }

          // Log slow response time
          if (heartbeat.metrics.avg_response_time_ms > 1000) {
            devConsoleLog(
              'info',
              'BE Metrics',
              `⚡ Slow avg response: ${heartbeat.metrics.avg_response_time_ms.toFixed(0)}ms`,
              { metrics: heartbeat.metrics }
            );
          }
        } catch (err) {
          console.error('[BackendLogs] Failed to parse heartbeat:', err);
        }
      });

      source.onerror = () => {
        source.close();
        setState(prev => ({ ...prev, connected: false }));
        
        // Exponential backoff for reconnection
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
        reconnectAttempts.current++;
        
        console.log(`[BackendLogs] Reconnecting in ${delay}ms...`);
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      };

      source.onopen = () => {
        console.log('[BackendLogs] ✓ Connected to backend observability stream');
        reconnectAttempts.current = 0;
        setState(prev => ({ ...prev, connected: true }));
        
        devConsoleLog(
          'info',
          'BE Connection',
          '✓ Connected to backend observability stream',
          { url: `${apiUrl}/api/v1/dev/logs/stream` }
        );
      };
    } catch (err) {
      console.error('[BackendLogs] Failed to connect:', err);
      const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
      reconnectAttempts.current++;
      reconnectTimeoutRef.current = setTimeout(connect, delay);
    }
  }, []);

  useEffect(() => {
    // Only connect when enabled (DevConsole is open)
    if (!enabled) {
      // Clean up any existing connection when disabled
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      setState(defaultState);
      return;
    }

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect, enabled]);

  return state;
}

export default useBackendLogs;
