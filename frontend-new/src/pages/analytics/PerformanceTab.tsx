import React from 'react';
import { Row, Col, Card, Table, Progress, Typography, Space, Tooltip } from 'antd';
import {
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { MetricCard, tokens, formatDuration, formatCompactNumber } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const { Text, Title } = Typography;
const log = createLogger('PerformanceTab');

// Mock data for performance metrics
const mockBottlenecks = [
  { activity: 'Approval Review', avgDuration: 172800, frequency: 1250, impact: 95 },
  { activity: 'Document Verification', avgDuration: 86400, frequency: 890, impact: 78 },
  { activity: 'Payment Processing', avgDuration: 43200, frequency: 2100, impact: 65 },
  { activity: 'Quality Check', avgDuration: 28800, frequency: 750, impact: 45 },
  { activity: 'Final Sign-off', avgDuration: 14400, frequency: 1100, impact: 32 },
];

const mockCycleTimeBreakdown = [
  { activity: 'Order Received', avgTime: 3600, percentage: 5 },
  { activity: 'Validation', avgTime: 7200, percentage: 10 },
  { activity: 'Processing', avgTime: 14400, percentage: 20 },
  { activity: 'Approval Review', avgTime: 172800, percentage: 45 },
  { activity: 'Completion', avgTime: 7200, percentage: 10 },
  { activity: 'Delivery', avgTime: 3600, percentage: 5 },
  { activity: 'Confirmation', avgTime: 3600, percentage: 5 },
];

const mockThroughputData = {
  casesPerDay: 85,
  casesPerWeek: 595,
  casesPerMonth: 2550,
  trend: 12.5,
};

export function PerformanceTab() {
  log.debug('Rendering PerformanceTab');

  const bottleneckColumns = [
    {
      title: 'Rank',
      key: 'rank',
      width: 60,
      render: (_: unknown, __: unknown, index: number) => (
        <Text strong style={{ color: index < 3 ? tokens.colors.error[500] : tokens.colors.neutral[600] }}>
          #{index + 1}
        </Text>
      ),
    },
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Avg Duration',
      dataIndex: 'avgDuration',
      key: 'avgDuration',
      render: (seconds: number) => formatDuration(seconds),
    },
    {
      title: 'Frequency',
      dataIndex: 'frequency',
      key: 'frequency',
      render: (val: number) => formatCompactNumber(val),
    },
    {
      title: 'Impact Score',
      dataIndex: 'impact',
      key: 'impact',
      render: (val: number) => (
        <Progress
          percent={val}
          size="small"
          strokeColor={val > 70 ? tokens.colors.error[500] : val > 40 ? tokens.colors.warning[500] : tokens.colors.success[500]}
          showInfo={false}
          style={{ width: 100 }}
        />
      ),
    },
  ];

  return (
    <div>
      {/* KPI Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Avg Cycle Time"
            value="4.2"
            suffix="days"
            trend={{ value: -8.5, isPositive: true, label: 'vs last month' }}
            status="success"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Throughput"
            value={mockThroughputData.casesPerDay}
            suffix="cases/day"
            trend={{ value: mockThroughputData.trend, isPositive: true, label: 'vs last week' }}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Bottleneck Activities"
            value={mockBottlenecks.length}
            status="warning"
          />
        </Col>
      </Row>

      <Row gutter={24}>
        {/* Bottleneck Analysis */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <WarningOutlined style={{ color: tokens.colors.warning[500] }} />
                <span>Bottleneck Analysis</span>
                <Tooltip title="Activities causing the most delays in your process">
                  <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                </Tooltip>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Table
              dataSource={mockBottlenecks}
              columns={bottleneckColumns}
              rowKey="activity"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>

        {/* Cycle Time Breakdown */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <ClockCircleOutlined style={{ color: tokens.colors.primary[500] }} />
                <span>Cycle Time Breakdown</span>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size={12}>
              {mockCycleTimeBreakdown.map((item) => (
                <div key={item.activity}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text>{item.activity}</Text>
                    <Text type="secondary">{formatDuration(item.avgTime)}</Text>
                  </div>
                  <Progress
                    percent={item.percentage}
                    showInfo={false}
                    strokeColor={
                      item.percentage > 30
                        ? tokens.colors.error[500]
                        : item.percentage > 15
                        ? tokens.colors.warning[500]
                        : tokens.colors.primary[500]
                    }
                    trailColor={tokens.colors.neutral[200]}
                  />
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>

      {/* Throughput Metrics */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined style={{ color: tokens.colors.success[500] }} />
            <span>Throughput Metrics</span>
          </Space>
        }
      >
        <Row gutter={24}>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                {mockThroughputData.casesPerDay}
              </Title>
              <Text type="secondary">Cases per Day</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                {formatCompactNumber(mockThroughputData.casesPerWeek)}
              </Title>
              <Text type="secondary">Cases per Week</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                {formatCompactNumber(mockThroughputData.casesPerMonth)}
              </Title>
              <Text type="secondary">Cases per Month</Text>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default PerformanceTab;
