import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Tooltip } from 'antd';
import { PlayCircleOutlined, StopOutlined } from '@ant-design/icons';
import { formatCompactNumber } from '@lumina/design-system';

interface ActivityNodeData {
  label: string;
  frequency: number;
  maxFrequency: number;
  isStart?: boolean;
  isEnd?: boolean;
  colorMode?: 'frequency' | 'performance';
  isSelected?: boolean;
}

interface ActivityNodeProps {
  data: ActivityNodeData;
  selected?: boolean;
}

// Color scale for frequency visualization (blue gradient)
function getFrequencyColor(ratio: number): string {
  // From light blue to dark blue
  const colors = [
    '#e6f0ff', // 0-20%
    '#bdd7ff', // 20-40%
    '#85b7ff', // 40-60%
    '#4d97ff', // 60-80%
    '#0052cc', // 80-100%
  ];

  const index = Math.min(Math.floor(ratio * 5), 4);
  return colors[index];
}

// Color scale for performance visualization (green-yellow-red)
function getPerformanceColor(ratio: number): string {
  // From green (fast) to red (slow)
  if (ratio < 0.33) return '#52c41a'; // Green - fast
  if (ratio < 0.66) return '#faad14'; // Yellow - medium
  return '#ff4d4f'; // Red - slow
}

export const ActivityNode: React.FC<ActivityNodeProps> = memo(({ data, selected }) => {
  const { label, frequency, maxFrequency, isStart, isEnd, colorMode = 'frequency', isSelected } = data;
  const ratio = frequency / maxFrequency;

  const bgColor = colorMode === 'frequency'
    ? getFrequencyColor(ratio)
    : getPerformanceColor(ratio);

  const textColor = ratio > 0.6 && colorMode === 'frequency' ? '#fff' : '#172b4d';
  const borderColor = (selected || isSelected) ? '#0052cc' : '#d9d9d9';
  const boxShadow = (selected || isSelected) ? '0 0 0 2px rgba(0, 82, 204, 0.3)' : 'none';

  return (
    <Tooltip
      title={
        <div>
          <div><strong>{label}</strong></div>
          <div>Frequency: {formatCompactNumber(frequency)}</div>
          {isStart && <div>Start Activity</div>}
          {isEnd && <div>End Activity</div>}
        </div>
      }
    >
      <div
        style={{
          padding: '8px 16px',
          borderRadius: 4,
          backgroundColor: bgColor,
          border: `2px solid ${borderColor}`,
          boxShadow,
          minWidth: 120,
          maxWidth: 180,
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
        }}
      >
        <Handle
          type="target"
          position={Position.Top}
          style={{
            background: '#0052cc',
            width: 8,
            height: 8,
            border: '2px solid #fff',
          }}
        />

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4 }}>
          {isStart && <PlayCircleOutlined style={{ color: '#52c41a', fontSize: 12 }} />}
          <span
            style={{
              fontSize: 12,
              fontWeight: 500,
              color: textColor,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {label}
          </span>
          {isEnd && <StopOutlined style={{ color: '#ff4d4f', fontSize: 12 }} />}
        </div>

        <div
          style={{
            fontSize: 10,
            color: ratio > 0.6 && colorMode === 'frequency' ? 'rgba(255,255,255,0.8)' : '#5e6c84',
            marginTop: 2,
          }}
        >
          {formatCompactNumber(frequency)}
        </div>

        <Handle
          type="source"
          position={Position.Bottom}
          style={{
            background: '#0052cc',
            width: 8,
            height: 8,
            border: '2px solid #fff',
          }}
        />
      </div>
    </Tooltip>
  );
});

ActivityNode.displayName = 'ActivityNode';
