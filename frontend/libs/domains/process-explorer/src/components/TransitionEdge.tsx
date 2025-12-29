import React, { memo } from 'react';
import { EdgeProps, getBezierPath, EdgeLabelRenderer } from '@xyflow/react';
import { formatCompactNumber, formatDurationFromSeconds } from '@lumina/design-system';

interface TransitionEdgeData {
  frequency: number;
  maxFrequency: number;
  performance?: number;
  colorMode?: 'frequency' | 'performance';
}

// Color scale for edge frequency
function getEdgeColor(ratio: number, colorMode: string): string {
  if (colorMode === 'performance') {
    if (ratio < 0.33) return '#52c41a';
    if (ratio < 0.66) return '#faad14';
    return '#ff4d4f';
  }
  // Frequency mode - blue gradient
  if (ratio < 0.2) return '#bdd7ff';
  if (ratio < 0.4) return '#85b7ff';
  if (ratio < 0.6) return '#4d97ff';
  if (ratio < 0.8) return '#1a75ff';
  return '#0052cc';
}

// Get stroke width based on frequency ratio
function getStrokeWidth(ratio: number): number {
  return 1 + ratio * 4; // 1px to 5px
}

export const TransitionEdge: React.FC<EdgeProps<TransitionEdgeData>> = memo(
  ({
    id,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    data,
    markerEnd,
    selected,
  }) => {
    const { frequency = 0, maxFrequency = 1, performance, colorMode = 'frequency' } = data || {};
    const ratio = frequency / maxFrequency;

    const [edgePath, labelX, labelY] = getBezierPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition,
    });

    const strokeColor = getEdgeColor(ratio, colorMode);
    const strokeWidth = getStrokeWidth(ratio);

    return (
      <>
        {/* Invisible wider path for easier selection */}
        <path
          id={`${id}-hitbox`}
          className="react-flow__edge-interaction"
          d={edgePath}
          fill="none"
          strokeWidth={20}
          stroke="transparent"
        />

        {/* Actual edge path */}
        <path
          id={id}
          className="react-flow__edge-path"
          d={edgePath}
          fill="none"
          stroke={selected ? '#0052cc' : strokeColor}
          strokeWidth={selected ? strokeWidth + 1 : strokeWidth}
          markerEnd={markerEnd}
          style={{
            opacity: ratio < 0.1 ? 0.3 : 0.7 + ratio * 0.3,
            transition: 'stroke 0.2s, stroke-width 0.2s',
          }}
        />

        {/* Edge label showing frequency */}
        {ratio > 0.15 && (
          <EdgeLabelRenderer>
            <div
              style={{
                position: 'absolute',
                transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
                pointerEvents: 'all',
                fontSize: 10,
                fontWeight: 500,
                padding: '2px 4px',
                borderRadius: 3,
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                border: '1px solid #d9d9d9',
                color: '#172b4d',
              }}
              className="nodrag nopan"
            >
              {formatCompactNumber(frequency)}
              {performance !== undefined && colorMode === 'performance' && (
                <span style={{ marginLeft: 4, color: '#5e6c84' }}>
                  ({formatDurationFromSeconds(performance)})
                </span>
              )}
            </div>
          </EdgeLabelRenderer>
        )}
      </>
    );
  }
);

TransitionEdge.displayName = 'TransitionEdge';
