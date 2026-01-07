/**
 * useJobStream - SSE hook for real-time job progress
 * 
 * Connects to /jobs/{id}/stream for Server-Sent Events.
 * Falls back to polling if SSE fails or is not supported.
 * 
 * Includes comprehensive DevConsole telemetry for debugging.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { instrumentedFetch } from '@/src/shared/design-system';
import { devLog } from '../../../../shared/ui/DevConsole';

export interface JobStreamEvent {
    job_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    progress: number;
    stage?: string;
    error?: string;
}

interface UseJobStreamOptions {
    enabled?: boolean;
    onProgress?: (event: JobStreamEvent) => void;
    onComplete?: (event: JobStreamEvent) => void;
    onError?: (event: JobStreamEvent) => void;
}

export function useJobStream(jobId: string | null, options: UseJobStreamOptions = {}) {
    const { enabled = true, onProgress, onComplete, onError } = options;
    const [jobState, setJobState] = useState<JobStreamEvent | null>(null);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState<string | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);
    const retryCountRef = useRef(0);
    const maxRetries = 3;

    const connect = useCallback(() => {
        if (!jobId || !enabled) return;

        const url = `/api/v1/jobs/${jobId}/stream`;
        devLog.action('useJobStream', `Connecting to SSE stream: ${jobId}`);

        try {
            const eventSource = new EventSource(url);
            eventSourceRef.current = eventSource;

            eventSource.onopen = () => {
                setIsConnected(true);
                setConnectionError(null);
                retryCountRef.current = 0;
                devLog.info('useJobStream', `SSE connected: ${jobId}`);
            };

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data) as JobStreamEvent;
                    setJobState(data);

                    devLog.info('useJobStream', `Job update: ${data.status} ${data.progress}%`, {
                        jobId,
                        stage: data.stage,
                    });

                    // Call appropriate callback
                    if (data.status === 'completed') {
                        onComplete?.(data);
                        eventSource.close();
                        setIsConnected(false);
                    } else if (data.status === 'failed' || data.status === 'cancelled') {
                        onError?.(data);
                        eventSource.close();
                        setIsConnected(false);
                    } else {
                        onProgress?.(data);
                    }
                } catch (e) {
                    devLog.error('useJobStream', 'Failed to parse SSE event', { error: e });
                }
            };

            eventSource.onerror = (err) => {
                devLog.error('useJobStream', 'SSE connection error', { jobId, error: err });
                setIsConnected(false);

                // Retry with backoff
                if (retryCountRef.current < maxRetries) {
                    retryCountRef.current++;
                    const delay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
                    devLog.info('useJobStream', `Retrying in ${delay}ms (attempt ${retryCountRef.current})`);
                    setTimeout(connect, delay);
                } else {
                    setConnectionError('SSE connection failed, falling back to polling');
                    devLog.error('useJobStream', 'Max retries reached, giving up');
                }

                eventSource.close();
            };

        } catch (err) {
            devLog.error('useJobStream', 'Failed to create EventSource', { error: err });
            setConnectionError('SSE not supported');
        }
    }, [jobId, enabled, onProgress, onComplete, onError]);

    // Connect when jobId changes
    useEffect(() => {
        connect();

        return () => {
            if (eventSourceRef.current) {
                devLog.action('useJobStream', 'Closing SSE connection');
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [connect]);

    // Fallback: poll if SSE fails
    useEffect(() => {
        if (!connectionError || !jobId || !enabled) return;

        devLog.info('useJobStream', 'Falling back to polling', { jobId });

        const poll = async () => {
            try {
                const response = await fetch(`/api/v1/jobs/${jobId}`);
                if (response.ok) {
                    const data = await response.json();
                    const event: JobStreamEvent = {
                        job_id: data.id,
                        status: data.status,
                        progress: data.progress || 0,
                        stage: data.stage,
                        error: data.error,
                    };
                    setJobState(event);

                    if (event.status === 'completed') {
                        onComplete?.(event);
                    } else if (event.status === 'failed') {
                        onError?.(event);
                    } else {
                        onProgress?.(event);
                    }
                }
            } catch (e) {
                devLog.error('useJobStream', 'Polling failed', { error: e });
            }
        };

        poll();
        const interval = setInterval(poll, 2000);

        return () => clearInterval(interval);
    }, [connectionError, jobId, enabled, onProgress, onComplete, onError]);

    return {
        jobState,
        isConnected,
        connectionError,
        reconnect: connect,
    };
}
