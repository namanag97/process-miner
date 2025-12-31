import React from 'react';
import { Row, Col, Card, Table, Progress, Typography, Space, Tooltip, Skeleton } from 'antd';
import {
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { MetricCard, tokens, formatDurationFromSeconds, formatCompactNumber, type PerformanceData } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text, Title } = Typography;
const log = createLogger('PerformanceTab');

interface PerformanceTabProps {
  logId: string | null;
  data?: PerformanceData;
  loading?: boolean;
}

export function PerformanceTab({ logId, data, loading }: PerformanceTabProps) {
  log.debug('Rendering PerformanceTab', { logId, hasData: !!data });

  if (loading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <Text type="secondary">Select an event log to view performance metrics</Text>
      </Card>
    );
  }

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
      title: 'Avg Wait Time',
      dataIndex: 'avgWaitingTime',
      key: 'avgWaitingTime',
      render: (seconds: number) => formatDurationFromSeconds(seconds),
    },
    {
      title: 'Impact Score',
      dataIndex: 'impactScore',
      key: 'impactScore',
      render: (val: number) => (
        <Progress
          percent={Math.round(val * 100)}
          size="small"
          strokeColor={val > 0.7 ? tokens.colors.error[500] : val > 0.4 ? tokens.colors.warning[500] : tokens.colors.success[500]}
          showInfo={false}
          style={{ width: 100 }}
        />
      ),
    },
  ];

  const avgCycleTimeDays = data.cycleTime.avgSeconds / 86400;
  const throughputPerDay = data.throughput.casesPerDay;

  return (
    <div>
      {/* KPI Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Avg Cycle Time"
            value={avgCycleTimeDays.toFixed(1)}
            suffix="days"
            status="success"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Throughput"
            value={throughputPerDay.toFixed(1)}
            suffix="cases/day"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Bottleneck Activities"
            value={data.topBottlenecks.length}
            status={data.topBottlenecks.length > 3 ? 'warning' : 'default'}
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
            {data.topBottlenecks.length > 0 ? (
              <Table
                dataSource={data.topBottlenecks}
                columns={bottleneckColumns}
                rowKey="activity"
                pagination={false}
                size="middle"
              />
            ) : (
              <Text type="secondary">No bottlenecks detected</Text>
            )}
          </Card>
        </Col>

        {/* Cycle Time Stats */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <ClockCircleOutlined style={{ color: tokens.colors.primary[500] }} />
                <span>Cycle Time Distribution</span>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Space direction="vertical" style={{ width: '100%' }} size={12}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Minimum</Text>
                <Text strong>{formatDurationFromSeconds(data.cycleTime.minSeconds)}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Median</Text>
                <Text strong>{formatDurationFromSeconds(data.cycleTime.medianSeconds)}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Average</Text>
                <Text strong>{formatDurationFromSeconds(data.cycleTime.avgSeconds)}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>75th Percentile</Text>
                <Text strong>{formatDurationFromSeconds(data.cycleTime.percentile75)}</Text>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Text>Maximum</Text>
                <Text strong>{formatDurationFromSeconds(data.cycleTime.maxSeconds)}</Text>
              </div>
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
                {data.throughput.casesPerDay.toFixed(1)}
              </Title>
              <Text type="secondary">Cases per Day</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                {formatCompactNumber(data.throughput.casesPerWeek)}
              </Title>
              <Text type="secondary">Cases per Week</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                {formatCompactNumber(data.throughput.casesPerMonth)}
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
