/**
 * AnalyticsPage - Process Analytics Dashboard
 *
 * Comprehensive analytics including:
 * - Performance metrics and bottleneck analysis
 * - Conformance checking
 * - Rework pattern analysis
 * - Resource utilization
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, useSearchParams, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Row, Col, Card, Tabs, Select, Space, Typography, Skeleton, Alert } from 'antd';
import {
  BarChartOutlined,
  LineChartOutlined,
  CheckCircleOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { PageHeader, MetricCard, EmptyState, tokens, formatCompactNumber, useSDK, formatDurationFromSeconds, type EventLog, logAction } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';
import { PerformanceTab, ConformanceTab, ReworkTab, ResourcesTab } from '../components';

const { Text } = Typography;
const log = createLogger('AnalyticsPage');

export function AnalyticsPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const { projectId } = useParams<{ projectId?: string; tab?: string }>();
  const sdk = useSDK();
  const [selectedLogId, setSelectedLogId] = useState<string | null>(null);

  // Fetch available logs
  const { data: logsData, isLoading: logsLoading, error: logsError } = useQuery({
    queryKey: ['processes'],
    queryFn: () => sdk.processes.list({ pageSize: 50 }),
  });

  const logs = logsData?.items ?? [];

  // Read logId from URL query param or auto-select first log
  useEffect(() => {
    const urlLogId = searchParams.get('logId');
    if (urlLogId && logs.some((l: EventLog) => l.id === urlLogId)) {
      setSelectedLogId(urlLogId);
      log.debug('Selected log from URL param', { logId: urlLogId });
    } else if (!selectedLogId && logs.length > 0) {
      setSelectedLogId(logs[0].id);
    }
  }, [logs, selectedLogId, searchParams]);

  // Fetch performance data for selected log
  const { data: performanceData, isLoading: perfLoading, error: perfError } = useQuery({
    queryKey: ['analytics', 'performance', selectedLogId],
    queryFn: () => sdk.analytics.getPerformance(selectedLogId!),
    enabled: !!selectedLogId,
  });

  // Fetch rework data for selected log
  const { data: reworkData, isLoading: reworkLoading } = useQuery({
    queryKey: ['analytics', 'rework', selectedLogId],
    queryFn: () => sdk.analytics.getRework(selectedLogId!),
    enabled: !!selectedLogId,
  });

  const isLoading = logsLoading || perfLoading || reworkLoading;

  // Determine active tab from URL
  const getActiveTab = () => {
    const path = location.pathname;
    if (path.includes('/conformance')) return 'conformance';
    if (path.includes('/rework')) return 'rework';
    if (path.includes('/resources')) return 'resources';
    return 'performance';
  };

  const handleTabChange = (key: string) => {
    logAction('AnalyticsPage', 'tab_changed', { from: getActiveTab(), to: key });
    log.debug('Tab changed', { tab: key });
    if (projectId) {
      // Project-scoped navigation
      if (key === 'performance') {
        navigate(`/workspace/${projectId}/analytics`);
      } else {
        navigate(`/workspace/${projectId}/analytics/${key}`);
      }
    } else {
      // Standalone navigation
      if (key === 'performance') {
        navigate('/analytics');
      } else {
        navigate(`/analytics/${key}`);
      }
    }
  };

  const handleLogChange = (logId: string) => {
    logAction('AnalyticsPage', 'log_selected', { logId });
    log.info('Log selection changed', { logId });
    setSelectedLogId(logId);
    navigate(`${location.pathname}?logId=${logId}`, { replace: true });
  };

  const selectedLog = logs.find((l: EventLog) => l.id === selectedLogId);

  // Summary stats from performance data
  const avgCycleTime = performanceData?.cycleTime?.avgSeconds != null
    ? formatDurationFromSeconds(performanceData.cycleTime.avgSeconds)
    : 'N/A';

  const reworkRate = reworkData?.reworkPercentage ?? null;
  const bottleneckCount = performanceData?.topBottlenecks?.length ?? 0;

  const tabItems = [
    {
      key: 'performance',
      label: (
        <Space>
          <LineChartOutlined />
          Performance
        </Space>
      ),
      children: <PerformanceTab logId={selectedLogId} data={performanceData} loading={perfLoading} />,
    },
    {
      key: 'conformance',
      label: (
        <Space>
          <CheckCircleOutlined />
          Conformance
        </Space>
      ),
      children: <ConformanceTab logId={selectedLogId} />,
    },
    {
      key: 'rework',
      label: (
        <Space>
          <ReloadOutlined />
          Rework Analysis
        </Space>
      ),
      children: <ReworkTab logId={selectedLogId} data={reworkData} loading={reworkLoading} />,
    },
    {
      key: 'resources',
      label: (
        <Space>
          <TeamOutlined />
          Resources
        </Space>
      ),
      children: <ResourcesTab logId={selectedLogId} />,
    },
  ];

  // Build breadcrumbs based on context
  const getBreadcrumbs = () => {
    if (projectId) {
      return [
        { label: 'Workspace', href: '/workspace' },
        { label: 'Project', href: `/workspace/${projectId}` },
        { label: 'Analytics' },
      ];
    }
    return [
      { label: 'Workspace', href: '/workspace' },
      { label: 'Analytics' },
    ];
  };

  // Error state
  if (logsError) {
    return (
      <div>
        <PageHeader
          title="Analytics"
          description="Analyze your process performance, conformance, and rework patterns"
          breadcrumb={getBreadcrumbs()}
        />
        <Alert
          message="Failed to load event logs"
          description={(logsError as Error).message}
          type="error"
          showIcon
        />
      </div>
    );
  }

  // If no logs available, show empty state
  if (!logsLoading && logs.length === 0) {
    return (
      <div>
        <PageHeader
          title="Analytics"
          description="Analyze your process performance, conformance, and rework patterns"
          breadcrumb={getBreadcrumbs()}
        />
        <EmptyState
          icon={<BarChartOutlined />}
          title="No event logs available"
          description="Upload an event log to start analyzing your processes"
          actionLabel="Upload Event Log"
          onAction={() => navigate(projectId ? `/workspace/${projectId}` : '/workspace')}
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Analyze your process performance, conformance, and rework patterns"
        breadcrumb={getBreadcrumbs()}
        actions={
          <Space>
            <Text type="secondary">Analyzing:</Text>
            <Select
              value={selectedLogId ?? undefined}
              onChange={handleLogChange}
              style={{ width: 240 }}
              loading={logsLoading}
              placeholder="Select a log..."
              options={logs.map((logItem: EventLog) => ({
                value: logItem.id,
                label: (
                  <Space>
                    <span>{logItem.name}</span>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                      ({formatCompactNumber(logItem.totalCases)} cases)
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
            value={avgCycleTime}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Throughput"
            value={performanceData?.throughput?.casesPerDay != null
              ? performanceData.throughput.casesPerDay.toFixed(1)
              : 'N/A'}
            suffix={performanceData?.throughput?.casesPerDay != null ? 'cases/day' : undefined}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Rework Rate"
            value={reworkRate != null ? `${reworkRate.toFixed(1)}%` : 'N/A'}
            status={reworkRate != null && reworkRate > 20 ? 'warning' : 'success'}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Bottlenecks"
            value={bottleneckCount}
            status={bottleneckCount > 3 ? 'warning' : 'default'}
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
              <Text strong>{formatCompactNumber(selectedLog.totalCases)}</Text> cases and{' '}
              <Text strong>{formatCompactNumber(selectedLog.totalEvents)}</Text> events
            </Text>
          </Space>
        </Card>
      )}

      {/* Tabs for sub-pages */}
      {isLoading && !performanceData ? (
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
