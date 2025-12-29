import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Typography,
  Space,
  Alert,
  Spin,
  Divider,
  Tooltip,
} from 'antd';
import {
  ClockCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { useCycleTime } from '../hooks';

const { Text, Title } = Typography;

interface CycleTimeChartProps {
  logId: string;
  compact?: boolean;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

export const CycleTimeChart: React.FC<CycleTimeChartProps> = ({ logId, compact = false }) => {
  const { data, isLoading, error } = useCycleTime(logId);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load cycle time"
        description="Could not retrieve cycle time data."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Spin tip="Loading cycle time..." />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <Alert type="info" message="No cycle time data available" />
      </Card>
    );
  }

  const range = data.maxCycleTime - data.minCycleTime;
  const avgPosition = range > 0 ? ((data.avgCycleTime - data.minCycleTime) / range) * 100 : 50;
  const medianPosition = range > 0 ? ((data.medianCycleTime - data.minCycleTime) / range) * 100 : 50;

  // Calculate variance indicator
  const coefficient = data.avgCycleTime > 0 ? range / data.avgCycleTime : 0;
  const variability = coefficient > 2 ? 'High' : coefficient > 1 ? 'Medium' : 'Low';
  const variabilityColor = coefficient > 2 ? '#ff4d4f' : coefficient > 1 ? '#faad14' : '#52c41a';

  if (compact) {
    return (
      <Card size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text type="secondary">Cycle Time</Text>
          <Statistic
            value={formatDuration(data.avgCycleTime)}
            prefix={<ClockCircleOutlined />}
            valueStyle={{ fontSize: 20 }}
          />
          <Text type="secondary" style={{ fontSize: 11 }}>
            Range: {formatDuration(data.minCycleTime)} - {formatDuration(data.maxCycleTime)}
          </Text>
        </Space>
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <ClockCircleOutlined style={{ color: '#0052cc' }} />
          Cycle Time Analysis
        </Space>
      }
    >
      {/* Main Statistics */}
      <Row gutter={[16, 16]}>
        <Col xs={12} sm={6}>
          <Statistic
            title="Average"
            value={formatDuration(data.avgCycleTime)}
            prefix={<LineChartOutlined />}
            valueStyle={{ color: '#0052cc' }}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Median"
            value={formatDuration(data.medianCycleTime)}
            valueStyle={{ color: '#722ed1' }}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Minimum"
            value={formatDuration(data.minCycleTime)}
            prefix={<ArrowDownOutlined style={{ color: '#52c41a' }} />}
            valueStyle={{ color: '#52c41a' }}
          />
        </Col>
        <Col xs={12} sm={6}>
          <Statistic
            title="Maximum"
            value={formatDuration(data.maxCycleTime)}
            prefix={<ArrowUpOutlined style={{ color: '#ff4d4f' }} />}
            valueStyle={{ color: '#ff4d4f' }}
          />
        </Col>
      </Row>

      <Divider />

      {/* Distribution Visualization */}
      <div style={{ marginBottom: 16 }}>
        <Title level={5}>Distribution</Title>
        <div
          style={{
            position: 'relative',
            height: 60,
            background: 'linear-gradient(90deg, #52c41a 0%, #faad14 50%, #ff4d4f 100%)',
            borderRadius: 4,
            marginBottom: 8,
          }}
        >
          {/* Average marker */}
          <Tooltip title={`Average: ${formatDuration(data.avgCycleTime)}`}>
            <div
              style={{
                position: 'absolute',
                left: `${avgPosition}%`,
                top: 0,
                bottom: 0,
                width: 2,
                background: '#0052cc',
                zIndex: 2,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  top: -20,
                  left: -15,
                  width: 30,
                  textAlign: 'center',
                  fontSize: 11,
                  fontWeight: 'bold',
                  color: '#0052cc',
                }}
              >
                AVG
              </div>
            </div>
          </Tooltip>

          {/* Median marker */}
          <Tooltip title={`Median: ${formatDuration(data.medianCycleTime)}`}>
            <div
              style={{
                position: 'absolute',
                left: `${medianPosition}%`,
                top: 0,
                bottom: 0,
                width: 2,
                background: '#722ed1',
                zIndex: 2,
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  bottom: -20,
                  left: -15,
                  width: 30,
                  textAlign: 'center',
                  fontSize: 11,
                  fontWeight: 'bold',
                  color: '#722ed1',
                }}
              >
                MED
              </div>
            </div>
          </Tooltip>
        </div>
        <Row justify="space-between">
          <Col>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {formatDuration(data.minCycleTime)}
            </Text>
          </Col>
          <Col>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {formatDuration(data.maxCycleTime)}
            </Text>
          </Col>
        </Row>
      </div>

      {/* Variability Indicator */}
      <div style={{ marginTop: 16 }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Text>Process Variability</Text>
          </Col>
          <Col>
            <Space>
              <Progress
                type="circle"
                percent={Math.min(coefficient * 33.3, 100)}
                size={40}
                strokeColor={variabilityColor}
                format={() => variability}
              />
            </Space>
          </Col>
        </Row>
        <Text type="secondary" style={{ fontSize: 11 }}>
          {variability === 'High'
            ? 'High variance in case durations - consider investigating outliers'
            : variability === 'Medium'
            ? 'Moderate variance - some cases take significantly longer'
            : 'Low variance - consistent process execution times'}
        </Text>
      </div>
    </Card>
  );
};
