
import { Row, Col, Card, Typography, Progress, List, Statistic } from 'antd';
import { ClockCircleOutlined, ThunderboltOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import {
  MetricCard,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  formatDurationFromSeconds,
  usePerformance,
  useCycleTime,
  useThroughput,
} from '@lumina/design-system';

const { Text: _Text } = Typography;

interface PerformanceTabProps {
  datasetId: string;
}

/**
 * PerformanceTab - Performance metrics and cycle time analysis (KPI Dashboard version)
 * Shows throughput, bottlenecks, and timing statistics using hooks-based data fetching.
 *
 * NOTE: There are two PerformanceTab components in this codebase:
 * - analytics/components/PerformanceTab.tsx - Props-based, detailed table view
 * - kpi/components/PerformanceTab.tsx (this file) - Hooks-based, simpler list view
 *
 * These are intentionally separate as they serve different UX purposes.
 */
export function PerformanceTab({ datasetId }: PerformanceTabProps) {
  const { data: performance, isLoading: perfLoading, error: perfError, refetch: refetchPerf } = usePerformance(datasetId);
  const { data: cycleTime, isLoading: cycleLoading } = useCycleTime(datasetId);
  const { data: throughput, isLoading: throughputLoading } = useThroughput(datasetId);

  const isLoading = perfLoading || cycleLoading || throughputLoading;

  if (isLoading) {
    return <LoadingState type="card" rows={3} />;
  }

  if (perfError) {
    return <QueryError error={perfError} onRetry={() => refetchPerf()} variant="card" />;
  }

  if (!performance) {
    return (
      <EmptyState
        icon={<ClockCircleOutlined />}
        title="No performance data"
        description="Performance metrics will appear once data is processed"
      />
    );
  }

  // Calculate efficiency from performance data (throughput ratio)
  const totalCases = throughput?.total_cases ?? 0;
  const completedCases = throughput?.completed_cases ?? 0;
  const efficiency = totalCases > 0 ? completedCases / totalCases : 0;

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Avg Cycle Time"
            value={formatDurationFromSeconds(cycleTime?.avg_seconds ?? 0)}
            prefix={<ClockCircleOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Throughput"
            value={throughput?.cases_per_day?.toFixed(1) ?? '0'}
            suffix="cases/day"
            prefix={<ThunderboltOutlined />}
            status="success"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Process Efficiency"
            value={`${(efficiency * 100).toFixed(0)}`}
            suffix="%"
            status={efficiency > 0.7 ? 'success' : efficiency > 0.4 ? 'warning' : 'error'}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: tokens.spacing[4] }}>
        <Col xs={24} lg={12}>
          <Card title="Bottleneck Activities">
            <List
              dataSource={performance.topBottlenecks?.slice(0, 5) ?? []}
              renderItem={(item: { activity: string; avgWaitingTime: number; impactScore: number }) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.activity}
                    description={`Wait time: ${formatDurationFromSeconds(item.avgWaitingTime)}`}
                  />
                  <Progress
                    percent={Math.round(item.impactScore * 100)}
                    size="small"
                    status={item.impactScore > 0.5 ? 'exception' : 'normal'}
                    style={{ width: 100 }}
                  />
                </List.Item>
              )}
              locale={{ emptyText: 'No bottlenecks detected' }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="Cycle Time Distribution">
            <div style={{ display: 'flex', gap: tokens.spacing[4], flexWrap: 'wrap' }}>
              <Statistic
                title="Minimum"
                value={formatDurationFromSeconds(cycleTime?.min_seconds ?? 0)}
                prefix={<ArrowDownOutlined style={{ color: tokens.colors.success[500] }} />}
              />
              <Statistic
                title="Median"
                value={formatDurationFromSeconds(cycleTime?.median_seconds ?? 0)}
              />
              <Statistic
                title="Maximum"
                value={formatDurationFromSeconds(cycleTime?.max_seconds ?? 0)}
                prefix={<ArrowUpOutlined style={{ color: tokens.colors.error[500] }} />}
              />
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default PerformanceTab;
