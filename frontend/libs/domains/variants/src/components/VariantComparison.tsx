import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Space,
  Typography,
  Divider,
  Alert,
  Spin,
  Empty,
} from 'antd';
import {
  SwapOutlined,
  ClockCircleOutlined,
  BarChartOutlined,
  BranchesOutlined,
} from '@ant-design/icons';
import type { ProcessVariant } from 'process-mining-sdk';
import { useVariantComparison } from '../hooks';
import { VariantTrace } from './VariantTrace';
import { HappyPathBadge } from './HappyPathBadge';

const { Text, Title } = Typography;

interface VariantComparisonProps {
  logId: string;
  variantKeys: string[];
  onClose?: () => void;
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined || seconds === null) return '-';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

export const VariantComparison: React.FC<VariantComparisonProps> = ({
  logId,
  variantKeys,
  onClose,
}) => {
  const { data, isLoading, error } = useVariantComparison(logId, variantKeys);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load comparison"
        description="Could not compare the selected variants."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Spin tip="Loading comparison..." />
      </Card>
    );
  }

  if (!data || data.variants.length === 0) {
    return (
      <Card>
        <Empty description="Select variants to compare" />
      </Card>
    );
  }

  const { variants, comparison } = data;

  const columns = [
    {
      title: 'Variant',
      dataIndex: 'key',
      key: 'key',
      render: (key: string, record: ProcessVariant) => (
        <Space>
          <Text strong>{key}</Text>
          <HappyPathBadge isHappyPath={record.isHappyPath} size="small" />
        </Space>
      ),
    },
    {
      title: 'Cases',
      dataIndex: 'caseCount',
      key: 'caseCount',
      render: (count: number) => count.toLocaleString(),
    },
    {
      title: 'Steps',
      dataIndex: 'length',
      key: 'length',
    },
    {
      title: 'Avg Duration',
      dataIndex: 'avgDurationSeconds',
      key: 'avgDurationSeconds',
      render: (duration?: number) => formatDuration(duration),
    },
    {
      title: 'Frequency',
      dataIndex: 'frequencyPercent',
      key: 'frequencyPercent',
      render: (freq?: number) => (freq ? `${freq.toFixed(1)}%` : '-'),
    },
  ];

  return (
    <Card
      title={
        <Space>
          <SwapOutlined />
          Variant Comparison ({variants.length} variants)
        </Space>
      }
      extra={onClose && <a onClick={onClose}>Close</a>}
    >
      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Statistic
            title="Total Cases"
            value={comparison.totalCases}
            prefix={<BarChartOutlined />}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Avg Duration"
            value={formatDuration(comparison.avgDuration)}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Longest Variant"
            value={comparison.longestVariant?.length || 0}
            suffix="steps"
            prefix={<BranchesOutlined />}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Shortest Variant"
            value={comparison.shortestVariant?.length || 0}
            suffix="steps"
            prefix={<BranchesOutlined />}
          />
        </Col>
      </Row>

      {/* Comparison Table */}
      <Table
        columns={columns}
        dataSource={variants}
        rowKey="key"
        size="small"
        pagination={false}
        style={{ marginBottom: 24 }}
      />

      <Divider />

      {/* Common Activities */}
      <div style={{ marginBottom: 24 }}>
        <Title level={5}>Common Activities ({comparison.commonActivities.length})</Title>
        {comparison.commonActivities.length > 0 ? (
          <Space wrap>
            {comparison.commonActivities.map((activity: string) => (
              <Tag key={activity} color="blue">
                {activity}
              </Tag>
            ))}
          </Space>
        ) : (
          <Text type="secondary">No common activities found</Text>
        )}
      </div>

      {/* Unique Activities per Variant */}
      <Title level={5}>Unique Activities</Title>
      {comparison.uniqueActivitiesPerVariant.map((item: { variantKey: string; uniqueActivities: string[] }) => (
        <div key={item.variantKey} style={{ marginBottom: 16 }}>
          <Text strong style={{ marginRight: 8 }}>
            {item.variantKey}:
          </Text>
          {item.uniqueActivities.length > 0 ? (
            <Space wrap>
              {item.uniqueActivities.map((activity: string) => (
                <Tag key={activity} color="orange">
                  {activity}
                </Tag>
              ))}
            </Space>
          ) : (
            <Text type="secondary">All activities are common</Text>
          )}
        </div>
      ))}

      <Divider />

      {/* Full Traces */}
      <Title level={5}>Full Traces</Title>
      {variants.map((variant: ProcessVariant) => (
        <div key={variant.key} style={{ marginBottom: 16 }}>
          <Text strong style={{ display: 'block', marginBottom: 8 }}>
            {variant.key}
          </Text>
          <VariantTrace
            activities={variant.activities}
            highlightActivities={
              comparison.uniqueActivitiesPerVariant.find(
                (u: { variantKey: string; uniqueActivities: string[] }) => u.variantKey === variant.key
              )?.uniqueActivities || []
            }
          />
        </div>
      ))}
    </Card>
  );
};
