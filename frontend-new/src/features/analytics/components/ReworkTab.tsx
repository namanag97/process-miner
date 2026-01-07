import { Row, Col, Card, Table, Progress, Typography, Space, Tag, Tooltip, Skeleton } from 'antd';
import {
  ReloadOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { MetricCard, tokens, formatCompactNumber, type ReworkData } from '@lumina/design-system';
import { createLogger } from '../../../shared/lib/logger';

const { Text } = Typography;
const log = createLogger('ReworkTab');

interface ReworkTabProps {
  datasetId: string | null;
  data?: ReworkData;
  loading?: boolean;
}

export function ReworkTab({ datasetId, data, loading }: ReworkTabProps) {
  log.debug('Rendering ReworkTab', { datasetId, hasData: !!data });

  if (loading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <Text type="secondary">Select an event log to view rework analysis</Text>
      </Card>
    );
  }

  const reworkColumns = [
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Rework Count',
      dataIndex: 'reworkCount',
      key: 'reworkCount',
      render: (val: number) => (
        <Tag color={val > 100 ? 'error' : val > 50 ? 'warning' : 'default'}>
          {formatCompactNumber(val)}
        </Tag>
      ),
    },
    {
      title: 'Cases Affected',
      dataIndex: 'casesWithRework',
      key: 'casesWithRework',
      render: (val: number) => formatCompactNumber(val),
    },
    {
      title: 'Rework %',
      dataIndex: 'reworkPercentage',
      key: 'reworkPercentage',
      render: (val: number) => (
        <Progress
          percent={val}
          size="small"
          strokeColor={val > 20 ? tokens.colors.error[500] : val > 10 ? tokens.colors.warning[500] : tokens.colors.success[500]}
          style={{ width: 100 }}
        />
      ),
    },
  ];

  const reworkPercentage = data.reworkPercentage;

  return (
    <div>
      {/* KPI Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Rework Rate"
            value={`${reworkPercentage.toFixed(1)}%`}
            status={reworkPercentage > 25 ? 'error' : reworkPercentage > 15 ? 'warning' : 'success'}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Cases with Rework"
            value={formatCompactNumber(data.totalReworkCases)}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Activities with Rework"
            value={data.reworkActivities.length}
            status={data.reworkActivities.length > 5 ? 'warning' : 'default'}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Top Rework Activity"
            value={data.reworkActivities[0]?.activity ?? 'N/A'}
          />
        </Col>
      </Row>

      {/* Rework Summary Visual */}
      <Card style={{ marginBottom: tokens.spacing[6] }}>
        <Row gutter={24} align="middle">
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={reworkPercentage}
                strokeColor={reworkPercentage > 25 ? tokens.colors.error[500] : reworkPercentage > 15 ? tokens.colors.warning[500] : tokens.colors.success[500]}
                strokeWidth={10}
                size={140}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: tokens.fontSize['3xl'], fontWeight: tokens.fontWeight.bold }}>
                      {percent?.toFixed(1)}%
                    </div>
                    <div style={{ fontSize: tokens.fontSize.sm, color: tokens.colors.neutral[500] }}>
                      Rework Rate
                    </div>
                  </div>
                )}
              />
            </div>
          </Col>
          <Col xs={24} sm={16}>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text>Cases without rework</Text>
                  <Text strong>{(100 - reworkPercentage).toFixed(1)}%</Text>
                </div>
                <Progress
                  percent={100 - reworkPercentage}
                  strokeColor={tokens.colors.success[500]}
                  trailColor={tokens.colors.neutral[200]}
                  showInfo={false}
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text>Cases with rework</Text>
                  <Text strong>{reworkPercentage.toFixed(1)}%</Text>
                </div>
                <Progress
                  percent={reworkPercentage}
                  strokeColor={reworkPercentage > 25 ? tokens.colors.error[500] : tokens.colors.warning[500]}
                  trailColor={tokens.colors.neutral[200]}
                  showInfo={false}
                />
              </div>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Rework Activities Table */}
      <Card
        title={
          <Space>
            <ReloadOutlined style={{ color: tokens.colors.warning[500] }} />
            <span>Rework by Activity</span>
            <Tooltip title="Activities that are repeated within cases">
              <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
            </Tooltip>
          </Space>
        }
        style={{ marginBottom: tokens.spacing[6] }}
      >
        {data.reworkActivities.length > 0 ? (
          <Table
            dataSource={data.reworkActivities}
            columns={reworkColumns}
            rowKey="activity"
            pagination={false}
            size="middle"
          />
        ) : (
          <Text type="secondary">No rework detected in this log</Text>
        )}
      </Card>
    </div>
  );
}

export default ReworkTab;
