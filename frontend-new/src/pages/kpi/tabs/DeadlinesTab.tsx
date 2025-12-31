import React from 'react';
import { Row, Col, Card, Typography, Progress, Empty, Statistic } from 'antd';
import { CalendarOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import {
  MetricCard,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useDeadlines,
} from '@lumina/design-system';

const { Text } = Typography;

interface DeadlinesTabProps {
  logId: string;
}

/**
 * DeadlinesTab - SLA compliance and deadline tracking
 * Shows on-time delivery rates and SLA violations
 */
export function DeadlinesTab({ logId }: DeadlinesTabProps) {
  const { data: deadlines, isLoading, error, refetch } = useDeadlines(logId);

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
  const onTimeCases = deadlines.onTimeCases ?? 0;
  const lateCases = deadlines.lateCases ?? 0;

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
            {deadlines.slaBreakdown && deadlines.slaBreakdown.length > 0 ? (
              deadlines.slaBreakdown.map((sla: { name: string; compliance: number; target: number }, idx: number) => (
                <div key={idx} style={{ marginBottom: tokens.spacing[3] }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                    <Text>{sla.name}</Text>
                    <Text type={sla.compliance >= sla.target ? undefined : 'danger'}>
                      {(sla.compliance * 100).toFixed(1)}% (target: {(sla.target * 100).toFixed(0)}%)
                    </Text>
                  </div>
                  <Progress
                    percent={sla.compliance * 100}
                    showInfo={false}
                    status={sla.compliance >= sla.target ? 'success' : 'exception'}
                  />
                </div>
              ))
            ) : (
              <Empty description="No SLA types configured" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default DeadlinesTab;
