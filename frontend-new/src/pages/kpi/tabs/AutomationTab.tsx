import React from 'react';
import { Row, Col, Card, Table, Tag, Typography, Progress, List } from 'antd';
import { RobotOutlined, UserOutlined, ThunderboltOutlined } from '@ant-design/icons';
import {
  MetricCard,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useAutomation,
} from '@lumina/design-system';

const { Text } = Typography;

interface AutomationTabProps {
  logId: string;
}

interface ActivityAutomation {
  activity: string;
  automationRate: number;
  manualCount: number;
  automatedCount: number;
  potentialSavings: number;
}

/**
 * AutomationTab - Automation level analysis and opportunities
 * Shows current automation rates and potential for improvement
 */
export function AutomationTab({ logId }: AutomationTabProps) {
  const { data: automation, isLoading, error, refetch } = useAutomation(logId);

  if (isLoading) {
    return <LoadingState type="card" rows={2} />;
  }

  if (error) {
    return <QueryError error={error} onRetry={() => refetch()} variant="card" />;
  }

  if (!automation) {
    return (
      <EmptyState
        icon={<RobotOutlined />}
        title="No automation data"
        description="Automation analysis requires resource information in your event log"
      />
    );
  }

  const overallRate = automation.automationRate ?? 0;
  const totalSavings = automation.potentialSavingsHours ?? 0;
  // Activities breakdown is not yet available from the API
  const activities: ActivityAutomation[] = [];

  const columns = [
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Automation Rate',
      dataIndex: 'automationRate',
      key: 'automationRate',
      render: (rate: number) => (
        <Progress
          percent={Math.round(rate * 100)}
          size="small"
          status={rate >= 0.8 ? 'success' : rate >= 0.5 ? 'normal' : 'exception'}
          style={{ width: 100 }}
        />
      ),
      sorter: (a: ActivityAutomation, b: ActivityAutomation) => a.automationRate - b.automationRate,
    },
    {
      title: 'Manual',
      dataIndex: 'manualCount',
      key: 'manualCount',
      render: (val: number) => (
        <span>
          <UserOutlined style={{ marginRight: 4, color: tokens.colors.warning[500] }} />
          {val.toLocaleString()}
        </span>
      ),
    },
    {
      title: 'Automated',
      dataIndex: 'automatedCount',
      key: 'automatedCount',
      render: (val: number) => (
        <span>
          <RobotOutlined style={{ marginRight: 4, color: tokens.colors.success[500] }} />
          {val.toLocaleString()}
        </span>
      ),
    },
    {
      title: 'Savings Potential',
      dataIndex: 'potentialSavings',
      key: 'potentialSavings',
      render: (val: number) => (
        <Tag color={val > 100 ? 'gold' : 'default'}>
          {val.toFixed(0)} hrs/month
        </Tag>
      ),
      sorter: (a: ActivityAutomation, b: ActivityAutomation) => a.potentialSavings - b.potentialSavings,
    },
  ];

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Overall Automation"
            value={`${(overallRate * 100).toFixed(0)}`}
            suffix="%"
            status={overallRate >= 0.7 ? 'success' : overallRate >= 0.4 ? 'warning' : 'error'}
            prefix={<RobotOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Manual Activities"
            value={activities.filter((a) => a.automationRate < 0.5).length}
            prefix={<UserOutlined />}
            status="warning"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Potential Savings"
            value={totalSavings.toFixed(0)}
            suffix="hrs/month"
            prefix={<ThunderboltOutlined />}
            status="success"
          />
        </Col>
      </Row>

      <Row style={{ marginTop: tokens.spacing[4] }}>
        <Col span={24}>
          <Card title="Automation by Activity">
            <Table
              dataSource={activities.sort((a, b) => a.automationRate - b.automationRate)}
              columns={columns}
              rowKey="activity"
              pagination={{ pageSize: 10 }}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

    </div>
  );
}

export default AutomationTab;
