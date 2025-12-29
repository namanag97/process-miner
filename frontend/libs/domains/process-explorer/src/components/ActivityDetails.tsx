import React from 'react';
import {
  Card,
  Typography,
  Statistic,
  Row,
  Col,
  Tag,
  Divider,
  Space,
  Progress,
  Button,
  Empty,
} from 'antd';
import {
  CloseOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  UserOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { formatCompactNumber, formatDurationFromSeconds } from '@lumina/design-system';
import type { DFGNode, DFGEdge } from 'process-mining-sdk';

const { Title, Text } = Typography;

interface ActivityDetailsProps {
  activity: DFGNode | null;
  incomingEdges?: DFGEdge[];
  outgoingEdges?: DFGEdge[];
  totalCases?: number;
  onClose?: () => void;
  onNavigateToActivity?: (activityId: string) => void;
}

export const ActivityDetails: React.FC<ActivityDetailsProps> = ({
  activity,
  incomingEdges = [],
  outgoingEdges = [],
  totalCases = 0,
  onClose,
  onNavigateToActivity,
}) => {
  if (!activity) {
    return (
      <Card size="small" style={{ width: 320 }}>
        <Empty
          description="Select an activity to view details"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const frequencyPercent = totalCases > 0 ? (activity.frequency / totalCases) * 100 : 0;

  // Sort edges by frequency
  const sortedIncoming = [...incomingEdges].sort((a, b) => b.frequency - a.frequency);
  const sortedOutgoing = [...outgoingEdges].sort((a, b) => b.frequency - a.frequency);

  const renderEdgeList = (edges: DFGEdge[], direction: 'incoming' | 'outgoing') => {
    if (edges.length === 0) {
      return (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {direction === 'incoming' ? 'No incoming transitions' : 'No outgoing transitions'}
        </Text>
      );
    }

    const maxFreq = Math.max(...edges.map((e) => e.frequency));

    return (
      <div style={{ maxHeight: 150, overflowY: 'auto' }}>
        {edges.slice(0, 10).map((edge) => {
          const activityId = direction === 'incoming' ? edge.source : edge.target;
          const ratio = edge.frequency / maxFreq;

          return (
            <div
              key={`${edge.source}-${edge.target}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '4px 0',
                borderBottom: '1px solid #f0f0f0',
                cursor: onNavigateToActivity ? 'pointer' : 'default',
              }}
              onClick={() => onNavigateToActivity?.(activityId)}
            >
              <Space size={4}>
                {direction === 'incoming' && (
                  <ArrowRightOutlined style={{ color: '#52c41a', fontSize: 10 }} />
                )}
                <Text
                  ellipsis
                  style={{ maxWidth: 150, fontSize: 12 }}
                  title={activityId}
                >
                  {activityId}
                </Text>
                {direction === 'outgoing' && (
                  <ArrowRightOutlined style={{ color: '#1890ff', fontSize: 10 }} />
                )}
              </Space>
              <Space size={4}>
                <Text style={{ fontSize: 11 }}>{formatCompactNumber(edge.frequency)}</Text>
                <div
                  style={{
                    width: 40,
                    height: 4,
                    backgroundColor: '#f0f0f0',
                    borderRadius: 2,
                  }}
                >
                  <div
                    style={{
                      width: `${ratio * 100}%`,
                      height: '100%',
                      backgroundColor: direction === 'incoming' ? '#52c41a' : '#1890ff',
                      borderRadius: 2,
                    }}
                  />
                </div>
              </Space>
            </div>
          );
        })}
        {edges.length > 10 && (
          <Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 4 }}>
            +{edges.length - 10} more transitions
          </Text>
        )}
      </div>
    );
  };

  return (
    <Card
      size="small"
      style={{ width: 320 }}
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <BarChartOutlined />
          <Text strong ellipsis style={{ maxWidth: 200 }} title={activity.label}>
            {activity.label}
          </Text>
        </div>
      }
      extra={
        onClose && (
          <Button type="text" size="small" icon={<CloseOutlined />} onClick={onClose} />
        )
      }
    >
      {/* Main Stats */}
      <Row gutter={[8, 8]}>
        <Col span={12}>
          <Statistic
            title="Frequency"
            value={formatCompactNumber(activity.frequency)}
            valueStyle={{ fontSize: 20 }}
          />
        </Col>
        <Col span={12}>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>Coverage</Text>
            <Progress
              percent={Number(frequencyPercent.toFixed(1))}
              size="small"
              strokeColor="#0052cc"
            />
          </div>
        </Col>
      </Row>

      <Divider style={{ margin: '12px 0' }} />

      {/* Incoming Transitions */}
      <div style={{ marginBottom: 12 }}>
        <Text strong style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
          <span style={{ color: '#52c41a' }}>Incoming</span> ({sortedIncoming.length})
        </Text>
        {renderEdgeList(sortedIncoming, 'incoming')}
      </div>

      {/* Outgoing Transitions */}
      <div>
        <Text strong style={{ fontSize: 12, display: 'block', marginBottom: 8 }}>
          <span style={{ color: '#1890ff' }}>Outgoing</span> ({sortedOutgoing.length})
        </Text>
        {renderEdgeList(sortedOutgoing, 'outgoing')}
      </div>
    </Card>
  );
};
