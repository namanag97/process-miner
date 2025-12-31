import React from 'react';
import { Row, Col, Card, Table, Tag, Typography, Statistic } from 'antd';
import { WarningOutlined, SyncOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import {
  MetricCard,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useRework,
} from '@lumina/design-system';

const { Text } = Typography;

interface UnwantedActivitiesTabProps {
  logId: string;
}

interface ReworkActivity {
  activity: string;
  reworkCount: number;
  reworkRate: number;
  avgRepetitions: number;
  impactedCases: number;
}

/**
 * UnwantedActivitiesTab - Rework and exception analysis
 * Shows activities with high rework rates and their impact
 */
export function UnwantedActivitiesTab({ logId }: UnwantedActivitiesTabProps) {
  const { data: rework, isLoading, error, refetch } = useRework(logId);

  if (isLoading) {
    return <LoadingState type="card" rows={2} />;
  }

  if (error) {
    return <QueryError error={error} onRetry={() => refetch()} variant="card" />;
  }

  if (!rework) {
    return (
      <EmptyState
        icon={<WarningOutlined />}
        title="No rework data"
        description="Rework analysis will appear once data is processed"
      />
    );
  }

  const totalRework = rework.totalReworkCount ?? 0;
  const reworkRate = rework.overallReworkRate ?? 0;
  const activities: ReworkActivity[] = rework.reworkActivities ?? [];

  const columns = [
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Rework Rate',
      dataIndex: 'reworkRate',
      key: 'reworkRate',
      render: (rate: number) => (
        <Tag color={rate > 0.3 ? 'red' : rate > 0.15 ? 'orange' : 'green'}>
          {(rate * 100).toFixed(1)}%
        </Tag>
      ),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.reworkRate - b.reworkRate,
    },
    {
      title: 'Avg Repetitions',
      dataIndex: 'avgRepetitions',
      key: 'avgRepetitions',
      render: (val: number) => val.toFixed(1),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.avgRepetitions - b.avgRepetitions,
    },
    {
      title: 'Impacted Cases',
      dataIndex: 'impactedCases',
      key: 'impactedCases',
      render: (val: number) => val.toLocaleString(),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.impactedCases - b.impactedCases,
    },
  ];

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Overall Rework Rate"
            value={`${(reworkRate * 100).toFixed(1)}`}
            suffix="%"
            status={reworkRate > 0.2 ? 'error' : reworkRate > 0.1 ? 'warning' : 'success'}
            prefix={<SyncOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Total Rework Events"
            value={totalRework.toLocaleString()}
            prefix={<WarningOutlined />}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Activities with Rework"
            value={activities.filter((a) => a.reworkRate > 0).length}
            suffix={`/ ${activities.length}`}
            prefix={<ExclamationCircleOutlined />}
            status={activities.filter((a) => a.reworkRate > 0.2).length > 0 ? 'warning' : 'default'}
          />
        </Col>
      </Row>

      <Row style={{ marginTop: tokens.spacing[4] }}>
        <Col span={24}>
          <Card title="Rework by Activity">
            <Table
              dataSource={activities.sort((a, b) => b.reworkRate - a.reworkRate)}
              columns={columns}
              rowKey="activity"
              pagination={{ pageSize: 10 }}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

      {rework.reworkPatterns && rework.reworkPatterns.length > 0 && (
        <Row style={{ marginTop: tokens.spacing[4] }}>
          <Col span={24}>
            <Card title="Common Rework Patterns">
              {rework.reworkPatterns.slice(0, 5).map((pattern: { sequence: string[]; count: number }, idx: number) => (
                <div
                  key={idx}
                  style={{
                    padding: tokens.spacing[3],
                    marginBottom: tokens.spacing[2],
                    backgroundColor: tokens.colors.neutral[50],
                    borderRadius: tokens.radius.md,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <Text>{pattern.sequence.join(' → ')}</Text>
                  <Tag>{pattern.count} occurrences</Tag>
                </div>
              ))}
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}

export default UnwantedActivitiesTab;
