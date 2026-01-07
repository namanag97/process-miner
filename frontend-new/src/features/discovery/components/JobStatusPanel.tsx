/**
 * JobStatusPanel Component
 * 
 * Shows real-time job status with progress bar and stage information.
 * Auto-polls and stops when job completes/fails.
 */

import { useEffect } from 'react';
import { useJobStatus } from '../hooks';
import type { Job } from '@/src/api/sdk';
import styles from './JobStatusPanel.module.css';

export interface JobStatusPanelProps {
    jobId: string | null;
    onComplete?: (job: Job) => void;
    onError?: (error: Error) => void;
    onCancel?: () => void;
}

export function JobStatusPanel({
    jobId,
    onComplete,
    onError,
    onCancel
}: JobStatusPanelProps) {
    const { data: job, isPolling, stopPolling, error } = useJobStatus(jobId, {
        onComplete,
        onError,
    });

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            stopPolling();
        };
    }, [stopPolling]);

    if (!jobId) {
        return null;
    }

    if (error) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    <span className={styles.errorIcon}>⚠️</span>
                    <span>Error: {error.message}</span>
                </div>
            </div>
        );
    }

    if (!job) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    <div className={styles.spinner} />
                    <span>Loading job status...</span>
                </div>
            </div>
        );
    }

    const statusColors: Record<string, string> = {
        pending: 'var(--color-warning, #f59e0b)',
        queued: 'var(--color-warning, #f59e0b)',
        running: 'var(--color-primary, #6366f1)',
        completed: 'var(--color-success, #10b981)',
        failed: 'var(--color-error, #ef4444)',
        cancelled: 'var(--color-neutral, #6b7280)',
    };

    const statusIcons: Record<string, string> = {
        pending: '⏳',
        queued: '⏳',
        running: '🔄',
        completed: '✅',
        failed: '❌',
        cancelled: '🚫',
    };

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <span className={styles.statusIcon}>{statusIcons[job.status] || '❓'}</span>
                <span className={styles.statusText} style={{ color: statusColors[job.status] }}>
                    {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                </span>
                {isPolling && <div className={styles.pollingIndicator} />}
            </div>

            {/* Progress Bar */}
            {(job.status === 'running' || job.status === 'queued' || job.status === 'pending') && (
                <div className={styles.progressContainer}>
                    <div className={styles.progressBar}>
                        <div
                            className={styles.progressFill}
                            style={{
                                width: `${job.progress}%`,
                                backgroundColor: statusColors[job.status],
                            }}
                        />
                    </div>
                    <span className={styles.progressText}>{job.progress}%</span>
                </div>
            )}

            {/* Stage */}
            {job.stage && (
                <div className={styles.stage}>
                    Stage: {job.stage}
                </div>
            )}

            {/* Error Message */}
            {job.status === 'failed' && job.error && (
                <div className={styles.errorMessage}>
                    {job.error}
                </div>
            )}

            {/* Cancel Button */}
            {(job.status === 'running' || job.status === 'queued' || job.status === 'pending') && onCancel && (
                <button className={styles.cancelButton} onClick={onCancel}>
                    Cancel
                </button>
            )}

            {/* Completed Info */}
            {job.status === 'completed' && job.entityId && (
                <div className={styles.completedInfo}>
                    Model ready! ID: <code>{job.entityId.slice(0, 8)}...</code>
                </div>
            )}
        </div>
    );
}

export default JobStatusPanel;
