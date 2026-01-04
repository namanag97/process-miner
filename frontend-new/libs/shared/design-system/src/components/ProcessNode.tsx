import { memo } from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { tokens } from '../theme';

export interface ProcessNodeData {
  label: string;
  count?: number;
  performance?: number;
  isStart?: boolean;
  isEnd?: boolean;
  isActive?: boolean;
}

/**
 * ProcessNode - A bespoke, architectural node for the DFG
 * Features:
 * - Glassmorphic surface
 * - Data-driven glow (based on performance/count)
 * - Precision border (2px)
 * - Semantic coloring for Start/End points
 */
export const ProcessNode = memo(({ data, selected }: NodeProps<ProcessNodeData>) => {
  const { label, count, performance: _performance, isStart, isEnd, isActive: _isActive } = data;

  // Semantic highlights
  const borderColor = isStart
    ? tokens.colors.success[500]
    : isEnd
      ? tokens.colors.error[500]
      : selected
        ? tokens.colors.primary[500]
        : tokens.colors.neutral[300];

  const glowOpacity = selected ? 0.3 : 0.1;
  const shadowSpread = selected ? '12px' : '4px';

  return (
    <div
      className="surface-noise"
      style={{
        padding: `${tokens.spacing[3]}px ${tokens.spacing[6]}px`,
        borderRadius: tokens.radius.xs,
        background: tokens.colors.neutral[0],
        border: `2px solid ${borderColor}`,
        boxShadow: selected
          ? `0 0 ${shadowSpread} ${borderColor}${Math.floor(glowOpacity * 255).toString(16)}`
          : tokens.shadow.sm,
        minWidth: 140,
        position: 'relative',
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
      }}
    >
      {/* Input Handle */}
      {!isStart && (
        <Handle
          type="target"
          position={Position.Left}
          style={{
            background: borderColor,
            width: 8,
            height: 8,
            border: '2px solid white'
          }}
        />
      )}

      {/* Node Content */}
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: tokens.fontSize.sm,
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: tokens.colors.neutral[500],
            marginBottom: 2,
          }}
        >
          {isStart ? 'START' : isEnd ? 'END' : 'Activity'}
        </div>
        <div
          style={{
            fontSize: tokens.fontSize.base,
            fontWeight: 600,
            color: tokens.colors.neutral[900],
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}
        >
          {label}
        </div>

        {count !== undefined && (
          <div
            style={{
              marginTop: 4,
              fontSize: tokens.fontSize.xs,
              color: tokens.colors.neutral[400],
              fontFamily: 'monospace'
            }}
          >
            n={count.toLocaleString()}
          </div>
        )}
      </div>

      {/* Output Handle */}
      {!isEnd && (
        <Handle
          type="source"
          position={Position.Right}
          style={{
            background: borderColor,
            width: 8,
            height: 8,
            border: '2px solid white'
          }}
        />
      )}
    </div>
  );
});

ProcessNode.displayName = 'ProcessNode';

export default ProcessNode;
