'use client';

import { memo } from 'react';
import {
    BaseEdge,
    EdgeLabelRenderer,
    getBezierPath,
    type EdgeProps,
} from '@xyflow/react';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { formatDuration } from '@/lib/utils';

export interface ProcessEdgeData extends Record<string, unknown> {
    frequency: number;
    avgDuration: number;
    caseCount: number;
    maxFrequency: number;
}

function ProcessEdgeComponent({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data,
    selected,
}: EdgeProps) {
    const edgeData = data as ProcessEdgeData | undefined;
    // Backend DFG edges only have frequency and avgDuration - caseCount and maxFrequency may be undefined
    const frequency = edgeData?.frequency ?? 1;
    const avgDuration = edgeData?.avgDuration ?? 0;
    const caseCount = edgeData?.caseCount ?? frequency; // Fallback to frequency if caseCount not available
    const maxFrequency = edgeData?.maxFrequency ?? 1;

    // Calculate edge thickness based on frequency (1-8px)
    const normalizedFreq = maxFrequency > 0 ? frequency / maxFrequency : 0;
    const strokeWidth = Math.max(1, Math.min(8, 1 + normalizedFreq * 7));

    // Determine if edge should be animated (< 5% of max frequency)
    const isLowFrequency = normalizedFreq < 0.05;

    const [edgePath, labelX, labelY] = getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    return (
        <>
            <BaseEdge
                id={id}
                path={edgePath}
                style={{
                    strokeWidth,
                    stroke: selected ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))',
                    strokeDasharray: isLowFrequency ? '5,5' : undefined,
                    animation: isLowFrequency ? 'dashmove 0.5s linear infinite' : undefined,
                }}
                markerEnd="url(#arrow)"
            />

            <EdgeLabelRenderer>
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div
                                className="absolute pointer-events-auto cursor-pointer px-2 py-1 rounded bg-background border text-xs font-medium shadow-sm hover:bg-muted transition-colors"
                                style={{
                                    transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
                                }}
                            >
                                {frequency}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="text-xs">
                            <div className="space-y-1">
                                <p><strong>Frequency:</strong> {frequency.toLocaleString()}</p>
                                <p><strong>Avg Duration:</strong> {formatDuration(avgDuration)}</p>
                                <p><strong>Cases:</strong> {caseCount.toLocaleString()}</p>
                            </div>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </EdgeLabelRenderer>
        </>
    );
}

export const ProcessEdge = memo(ProcessEdgeComponent);
