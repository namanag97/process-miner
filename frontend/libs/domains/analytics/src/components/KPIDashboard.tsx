import React from 'react';
import { Row, Col, Card, Statistic, Spin, Alert, Space, Tooltip } from 'antd';
import {
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { usePerformanceDashboard } from '../hooks';

interface KPIDashboardProps {
  logId: string;
  compact?: boolean;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

function formatThroughput(casesPerDay: number): string {
  if (casesPerDay >= 1) return `${casesPerDay.toFixed(1)}/day`;
  if (casesPerDay >= 1 / 7) return `${(casesPerDay * 7).toFixed(1)}/week`;
  return `${(casesPerDay * 30).toFixed(1)}/month`;
}

export const KPIDashboard: React.FC<KPIDashboardProps> = ({ logId, compact = false }) => {
  const { data, isLoading, error } = usePerformanceDashboard(logId);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load performance metrics"
        description="Could not retrieve performance data for this log."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Spin tip="Loading performance metrics..." />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <Alert type="info" message="No performance data available" />
      </Card>
    );
  }

  const { summary } = data;

  const kpis = [
    {
      title: (
        <Tooltip title="Average time to complete a case from start to finish">
          <Space>
            Avg Cycle Time
            <InfoCircleOutlined style={{ fontSize: 12, color: '#8c8c8c' }} />
          </Space>
        </Tooltip>
      ),
      value: formatDuration(summary.avgCycleTime),
      icon: <ClockCircleOutlined style={{ color: '#0052cc' }} />,
      color: '#0052cc',
    },
    {
      title: (
        <Tooltip title="Average cases processed per time period">
          <Space>
            Throughput
            <InfoCircleOutlined style={{ fontSize: 12, color: '#8c8c8c' }} />
          </Space>
        </Tooltip>
      ),
      value: formatThroughput(summary.avgThroughput),
      icon: <ThunderboltOutlined style={{ color: '#52c41a' }} />,
      color: '#52c41a',
    },
    {
      title: (
        <Tooltip title="Number of activities identified as bottlenecks">
          <Space>
            Bottlenecks
            <InfoCircleOutlined style={{ fontSize: 12, color: '#8c8c8c' }} />
          </Space>
        </Tooltip>
      ),
      value: summary.bottleneckCount,
      icon: <WarningOutlined style={{ color: summary.bottleneckCount > 3 ? '#ff4d4f' : '#faad14' }} />,
      color: summary.bottleneckCount > 3 ? '#ff4d4f' : '#faad14',
      suffix: summary.bottleneckCount > 3 ? 'High' : summary.bottleneckCount > 0 ? 'Detected' : '',
    },
    {
      title: (
        <Tooltip title="Percentage of cases with repeated activities">
          <Space>
            Rework Rate
            <InfoCircleOutlined style={{ fontSize: 12, color: '#8c8c8c' }} />
          </Space>
        </Tooltip>
      ),
      value: `${(summary.reworkRate * 100).toFixed(1)}%`,
      icon: <ReloadOutlined style={{ color: summary.reworkRate > 0.2 ? '#ff4d4f' : '#722ed1' }} />,
      color: summary.reworkRate > 0.2 ? '#ff4d4f' : '#722ed1',
    },
  ];

  if (compact) {
    return (
      <Row gutter={[8, 8]}>
        {kpis.map((kpi, index) => (
          <Col xs={12} sm={6} key={index}>
            <Card size="small" styles={{ body: { padding: 12 } }}>
              <Statistic
                title={kpi.title}
                value={kpi.value}
                prefix={kpi.icon}
                valueStyle={{ fontSize: 16, color: kpi.color }}
                suffix={kpi.suffix}
              />
            </Card>
          </Col>
        ))}
      </Row>
    );
  }

  return (
    <Card title="Performance KPIs">
      <Row gutter={[16, 16]}>
        {kpis.map((kpi, index) => (
          <Col xs={12} md={6} key={index}>
            <Card
              styles={{
                body: {
                  padding: 16,
                  background: `linear-gradient(135deg, ${kpi.color}08 0%, ${kpi.color}03 100%)`,
                  borderLeft: `3px solid ${kpi.color}`,
                },
              }}
            >
              <Statistic
                title={kpi.title}
                value={kpi.value}
                prefix={kpi.icon}
                valueStyle={{ color: kpi.color }}
                suffix={kpi.suffix}
              />
            </Card>
          </Col>
        ))}
      </Row>
    </Card>
  );
};
