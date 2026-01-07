import { Row, Col, Card, Table, Tag, Typography } from 'antd';
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
  datasetId: string;
}

interface ReworkActivity {
  activity: string;
  reworkCount: number;
  casesWithRework: number;
  reworkPercentage: number;
}

/**
 * UnwantedActivitiesTab - Rework and exception analysis
 * Shows activities with high rework rates and their impact
 */
export function UnwantedActivitiesTab({ datasetId }: UnwantedActivitiesTabProps) {
  const { data: rework, isLoading, error, refetch } = useRework(datasetId);

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

  const totalRework = rework.totalReworkCases ?? 0;
  const reworkRate = (rework.reworkPercentage ?? 0) / 100; // Convert percentage to rate
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
      dataIndex: 'reworkPercentage',
      key: 'reworkPercentage',
      render: (rate: number) => (
        <Tag color={rate > 30 ? 'red' : rate > 15 ? 'orange' : 'green'}>
          {rate.toFixed(1)}%
        </Tag>
      ),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.reworkPercentage - b.reworkPercentage,
    },
    {
      title: 'Rework Count',
      dataIndex: 'reworkCount',
      key: 'reworkCount',
      render: (val: number) => val.toLocaleString(),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.reworkCount - b.reworkCount,
    },
    {
      title: 'Cases With Rework',
      dataIndex: 'casesWithRework',
      key: 'casesWithRework',
      render: (val: number) => val.toLocaleString(),
      sorter: (a: ReworkActivity, b: ReworkActivity) => a.casesWithRework - b.casesWithRework,
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
            value={activities.filter((a) => a.reworkPercentage > 0).length}
            suffix={`/ ${activities.length}`}
            prefix={<ExclamationCircleOutlined />}
            status={activities.filter((a) => a.reworkPercentage > 20).length > 0 ? 'warning' : 'default'}
          />
        </Col>
      </Row>

      <Row style={{ marginTop: tokens.spacing[4] }}>
        <Col span={24}>
          <Card title="Rework by Activity">
            <Table
              dataSource={activities.sort((a, b) => b.reworkPercentage - a.reworkPercentage)}
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

export default UnwantedActivitiesTab;
