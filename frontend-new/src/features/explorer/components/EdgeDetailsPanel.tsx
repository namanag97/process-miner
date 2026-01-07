/**
 * EdgeDetailsPanel - Transition Details Component
 *
 * Shows details about a selected edge/transition in the process graph:
 * - Source and target activities
 * - Frequency and percentage
 * - Duration statistics
 * - Filter actions
 */

import { Typography, Descriptions, Tag, Button, Space, Divider } from 'antd';
import {
  FilterOutlined,
  CloseOutlined,
  SwapRightOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../shared/lib/logger';
import { formatDuration, formatNumber } from '../utils/colorScales';
import type { EdgeDetail } from '../types';

const log = createLogger('EdgeDetailsPanel');
const { Title, Text } = Typography;

// =============================================================================
// TYPES
// =============================================================================

export interface EdgeDetailsPanelProps {
  edge: EdgeDetail | null;
  onClose?: () => void;
  onFilterToTransition?: (source: string, target: string) => void;
  onFilterWithTransition?: (source: string, target: string) => void;
  totalCases?: number;
}

// =============================================================================
// MINI TRANSITION VISUAL
// =============================================================================

interface TransitionVisualProps {
  source: string;
  target: string;
  probability?: number;
}

function TransitionVisual({ source, target, probability }: TransitionVisualProps) {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 12,
        padding: '16px 12px',
        backgroundColor: tokens.colors.neutral[50],
        borderRadius: tokens.radius.lg,
        marginBottom: 16,
      }}
    >
      {/* Source Node */}
      <div
        style={{
          padding: '8px 12px',
          backgroundColor: tokens.colors.neutral[0],
          border: `1px solid ${tokens.colors.neutral[300]}`,
          borderRadius: tokens.radius.md,
          fontSize: 12,
          fontWeight: 500,
          maxWidth: 100,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
        title={source}
      >
        {source}
      </div>

      {/* Arrow with probability */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
        <SwapRightOutlined
          style={{
            fontSize: 20,
            color: tokens.colors.primary[500],
          }}
        />
        {probability !== undefined && (
          <Text style={{ fontSize: 10, color: tokens.colors.neutral[500] }}>
            {(probability * 100).toFixed(0)}%
          </Text>
        )}
      </div>

      {/* Target Node */}
      <div
        style={{
          padding: '8px 12px',
          backgroundColor: tokens.colors.neutral[0],
          border: `1px solid ${tokens.colors.neutral[300]}`,
          borderRadius: tokens.radius.md,
          fontSize: 12,
          fontWeight: 500,
          maxWidth: 100,
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
        title={target}
      >
        {target}
      </div>
    </div>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function EdgeDetailsPanel({
  edge,
  onClose,
  onFilterToTransition,
  onFilterWithTransition,
  totalCases,
}: EdgeDetailsPanelProps) {
  log.debug('Rendering EdgeDetailsPanel', { edge: edge?.id });

  if (!edge) {
    return (
      <div
        style={{
          padding: tokens.spacing[6],
          textAlign: 'center',
          color: tokens.colors.neutral[400],
        }}
      >
        <SwapRightOutlined style={{ fontSize: 32, marginBottom: 8 }} />
        <Text type="secondary" style={{ display: 'block' }}>
          Click a transition to see details
        </Text>
      </div>
    );
  }

  const {
    source,
    target,
    frequency,
    frequencyPercent,
    avgDurationSeconds,
  } = edge;

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: tokens.spacing[4],
        }}
      >
        <Title level={5} style={{ margin: 0 }}>
          Transition
        </Title>
        {onClose && (
          <Button type="text" size="small" icon={<CloseOutlined />} onClick={onClose} />
        )}
      </div>

      {/* Visual representation */}
      <TransitionVisual source={source} target={target} />

      {/* Statistics */}
      <Descriptions column={1} size="small" style={{ marginBottom: tokens.spacing[4] }}>
        <Descriptions.Item
          label={
            <Space>
              <ThunderboltOutlined />
              Frequency
            </Space>
          }
        >
          <Space>
            <Tag color="blue">{formatNumber(frequency)}</Tag>
            <Text type="secondary" style={{ fontSize: 12 }}>
              ({frequencyPercent.toFixed(1)}% of all transitions)
            </Text>
          </Space>
        </Descriptions.Item>

        {avgDurationSeconds !== undefined && (
          <Descriptions.Item
            label={
              <Space>
                <ClockCircleOutlined />
                Avg Duration
              </Space>
            }
          >
            <Tag>{formatDuration(avgDurationSeconds)}</Tag>
          </Descriptions.Item>
        )}
      </Descriptions>

      <Divider style={{ margin: `${tokens.spacing[3]} 0` }} />

      {/* Filter Actions */}
      <Text
        type="secondary"
        style={{
          fontSize: 11,
          display: 'block',
          marginBottom: tokens.spacing[2],
        }}
      >
        Filter Actions
      </Text>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          block
          icon={<FilterOutlined />}
          onClick={() => onFilterWithTransition?.(source, target)}
        >
          Cases with this transition
        </Button>
        <Button
          block
          icon={<FilterOutlined />}
          onClick={() => onFilterToTransition?.(source, target)}
          type="default"
        >
          Only {source} → {target}
        </Button>
      </Space>

      {/* Context info */}
      {totalCases !== undefined && (
        <div
          style={{
            marginTop: tokens.spacing[4],
            padding: tokens.spacing[3],
            backgroundColor: tokens.colors.neutral[50],
            borderRadius: tokens.radius.md,
            fontSize: 11,
            color: tokens.colors.neutral[600],
          }}
        >
          This transition occurs in{' '}
          <Text strong>
            {totalCases > 0 ? ((frequency / totalCases) * 100).toFixed(1) : 0}%
          </Text>{' '}
          of all cases ({formatNumber(frequency)} of {formatNumber(totalCases)})
        </div>
      )}
    </div>
  );
}

export default EdgeDetailsPanel;
