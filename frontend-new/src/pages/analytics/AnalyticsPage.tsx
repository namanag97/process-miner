import React, { useState } from 'react';
import { useNavigate, useLocation, Routes, Route } from 'react-router-dom';
import { Row, Col, Card, Tabs, Select, Space, Typography, Skeleton } from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { PageHeader, MetricCard, EmptyState, tokens, formatCompactNumber } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';
import { PerformanceTab } from './PerformanceTab';
import { ConformanceTab } from './ConformanceTab';
import { ReworkTab } from './ReworkTab';

const { Text } = Typography;
const log = createLogger('AnalyticsPage');

// Mock available logs for the selector
const mockLogs = [
  { id: '1', name: 'Orders_2024.csv', cases: 5340, events: 156000 },
  { id: '2', name: 'Claims_Process.xes', cases: 2890, events: 78000 },
  { id: '3', name: 'Purchase_Orders.csv', cases: 8200, events: 245000 },
];

// Mock summary stats
const mockSummaryStats = {
  avgCycleTime: '4.2 days',
  fitnessScore: 87.5,
  reworkRate: 23.4,
  bottlenecks: 5,
};

const tabItems = [
  {
    key: 'performance',
    label: (
      <Space>
        <LineChartOutlined />
        Performance
      </Space>
    ),
    children: <PerformanceTab />,
  },
  {
    key: 'conformance',
    label: (
      <Space>
        <CheckCircleOutlined />
        Conformance
      </Space>
    ),
    children: <ConformanceTab />,
  },
  {
    key: 'rework',
    label: (
      <Space>
        <ReloadOutlined />
        Rework Analysis
      </Space>
    ),
    children: <ReworkTab />,
  },
];

export function AnalyticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedLogId, setSelectedLogId] = useState<string>(mockLogs[0].id);
  const [isLoading, setIsLoading] = useState(false);

  // Determine active tab from URL
  const getActiveTab = () => {
    const path = location.pathname;
    if (path.includes('/conformance')) return 'conformance';
    if (path.includes('/rework')) return 'rework';
    return 'performance';
  };

  const handleTabChange = (key: string) => {
    log.debug('Tab changed', { tab: key });
    if (key === 'performance') {
      navigate('/analytics');
    } else {
      navigate(`/analytics/${key}`);
    }
  };

  const handleLogChange = (logId: string) => {
    log.info('Log selection changed', { logId });
    setSelectedLogId(logId);
    // Simulate loading new data
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 500);
  };

  const selectedLog = mockLogs.find((l) => l.id === selectedLogId);

  // If no logs available, show empty state
  if (mockLogs.length === 0) {
    return (
      <div>
        <PageHeader
          title="Analytics"
          description="Analyze your process performance, conformance, and rework patterns"
        />
        <EmptyState
          icon={<BarChartOutlined />}
          title="No event logs available"
          description="Upload an event log to start analyzing your processes"
          actionLabel="Upload Event Log"
          onAction={() => navigate('/logs/upload')}
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Analyze your process performance, conformance, and rework patterns"
        actions={
          <Space>
            <Text type="secondary">Analyzing:</Text>
            <Select
              value={selectedLogId}
              onChange={handleLogChange}
              style={{ width: 240 }}
              options={mockLogs.map((log) => ({
                value: log.id,
                label: (
                  <Space>
                    <span>{log.name}</span>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                      ({formatCompactNumber(log.cases)} cases)
                    </Text>
                  </Space>
                ),
              }))}
            />
          </Space>
        }
      />

      {/* Summary Stats Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Avg Cycle Time"
            value={mockSummaryStats.avgCycleTime}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Fitness Score"
            value={`${mockSummaryStats.fitnessScore}%`}
            status={mockSummaryStats.fitnessScore >= 85 ? 'success' : 'warning'}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Rework Rate"
            value={`${mockSummaryStats.reworkRate}%`}
            status={mockSummaryStats.reworkRate > 20 ? 'warning' : 'success'}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Bottlenecks"
            value={mockSummaryStats.bottlenecks}
            status="warning"
            loading={isLoading}
          />
        </Col>
      </Row>

      {/* Selected Log Info */}
      {selectedLog && (
        <Card
          size="small"
          style={{ marginBottom: tokens.spacing[4], backgroundColor: tokens.colors.neutral[50] }}
        >
          <Space>
            <InfoCircleOutlined style={{ color: tokens.colors.primary[500] }} />
            <Text>
              Analyzing <Text strong>{selectedLog.name}</Text> with{' '}
              <Text strong>{formatCompactNumber(selectedLog.cases)}</Text> cases and{' '}
              <Text strong>{formatCompactNumber(selectedLog.events)}</Text> events
            </Text>
          </Space>
        </Card>
      )}

      {/* Tabs for sub-pages */}
      {isLoading ? (
        <Card>
          <Skeleton active paragraph={{ rows: 10 }} />
        </Card>
      ) : (
        <Tabs
          activeKey={getActiveTab()}
          onChange={handleTabChange}
          items={tabItems}
          size="large"
          style={{ marginTop: tokens.spacing[4] }}
        />
      )}
    </div>
  );
}

export default AnalyticsPage;
