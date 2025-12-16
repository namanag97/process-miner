'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { cn } from '@/lib/utils';

export interface ActivityNodeData extends Record<string, unknown> {
    label: string;
    frequency: number;
    isStart: boolean;
    isEnd: boolean;
    avgDuration: number;
    maxFrequency: number;
}

interface ActivityNodeProps {
    data: ActivityNodeData;
    selected?: boolean;
}

function ActivityNodeComponent({ data, selected }: ActivityNodeProps) {
    const { label, frequency, isStart, isEnd, maxFrequency } = data;

    // Calculate size based on frequency (normalize between 120-200px width)
    const normalizedFreq = maxFrequency > 0 ? frequency / maxFrequency : 0;
    const width = Math.max(120, Math.min(200, 120 + normalizedFreq * 80));

    // Determine border color based on start/end status
    const borderStyle = isStart
        ? 'border-l-4 border-l-green-500'
        : isEnd
            ? 'border-l-4 border-l-red-500'
            : 'border-l-4 border-l-transparent';

    return (
        <div
            className={cn(
                'px-4 py-3 rounded-lg bg-card border shadow-sm transition-all',
                borderStyle,
                selected && 'ring-2 ring-primary ring-offset-2 ring-offset-background'
            )}
            style={{ minWidth: width }}
        >
            {/* Input handle (left) */}
            <Handle
                type="target"
                position={Position.Left}
                className="!bg-muted-foreground !w-2 !h-2"
            />

            {/* Content */}
            <div className="text-center">
                <p className="font-medium text-sm truncate" title={label}>
                    {label}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                    {frequency.toLocaleString()} occurrences
                </p>
            </div>

            {/* Start/End badge */}
            {(isStart || isEnd) && (
                <div className="flex justify-center gap-1 mt-2">
                    {isStart && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-700">
                            Start
                        </span>
                    )}
                    {isEnd && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-500/20 text-red-700">
                            End
                        </span>
                    )}
                </div>
            )}

            {/* Output handle (right) */}
            <Handle
                type="source"
                position={Position.Right}
                className="!bg-muted-foreground !w-2 !h-2"
            />
        </div>
    );
}

export const ActivityNode = memo(ActivityNodeComponent);
