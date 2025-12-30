/**
 * EnhancedActivityNode - Rich Process Activity Node Component
 *
 * Features:
 * - Frequency-based sizing
 * - Performance coloring
 * - Start/End markers
 * - Rework/loop indicators
 * - Duration display
 * - Hover tooltips
 */

import React, { memo, useMemo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { Tooltip, Badge } from 'antd';
import {
  PlayCircleFilled,
  StopFilled,
  ReloadOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { COLORS, formatDuration, formatNumber, hexToRgba } from '../utils/colorScales';

// =============================================================================
// TYPES
// =============================================================================

export interface EnhancedActivityNodeData {
  // Core data
  label: string;
  frequency: number;
  frequencyPercent?: number;

  // Duration metrics
  avgDuration?: number;
  minDuration?: number;
  maxDuration?: number;

  // Node type flags
  isStart?: boolean;
  isEnd?: boolean;
  hasRework?: boolean;  // Activity appears multiple times in some cases

  // Visual state
  isSelected?: boolean;
  isHighlighted?: boolean;
  isOnCriticalPath?: boolean;

  // Performance mode
  showPerformance?: boolean;
  performanceColor?: string;

  // Scale factor from parent
  scale?: number;
}

// =============================================================================
// STYLES
// =============================================================================

const NODE_MIN_WIDTH = 140;
const NODE_MAX_WIDTH = 200;

// =============================================================================
// COMPONENT
// =============================================================================

function EnhancedActivityNodeComponent({ data, selected }: NodeProps<EnhancedActivityNodeData>) {
  const {
    label,
    frequency,
    frequencyPercent,
    avgDuration,
    isStart,
    isEnd,
    hasRework,
    isSelected,
    isHighlighted,
    isOnCriticalPath,
    showPerformance,
    performanceColor,
    scale = 1,
  } = data;

  // Calculate dynamic styles
  const styles = useMemo(() => {
    // Base sizing
    const width = Math.min(NODE_MAX_WIDTH, Math.max(NODE_MIN_WIDTH, NODE_MIN_WIDTH * scale));

    // Background color logic
    let backgroundColor = COLORS.node.default;
    let borderColor = COLORS.border.default;
    let borderWidth = 1;

    if (showPerformance && performanceColor) {
      backgroundColor = hexToRgba(performanceColor, 0.12);
      borderColor = performanceColor;
    } else if (isStart) {
      backgroundColor = COLORS.node.start;
      borderColor = COLORS.border.start;
    } else if (isEnd) {
      backgroundColor = COLORS.node.end;
      borderColor = COLORS.border.end;
    } else if (isSelected || selected) {
      backgroundColor = COLORS.node.selected;
      borderColor = COLORS.border.selected;
      borderWidth = 2;
    } else if (isHighlighted) {
      backgroundColor = COLORS.node.highlighted;
      borderColor = '#3B82F6';
    }

    // Critical path styling
    if (isOnCriticalPath) {
      borderWidth = 2;
    }

    return {
      width,
      backgroundColor,
      borderColor,
      borderWidth,
    };
  }, [
    scale,
    showPerformance,
    performanceColor,
    isStart,
    isEnd,
    isSelected,
    selected,
    isHighlighted,
    isOnCriticalPath,
  ]);

  // Tooltip content
  const tooltipContent = useMemo(() => (
    <div style={{ fontSize: 12 }}>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{label}</div>
      <div>Frequency: {formatNumber(frequency)} cases</div>
      {frequencyPercent !== undefined && (
        <div>Coverage: {frequencyPercent.toFixed(1)}%</div>
      )}
      {avgDuration !== undefined && (
        <div>Avg Duration: {formatDuration(avgDuration)}</div>
      )}
      {hasRework && (
        <div style={{ color: COLORS.performance.moderate, marginTop: 4 }}>
          Contains rework loops
        </div>
      )}
    </div>
  ), [label, frequency, frequencyPercent, avgDuration, hasRework]);

  return (
    <Tooltip title={tooltipContent} placement="top" mouseEnterDelay={0.5}>
      <div
        style={{
          width: styles.width,
          backgroundColor: styles.backgroundColor,
          border: `${styles.borderWidth}px solid ${styles.borderColor}`,
          borderRadius: tokens.radius.lg,
          padding: '10px 12px',
          boxShadow: (isSelected || selected) ? tokens.shadow.md : tokens.shadow.sm,
          transition: 'all 150ms ease',
          cursor: 'pointer',
          position: 'relative',
        }}
      >
        {/* Left Handle */}
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: styles.borderColor,
            width: 8,
            height: 8,
            border: '2px solid white',
          }}
        />

        {/* Node Content */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {/* Header Row: Icons + Label */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            {/* Start/End Icon */}
            {isStart && (
              <PlayCircleFilled style={{ color: COLORS.border.start, fontSize: 14 }} />
            )}
            {isEnd && (
              <StopFilled style={{ color: COLORS.border.end, fontSize: 14 }} />
            )}

            {/* Label */}
            <span
              style={{
                fontWeight: 600,
                fontSize: 13,
                color: tokens.colors.neutral[800],
                flex: 1,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {label}
            </span>

            {/* Rework Indicator */}
            {hasRework && (
              <Tooltip title="Contains rework">
                <ReloadOutlined
                  style={{
                    color: COLORS.performance.moderate,
                    fontSize: 12,
                  }}
                />
              </Tooltip>
            )}
          </div>

          {/* Metrics Row */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: 8,
            }}
          >
            {/* Frequency */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                fontSize: 11,
                color: tokens.colors.neutral[600],
              }}
            >
              <ThunderboltOutlined style={{ fontSize: 10 }} />
              <span>{formatNumber(frequency)}</span>
              {frequencyPercent !== undefined && (
                <span style={{ color: tokens.colors.neutral[400] }}>
                  ({frequencyPercent.toFixed(0)}%)
                </span>
              )}
            </div>

            {/* Duration */}
            {avgDuration !== undefined && avgDuration > 0 && (
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 3,
                  fontSize: 11,
                  color: showPerformance && performanceColor
                    ? performanceColor
                    : tokens.colors.neutral[500],
                  fontWeight: showPerformance ? 500 : 400,
                }}
              >
                <ClockCircleOutlined style={{ fontSize: 10 }} />
                <span>{formatDuration(avgDuration)}</span>
              </div>
            )}
          </div>

          {/* Frequency Bar */}
          {frequencyPercent !== undefined && (
            <div
              style={{
                height: 3,
                backgroundColor: tokens.colors.neutral[200],
                borderRadius: 2,
                overflow: 'hidden',
                marginTop: 2,
              }}
            >
              <div
                style={{
                  height: '100%',
                  width: `${Math.min(100, frequencyPercent)}%`,
                  backgroundColor: showPerformance && performanceColor
                    ? performanceColor
                    : isHighlighted
                    ? '#3B82F6'
                    : tokens.colors.primary[500],
                  borderRadius: 2,
                  transition: 'width 300ms ease',
                }}
              />
            </div>
          )}
        </div>

        {/* Right Handle */}
        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: styles.borderColor,
            width: 8,
            height: 8,
            border: '2px solid white',
          }}
        />

        {/* Critical Path Badge */}
        {isOnCriticalPath && (
          <div
            style={{
              position: 'absolute',
              top: -8,
              right: -8,
            }}
          >
            <Badge
              count="!"
              style={{
                backgroundColor: COLORS.performance.poor,
                fontSize: 10,
              }}
            />
          </div>
        )}
      </div>
    </Tooltip>
  );
}

// Memoize to prevent unnecessary re-renders
export const EnhancedActivityNode = memo(EnhancedActivityNodeComponent);

export default EnhancedActivityNode;
