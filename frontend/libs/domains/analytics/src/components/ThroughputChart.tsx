import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Space,
  Alert,
  Spin,
  Progress,
} from 'antd';
import {
  ThunderboltOutlined,
  CalendarOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import { useThroughput } from '../hooks';

const { Text } = Typography;

interface ThroughputChartProps {
  logId: string;
  compact?: boolean;
}

export const ThroughputChart: React.FC<ThroughputChartProps> = ({ logId, compact = false }) => {
  const { data, isLoading, error } = useThroughput(logId);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load throughput"
        description="Could not retrieve throughput data."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Spin tip="Loading throughput..." />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <Alert type="info" message="No throughput data available" />
      </Card>
    );
  }

  const casesPerWeek = data.casesPerDay * 7;
  const casesPerMonth = data.casesPerDay * 30;
  const eventsPerWeek = data.eventsPerDay * 7;

  // Calculate efficiency ratio (events per case)
  const eventsPerCase = data.casesPerDay > 0 ? data.eventsPerDay / data.casesPerDay : 0;

  if (compact) {
    return (
      <Card size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text type="secondary">Throughput</Text>
          <Statistic
            value={data.casesPerDay.toFixed(1)}
            suffix="cases/day"
            prefix={<ThunderboltOutlined />}
            valueStyle={{ fontSize: 20, color: '#52c41a' }}
          />
        </Space>
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <ThunderboltOutlined style={{ color: '#52c41a' }} />
          Throughput Metrics
        </Space>
      }
    >
      {/* Cases per time period */}
      <Row gutter={[16, 24]}>
        <Col xs={24}>
          <Text strong style={{ display: 'block', marginBottom: 12 }}>
            Cases Processed
          </Text>
        </Col>
        <Col xs={8}>
          <Statistic
            title="Per Day"
            value={data.casesPerDay.toFixed(1)}
            prefix={<RiseOutlined />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Per Week"
            value={casesPerWeek.toFixed(0)}
            prefix={<CalendarOutlined />}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Per Month"
            value={casesPerMonth.toFixed(0)}
            prefix={<CalendarOutlined />}
          />
        </Col>
      </Row>

      {/* Events per time period */}
      <Row gutter={[16, 24]} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Text strong style={{ display: 'block', marginBottom: 12 }}>
            Events Processed
          </Text>
        </Col>
        <Col xs={8}>
          <Statistic
            title="Per Day"
            value={data.eventsPerDay.toFixed(0)}
            valueStyle={{ color: '#0052cc' }}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Per Week"
            value={eventsPerWeek.toFixed(0)}
          />
        </Col>
        <Col xs={8}>
          <Statistic
            title="Avg Events/Case"
            value={eventsPerCase.toFixed(1)}
            valueStyle={{ color: '#722ed1' }}
          />
        </Col>
      </Row>

      {/* Efficiency Gauge */}
      <div style={{ marginTop: 24 }}>
        <Row align="middle" gutter={16}>
          <Col flex="auto">
            <Text>Processing Capacity</Text>
            <Progress
              percent={Math.min(data.casesPerDay * 10, 100)}
              strokeColor={{
                '0%': '#52c41a',
                '100%': '#0052cc',
              }}
              format={() => `${data.casesPerDay.toFixed(1)}/day`}
            />
          </Col>
        </Row>
        <Text type="secondary" style={{ fontSize: 11 }}>
          {data.casesPerDay >= 10
            ? 'High throughput - process is handling cases efficiently'
            : data.casesPerDay >= 1
            ? 'Moderate throughput - normal processing rate'
            : 'Low throughput - consider process optimization'}
        </Text>
      </div>
    </Card>
  );
};
