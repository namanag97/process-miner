/**
 * WorkflowElapsedTime - Real-time elapsed time counter for active workflows
 * 
 * Shows running time that updates every second for active workflows.
 */

import { useState, useEffect, useMemo } from 'react';
import { Typography, Space, Tag } from 'antd';
import { ClockCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { tokens } from '@/src/shared/design-system';

const { Text } = Typography;

export interface WorkflowElapsedTimeProps {
    /** When the workflow started (ISO string or Date) */
    startedAt: string | Date | null;
    /** Whether workflow is still active */
    isActive: boolean;
    /** Optional: show compact version */
    compact?: boolean;
}

/**
 * Format duration in seconds to human-readable string
 */
function formatElapsedTime(seconds: number): string {
    if (seconds < 60) {
        return `${seconds}s`;
    }
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins < 60) {
        return `${mins}m ${secs}s`;
    }
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return `${hours}h ${remainingMins}m`;
}

export function WorkflowElapsedTime({
    startedAt,
    isActive,
    compact = false,
}: WorkflowElapsedTimeProps) {
    const [elapsed, setElapsed] = useState(0);

    // Parse start time
    const startTime = useMemo(() => {
        if (!startedAt) return null;
        return typeof startedAt === 'string' ? new Date(startedAt) : startedAt;
    }, [startedAt]);

    // Update elapsed time every second while active
    useEffect(() => {
        if (!startTime || !isActive) {
            // Calculate final elapsed time if not active
            if (startTime) {
                setElapsed(Math.floor((Date.now() - startTime.getTime()) / 1000));
            }
            return;
        }

        // Initial calculation
        setElapsed(Math.floor((Date.now() - startTime.getTime()) / 1000));

        // Update every second
        const interval = setInterval(() => {
            setElapsed(Math.floor((Date.now() - startTime.getTime()) / 1000));
        }, 1000);

        return () => clearInterval(interval);
    }, [startTime, isActive]);

    if (!startTime) {
        return null;
    }

    const formattedTime = formatElapsedTime(elapsed);

    if (compact) {
        return (
            <Tag
                icon={isActive ? <LoadingOutlined spin /> : <ClockCircleOutlined />}
                color={isActive ? 'processing' : 'default'}
                style={{ marginRight: 0 }}
            >
                {formattedTime}
            </Tag>
        );
    }

    return (
        <Space size={4}>
            {isActive ? (
                <LoadingOutlined spin style={{ color: tokens.colors.primary[500] }} />
            ) : (
                <ClockCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
            )}
            <Text
                style={{
                    fontSize: 13,
                    color: isActive ? tokens.colors.primary[600] : tokens.colors.neutral[500],
                    fontVariantNumeric: 'tabular-nums',
                }}
            >
                {isActive ? 'Running for ' : 'Completed in '}
                <strong>{formattedTime}</strong>
            </Text>
        </Space>
    );
}

export default WorkflowElapsedTime;
