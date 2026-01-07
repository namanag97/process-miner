/**
 * WorkflowProgressCard - Complete workflow progress display with elapsed time
 * 
 * Shows workflow status, progress bar, current step, and elapsed time.
 */

import { Card, Progress, Space, Typography, Tag, Button, Tooltip } from 'antd';
import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    SyncOutlined,
    PauseCircleOutlined,
    ReloadOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { WorkflowElapsedTime } from './WorkflowElapsedTime';

// Inline type definition (from deleted useWorkflowPolling hook)
export type WorkflowStatus =
    | 'pending'
    | 'running'
    | 'completed'
    | 'failed'
    | 'cancelled'
    | 'timed_out';

export interface WorkflowProgress {
    /** Workflow ID */
    workflowId: string;
    /** Current status */
    status: WorkflowStatus;
    /** Progress percentage (0-100) */
    progressPercent: number;
    /** Human-readable current step */
    currentStep: string | null;
    /** Error message if failed */
    errorMessage: string | null;
    /** Whether workflow is still in progress */
    isActive: boolean;
    /** Whether workflow completed successfully */
    isComplete: boolean;
    /** Whether workflow failed */
    isFailed: boolean;
    /** Refetch function */
    refetch: () => void;
}

const { Text, Title } = Typography;

export interface WorkflowProgressCardProps {
    /** Workflow progress data from useWorkflowPolling */
    progress: WorkflowProgress | null;
    /** Title for the card */
    title?: string;
    /** When workflow started (for elapsed time) */
    startedAt?: string | Date | null;
    /** Callback to retry failed workflow */
    onRetry?: () => void;
    /** Callback when workflow completes */
    onComplete?: () => void;
    /** Show compact version */
    compact?: boolean;
}

const STATUS_CONFIG = {
    pending: {
        color: 'default',
        icon: <PauseCircleOutlined />,
        label: 'Pending',
    },
    running: {
        color: 'processing',
        icon: <SyncOutlined spin />,
        label: 'Running',
    },
    completed: {
        color: 'success',
        icon: <CheckCircleOutlined />,
        label: 'Completed',
    },
    failed: {
        color: 'error',
        icon: <CloseCircleOutlined />,
        label: 'Failed',
    },
    cancelled: {
        color: 'warning',
        icon: <PauseCircleOutlined />,
        label: 'Cancelled',
    },
    timed_out: {
        color: 'error',
        icon: <CloseCircleOutlined />,
        label: 'Timed Out',
    },
} as const;

export function WorkflowProgressCard({
    progress,
    title = 'Workflow Progress',
    startedAt,
    onRetry,
    onComplete,
    compact = false,
}: WorkflowProgressCardProps) {
    if (!progress) {
        return null;
    }

    const statusConfig = STATUS_CONFIG[progress.status] || STATUS_CONFIG.pending;

    // Call onComplete when status changes to completed
    if (progress.isComplete && onComplete) {
        onComplete();
    }

    if (compact) {
        return (
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: tokens.spacing[3],
                    padding: tokens.spacing[3],
                    backgroundColor: tokens.colors.neutral[50],
                    borderRadius: tokens.radius.md,
                    border: `1px solid ${tokens.colors.neutral[200]}`,
                }}
            >
                <Tag
                    icon={statusConfig.icon}
                    color={statusConfig.color as string}
                    style={{ marginRight: 0 }}
                >
                    {statusConfig.label}
                </Tag>
                <Progress
                    percent={progress.progressPercent}
                    size="small"
                    style={{ flex: 1, marginBottom: 0 }}
                    status={progress.isFailed ? 'exception' : progress.isComplete ? 'success' : 'active'}
                />
                <WorkflowElapsedTime
                    startedAt={startedAt || null}
                    isActive={progress.isActive}
                    compact
                />
            </div>
        );
    }

    return (
        <Card
            size="small"
            style={{
                borderColor: progress.isFailed
                    ? tokens.colors.error[300]
                    : progress.isComplete
                        ? tokens.colors.success[300]
                        : tokens.colors.neutral[200],
            }}
        >
            <Space direction="vertical" style={{ width: '100%' }} size={12}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Title level={5} style={{ margin: 0 }}>
                        {title}
                    </Title>
                    <Tag
                        icon={statusConfig.icon}
                        color={statusConfig.color as string}
                        style={{ marginRight: 0 }}
                    >
                        {statusConfig.label}
                    </Tag>
                </div>

                {/* Progress bar */}
                <Progress
                    percent={progress.progressPercent}
                    status={progress.isFailed ? 'exception' : progress.isComplete ? 'success' : 'active'}
                    strokeColor={
                        progress.isActive
                            ? {
                                '0%': tokens.colors.primary[400],
                                '100%': tokens.colors.primary[600],
                            }
                            : undefined
                    }
                />

                {/* Current step */}
                {progress.currentStep && (
                    <Text
                        style={{
                            color: tokens.colors.neutral[600],
                            fontSize: 13,
                        }}
                    >
                        {progress.currentStep}
                    </Text>
                )}

                {/* Elapsed time */}
                <WorkflowElapsedTime startedAt={startedAt || null} isActive={progress.isActive} />

                {/* Error message */}
                {progress.errorMessage && (
                    <div
                        style={{
                            padding: tokens.spacing[3],
                            backgroundColor: tokens.colors.error[50],
                            borderRadius: tokens.radius.sm,
                            border: `1px solid ${tokens.colors.error[200]}`,
                        }}
                    >
                        <Text style={{ color: tokens.colors.error[600], fontSize: 13 }}>
                            {progress.errorMessage}
                        </Text>
                    </div>
                )}

                {/* Retry button for failed workflows */}
                {progress.isFailed && onRetry && (
                    <Tooltip title="Retry this workflow">
                        <Button
                            type="primary"
                            danger
                            icon={<ReloadOutlined />}
                            onClick={onRetry}
                            block
                        >
                            Retry
                        </Button>
                    </Tooltip>
                )}
            </Space>
        </Card>
    );
}

export default WorkflowProgressCard;
