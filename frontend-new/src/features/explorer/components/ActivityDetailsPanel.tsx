/**
 * ActivityDetailsPanel - Activity Details Component
 */

import { Typography, Descriptions, Tag, Button, Space, Divider } from 'antd';
import { FilterOutlined, CloseOutlined } from '@ant-design/icons';
import { tokens } from '@/src/shared/design-system';
import { createLogger } from '../../../shared/lib/logger';
import { formatDuration } from '../utils/colorScales';
import type { ActivityData } from '../types';

const log = createLogger('ActivityDetailsPanel');
const { Title, Text } = Typography;

export interface ActivityDetailsPanelProps {
  activity: ActivityData | null;
  onClose?: () => void;
  onFilterWith?: (activityId: string) => void;
  onFilterWithout?: (activityId: string) => void;
}

export function ActivityDetailsPanel({
  activity,
  onClose,
  onFilterWith,
  onFilterWithout,
}: ActivityDetailsPanelProps) {
  log.debug('Rendering ActivityDetailsPanel', { activity: activity?.name });

  if (!activity) {
    return (
      <div
        style={{
          padding: tokens.spacing[6],
          textAlign: 'center',
          color: tokens.colors.neutral[400],
        }}
      >
        <Text type="secondary">Click a node to see activity details</Text>
      </div>
    );
  }

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: tokens.spacing[4] }}>
        <Title level={5} style={{ margin: 0 }}>
          {activity.name}
        </Title>
        {onClose && (
          <Button
            type="text"
            size="small"
            icon={<CloseOutlined />}
            onClick={onClose}
          />
        )}
      </div>

      <Descriptions column={1} size="small" style={{ marginBottom: tokens.spacing[4] }}>
        <Descriptions.Item label="Total occurrences">
          <Tag color="blue">{activity.totalOccurrences.toLocaleString()}</Tag>
        </Descriptions.Item>
        <Descriptions.Item label="Cases with activity">
          <Text strong>{activity.casePercentage.toFixed(1)}%</Text>
        </Descriptions.Item>
        <Descriptions.Item label="Average duration">
          <Text>{formatDuration(activity.avgDurationSeconds)}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="Duration range">
          <Text type="secondary">
            {formatDuration(activity.minDurationSeconds)} – {formatDuration(activity.maxDurationSeconds)}
          </Text>
        </Descriptions.Item>
      </Descriptions>

      {activity.resources.length > 0 && (
        <>
          <Text type="secondary" style={{ fontSize: tokens.fontSize.sm, display: 'block', marginBottom: tokens.spacing[2] }}>
            Resources
          </Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginBottom: tokens.spacing[4] }}>
            {activity.resources.slice(0, 5).map((resource) => (
              <Tag key={resource}>{resource}</Tag>
            ))}
            {activity.resources.length > 5 && (
              <Tag>+{activity.resources.length - 5} more</Tag>
            )}
          </div>
        </>
      )}

      <Divider style={{ margin: `${tokens.spacing[3]} 0` }} />

      <Text type="secondary" style={{ fontSize: tokens.fontSize.sm, display: 'block', marginBottom: tokens.spacing[2] }}>
        Filter Actions
      </Text>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Button
          block
          icon={<FilterOutlined />}
          onClick={() => {
            onFilterWith?.(activity.id);
            log.info('Filter with activity', { activityId: activity.id });
          }}
        >
          Only cases with this activity
        </Button>
        <Button
          block
          icon={<FilterOutlined />}
          onClick={() => {
            onFilterWithout?.(activity.id);
            log.info('Filter without activity', { activityId: activity.id });
          }}
        >
          Only cases without this activity
        </Button>
      </Space>
    </div>
  );
}

export default ActivityDetailsPanel;
