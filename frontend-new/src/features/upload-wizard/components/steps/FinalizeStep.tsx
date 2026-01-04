/**
 * FinalizeStep - Step 5: Processing progress with animated indicators
 * 
 * Shows real-time processing status:
 * - Transforming your data ✓
 * - Creating Data Model ✓
 * - Loading Process Data Model (in progress)
 * - Finishing up
 * 
 * Includes comprehensive DevConsole telemetry for debugging
 */

import { useEffect, useState } from 'react';
import { Card, Typography, Progress, Spin, Alert, Button, Steps, Result } from 'antd';
import {
    LoadingOutlined,
    CheckCircleOutlined,
    SyncOutlined,
    ClockCircleOutlined,
    ExclamationCircleOutlined,
} from '@ant-design/icons';
import { tokens, logAction } from '@lumina/design-system';
import { devLog } from '../../../../components/DevConsole';

const { Title, Text } = Typography;

interface JobStatus {
    id: string;
    status: string; // 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
    progress?: number;
    error?: string;
    result?: Record<string, unknown>;
}

interface FinalizeStepProps {
    jobId: string | null;
    jobStatus: JobStatus | undefined;
    datasetId: string;
    projectId: string;
    onComplete: () => void;
    onRetry: () => void;
}

const PROCESSING_STEPS = [
    { title: 'Transforming your data', key: 'transform' },
    { title: 'Creating Data Model', key: 'model' },
    { title: 'Loading Process Data Model', key: 'load' },
    { title: 'Finishing up', key: 'finish' },
];

function getProcessingStep(progress?: number): number {
    if (!progress) return 0;
    if (progress < 25) return 0;
    if (progress < 50) return 1;
    if (progress < 75) return 2;
    return 3;
}

export function FinalizeStep({
    jobId,
    jobStatus,
    datasetId,
    projectId,
    onComplete,
    onRetry,
}: FinalizeStepProps) {
    const [elapsedTime, setElapsedTime] = useState(0);
    const [lastLoggedProgress, setLastLoggedProgress] = useState(-1);

    // Timer for elapsed time
    useEffect(() => {
        const interval = setInterval(() => {
            setElapsedTime(prev => prev + 1);
        }, 1000);

        return () => clearInterval(interval);
    }, []);

    // Comprehensive telemetry logging
    useEffect(() => {
        if (jobStatus) {
            const progress = jobStatus.progress || 0;

            // Log progress changes to DevConsole
            if (progress !== lastLoggedProgress) {
                devLog.info('FinalizeStep', `Job ${jobId} progress: ${progress}%`, {
                    status: jobStatus.status,
                    progress,
                    elapsed: elapsedTime,
                    step: PROCESSING_STEPS[getProcessingStep(progress)]?.title,
                });
                setLastLoggedProgress(progress);
            }

            // Log state changes
            if (jobStatus.status === 'completed') {
                devLog.info('FinalizeStep', `✅ Job ${jobId} completed successfully`, {
                    result: jobStatus.result,
                    totalTime: elapsedTime,
                });
                logAction('UploadWizard', 'processing_complete', {
                    jobId,
                    datasetId,
                    duration: elapsedTime
                });
            } else if (jobStatus.status === 'failed') {
                devLog.error('FinalizeStep', `❌ Job ${jobId} failed: ${jobStatus.error}`, {
                    error: jobStatus.error,
                    elapsed: elapsedTime,
                });
                logAction('UploadWizard', 'processing_failed', {
                    jobId,
                    error: jobStatus.error
                });
            }
        }
    }, [jobStatus, jobId, elapsedTime, lastLoggedProgress, datasetId]);

    // Initial log
    useEffect(() => {
        devLog.action('FinalizeStep', `Started processing job: ${jobId}`, { datasetId, projectId });
    }, [jobId, datasetId, projectId]);

    // Detect stuck jobs (possible infrastructure issue like missing Celery worker)
    const [stuckWarning, setStuckWarning] = useState(false);
    useEffect(() => {
        // Check if job has been stuck at 0% for 30+ seconds
        if (elapsedTime >= 30 && (!jobStatus?.progress || jobStatus.progress === 0) && jobStatus?.status !== 'completed' && jobStatus?.status !== 'failed') {
            if (!stuckWarning) {
                setStuckWarning(true);
                devLog.error('FinalizeStep', '⚠️ INFRASTRUCTURE ALERT: Job appears stuck at 0%', {
                    jobId,
                    elapsedTime,
                    status: jobStatus?.status,
                    possibleCause: 'Celery worker may not be running',
                    resolution: 'Start worker: celery -A src.infrastructure.tasks worker --loglevel=info',
                });
                logAction('UploadWizard', 'job_stuck_warning', { jobId, elapsedTime });
            }
        }
    }, [elapsedTime, jobStatus, stuckWarning, jobId]);

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
    };

    const isComplete = jobStatus?.status === 'completed';
    const isFailed = jobStatus?.status === 'failed';
    const progress = jobStatus?.progress || 0;
    const currentProcessingStep = getProcessingStep(progress);

    // Completed state
    if (isComplete) {
        return (
            <Result
                status="success"
                title="Processing Complete!"
                subTitle="Your data has been successfully analyzed and is ready for exploration."
                extra={[
                    <Button type="primary" size="large" key="explore" onClick={onComplete}>
                        Start Exploring
                    </Button>,
                ]}
            />
        );
    }

    // Failed state
    if (isFailed) {
        return (
            <Result
                status="error"
                title="Processing Failed"
                subTitle={jobStatus?.error || 'An error occurred during processing.'}
                extra={[
                    <Button type="primary" key="retry" onClick={onRetry}>
                        Try Again
                    </Button>,
                ]}
            />
        );
    }

    // Processing state
    return (
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <div style={{ textAlign: 'center', marginBottom: tokens.spacing[6] }}>
                <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
                <Title level={3} style={{ marginTop: tokens.spacing[4] }}>
                    Processing Your Data
                </Title>
                <Text type="secondary">
                    This may take a few moments depending on the file size.
                    You can navigate away - processing will continue in the background.
                </Text>
            </div>

            {/* Progress bar */}
            <Card style={{ marginBottom: tokens.spacing[4] }}>
                <Progress
                    percent={progress}
                    status="active"
                    strokeColor={{
                        '0%': tokens.colors.primary[400],
                        '100%': tokens.colors.primary[600],
                    }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: tokens.spacing[2] }}>
                    <Text type="secondary">Time elapsed: {formatTime(elapsedTime)}</Text>
                    <Text type="secondary">Job ID: {jobId?.slice(0, 8)}...</Text>
                </div>
            </Card>

            {/* Processing steps */}
            <Card size="small">
                <Steps
                    direction="vertical"
                    current={currentProcessingStep}
                    items={PROCESSING_STEPS.map((step, idx) => ({
                        title: step.title,
                        icon: idx < currentProcessingStep
                            ? <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />
                            : idx === currentProcessingStep
                                ? <SyncOutlined spin style={{ color: tokens.colors.primary[500] }} />
                                : <ClockCircleOutlined style={{ color: tokens.colors.neutral[400] }} />,
                        status: idx < currentProcessingStep
                            ? 'finish'
                            : idx === currentProcessingStep
                                ? 'process'
                                : 'wait',
                    }))}
                />
            </Card>

            {/* Stuck job warning */}
            {stuckWarning && (
                <Alert
                    type="warning"
                    icon={<ExclamationCircleOutlined />}
                    message="Processing appears stuck"
                    description={
                        <div>
                            Job has been at 0% for {formatTime(elapsedTime)}.
                            This may indicate the background worker is not running.
                            <br />
                            <Text code style={{ marginTop: 8, display: 'block' }}>
                                Check: celery worker status
                            </Text>
                        </div>
                    }
                    style={{ marginTop: tokens.spacing[4] }}
                />
            )}

            <Alert
                type="info"
                message="Background Processing"
                description="You can safely navigate away. Come back anytime to check progress or start exploring once complete."
                style={{ marginTop: tokens.spacing[4] }}
            />
        </div>
    );
}
