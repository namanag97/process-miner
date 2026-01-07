import { Row, Col, Card, Typography, Progress, Empty } from 'antd';
import { CalendarOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import {
  MetricCard,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
} from '@/src/shared/design-system';
import { useDeadlines } from '@/src/api/hooks';

const { Text } = Typography;

interface DeadlinesTabProps {
  datasetId: string;
}

/**
 * DeadlinesTab - SLA compliance and deadline tracking
 * Shows on-time delivery rates and SLA violations
 */
export function DeadlinesTab({ datasetId }: DeadlinesTabProps) {
  const { data: deadlines, isLoading, error, refetch } = useDeadlines(datasetId);

  if (isLoading) {
    return <LoadingState type="card" rows={2} />;
  }

  if (error) {
    return <QueryError error={error} onRetry={() => refetch()} variant="card" />;
  }

  if (!deadlines) {
    return (
      <EmptyState
        icon={<CalendarOutlined />}
        title="No deadline data"
        description="Configure SLAs to track deadline compliance"
      />
    );
  }

  const onTimeRate = deadlines.onTimeRate ?? 0;
  const totalCases = deadlines.totalCases ?? 0;
  // Derive on-time and late cases from rate and total
  const onTimeCases = Math.round(totalCases * onTimeRate);
  const lateCases = totalCases - onTimeCases;

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="On-Time Delivery"
            value={`${(onTimeRate * 100).toFixed(1)}`}
            suffix="%"
            status={onTimeRate >= 0.95 ? 'success' : onTimeRate >= 0.8 ? 'warning' : 'error'}
            prefix={<CalendarOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="On-Time Cases"
            value={onTimeCases.toLocaleString()}
            prefix={<CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />}
            status="success"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Late Cases"
            value={lateCases.toLocaleString()}
            prefix={<CloseCircleOutlined style={{ color: tokens.colors.error[500] }} />}
            status={lateCases > 0 ? 'error' : 'default'}
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: tokens.spacing[4] }}>
        <Col xs={24} lg={12}>
          <Card title="SLA Compliance Overview">
            <Progress
              type="circle"
              percent={Math.round(onTimeRate * 100)}
              strokeColor={{
                '0%': tokens.colors.error[500],
                '50%': tokens.colors.warning[500],
                '100%': tokens.colors.success[500],
              }}
              format={(percent) => (
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 24, fontWeight: 600 }}>{percent}%</div>
                  <div style={{ fontSize: 12, color: tokens.colors.neutral[500] }}>Compliance</div>
                </div>
              )}
            />
            <div style={{ marginTop: tokens.spacing[4], textAlign: 'center' }}>
              <Text type="secondary">
                {onTimeCases} of {totalCases} cases delivered on time
              </Text>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="SLA Breakdown by Type">
            <Empty description="SLA breakdown requires configuration" />
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default DeadlinesTab;
