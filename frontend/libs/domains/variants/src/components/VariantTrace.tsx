import React from 'react';
import { Space, Tag, Typography, Tooltip } from 'antd';
import { RightOutlined, PlayCircleOutlined, StopOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface VariantTraceProps {
  activities: string[];
  maxVisible?: number;
  showStartEnd?: boolean;
  highlightActivities?: string[];
  compact?: boolean;
}

export const VariantTrace: React.FC<VariantTraceProps> = ({
  activities,
  maxVisible = 10,
  showStartEnd = true,
  highlightActivities = [],
  compact = false,
}) => {
  const displayActivities =
    activities.length > maxVisible
      ? activities.slice(0, maxVisible)
      : activities;

  const hasMore = activities.length > maxVisible;

  const getActivityColor = (activity: string, index: number): string => {
    if (highlightActivities.includes(activity)) {
      return '#ff4d4f'; // Highlight color
    }
    // Color gradient based on position
    const hue = (index * 30) % 360;
    return `hsl(${hue}, 70%, 45%)`;
  };

  if (compact) {
    return (
      <Tooltip
        title={activities.join(' → ')}
        placement="top"
        overlayStyle={{ maxWidth: 400 }}
      >
        <Text type="secondary" style={{ fontSize: 12 }}>
          {activities.slice(0, 3).join(' → ')}
          {activities.length > 3 && ` ... (+${activities.length - 3})`}
        </Text>
      </Tooltip>
    );
  }

  return (
    <Space wrap size={[4, 8]} style={{ lineHeight: 1.8 }}>
      {showStartEnd && (
        <Tag
          icon={<PlayCircleOutlined />}
          color="green"
          style={{ margin: 0, fontSize: 11 }}
        >
          Start
        </Tag>
      )}

      {displayActivities.map((activity, index) => (
        <React.Fragment key={`${activity}-${index}`}>
          {index > 0 && (
            <RightOutlined style={{ color: '#bfbfbf', fontSize: 10 }} />
          )}
          <Tooltip title={`Step ${index + 1}: ${activity}`}>
            <Tag
              color={getActivityColor(activity, index)}
              style={{
                margin: 0,
                maxWidth: 150,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {activity}
            </Tag>
          </Tooltip>
        </React.Fragment>
      ))}

      {hasMore && (
        <>
          <RightOutlined style={{ color: '#bfbfbf', fontSize: 10 }} />
          <Tooltip title={`${activities.length - maxVisible} more activities`}>
            <Tag color="default" style={{ margin: 0 }}>
              +{activities.length - maxVisible} more
            </Tag>
          </Tooltip>
        </>
      )}

      {showStartEnd && (
        <>
          <RightOutlined style={{ color: '#bfbfbf', fontSize: 10 }} />
          <Tag
            icon={<StopOutlined />}
            color="red"
            style={{ margin: 0, fontSize: 11 }}
          >
            End
          </Tag>
        </>
      )}
    </Space>
  );
};
