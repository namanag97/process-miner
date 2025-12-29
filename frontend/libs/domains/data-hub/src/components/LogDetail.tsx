import React from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Skeleton,
  Tabs,
  Table,
  Tag,
  Alert,
  Button,
  Descriptions,
  Space,
  Progress,
} from 'antd';
import {
  PlayCircleOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  CalendarOutlined,
  UserOutlined,
  BranchesOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useLog, useLogStatistics, useLogQuality, useLogVariants } from '../hooks';
import { QualityReport } from './QualityReport';
import { formatCompactNumber, formatDurationFromSeconds } from '@lumina/design-system';

const { Title, Text } = Typography;

interface LogDetailProps {
  logId: string;
}

export const LogDetail: React.FC<LogDetailProps> = ({ logId }) => {
  const navigate = useNavigate();
  const { data: log, isLoading: logLoading, error: logError } = useLog(logId);
  const { data: stats, isLoading: statsLoading } = useLogStatistics(logId);
  const { data: quality, isLoading: qualityLoading } = useLogQuality(logId);
  const { data: variants, isLoading: variantsLoading } = useLogVariants(logId);

  if (logError) {
    return (
      <Alert
        type="error"
        message="Failed to load event log"
        description="The event log could not be found or you don't have permission to access it."
        action={
          <Button onClick={() => navigate('/data/logs')}>Back to Logs</Button>
        }
      />
    );
  }

  const variantColumns = [
    {
      title: '#',
      key: 'index',
      width: 50,
      render: (_: unknown, __: unknown, index: number) => index + 1,
    },
    {
      title: 'Variant',
      dataIndex: 'activities',
      key: 'activities',
      render: (activities: string[]) => (
        <Text ellipsis style={{ maxWidth: 400 }}>
          {activities.join(' → ')}
        </Text>
      ),
    },
    {
      title: 'Cases',
      dataIndex: 'caseCount',
      key: 'caseCount',
      width: 100,
      render: (count: number) => formatCompactNumber(count),
    },
    {
      title: 'Frequency',
      dataIndex: 'frequencyPercent',
      key: 'frequencyPercent',
      width: 120,
      render: (percent: number) => (
        <Progress percent={percent} size="small" format={(p) => `${p?.toFixed(1)}%`} />
      ),
    },
    {
      title: 'Avg Duration',
      dataIndex: 'avgDurationSeconds',
      key: 'avgDurationSeconds',
      width: 120,
      render: (seconds: number) => formatDurationFromSeconds(seconds),
    },
    {
      title: '',
      key: 'tags',
      width: 100,
      render: (_: unknown, record: { isHappyPath?: boolean }) =>
        record.isHappyPath && <Tag color="green">Happy Path</Tag>,
    },
  ];

  const tabItems = [
    {
      key: 'overview',
      label: 'Overview',
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="Log Information" size="small">
              {logLoading ? (
                <Skeleton active />
              ) : (
                <Descriptions column={3} size="small">
                  <Descriptions.Item label="Name">{log?.name}</Descriptions.Item>
                  <Descriptions.Item label="Source File">{log?.sourceFile || 'Uploaded'}</Descriptions.Item>
                  <Descriptions.Item label="Created">
                    {log?.createdAt && new Date(log.createdAt).toLocaleString()}
                  </Descriptions.Item>
                  <Descriptions.Item label="Description" span={3}>
                    {log?.description || 'No description provided'}
                  </Descriptions.Item>
                </Descriptions>
              )}
            </Card>
          </Col>

          <Col span={24}>
            <Card title="Activity Distribution" size="small">
              {statsLoading ? (
                <Skeleton active />
              ) : (
                <Row gutter={16}>
                  <Col span={12}>
                    <Text strong>Start Activities</Text>
                    <div style={{ marginTop: 8 }}>
                      {stats?.startActivities &&
                        Object.entries(stats.startActivities)
                          .sort(([, a], [, b]) => (b as number) - (a as number))
                          .slice(0, 5)
                          .map(([activity, count]) => (
                            <Tag key={activity} style={{ marginBottom: 4 }}>
                              {activity}: {formatCompactNumber(count as number)}
                            </Tag>
                          ))}
                    </div>
                  </Col>
                  <Col span={12}>
                    <Text strong>End Activities</Text>
                    <div style={{ marginTop: 8 }}>
                      {stats?.endActivities &&
                        Object.entries(stats.endActivities)
                          .sort(([, a], [, b]) => (b as number) - (a as number))
                          .slice(0, 5)
                          .map(([activity, count]) => (
                            <Tag key={activity} style={{ marginBottom: 4 }}>
                              {activity}: {formatCompactNumber(count as number)}
                            </Tag>
                          ))}
                    </div>
                  </Col>
                </Row>
              )}
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'variants',
      label: 'Variants',
      children: (
        <Card size="small">
          <Table
            columns={variantColumns}
            dataSource={variants?.map((v, i) => ({ ...v, key: v.key || i })) || []}
            loading={variantsLoading}
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </Card>
      ),
    },
    {
      key: 'quality',
      label: 'Quality',
      children: <QualityReport logId={logId} />,
    },
  ];

  return (
    <div>
      {/* Header with actions */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          {logLoading ? (
            <Skeleton.Input active style={{ width: 200 }} />
          ) : (
            <>
              <Title level={3} style={{ marginBottom: 4 }}>{log?.name}</Title>
              <Text type="secondary">Event log ID: {logId}</Text>
            </>
          )}
        </div>
        <Space>
          <Button icon={<PlayCircleOutlined />} onClick={() => navigate(`/explorer/${logId}`)}>
            Process Explorer
          </Button>
          <Button icon={<BarChartOutlined />} onClick={() => navigate(`/analytics/${logId}`)}>
            Analytics
          </Button>
          <Button icon={<CheckCircleOutlined />} onClick={() => navigate(`/conformance/${logId}`)}>
            Conformance
          </Button>
        </Space>
      </div>

      {/* Statistics Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Total Cases"
                value={stats?.caseCount || log?.totalCases || 0}
                prefix={<BranchesOutlined />}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Total Events"
                value={stats?.eventCount || log?.totalEvents || 0}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Activities"
                value={stats?.activityCount || log?.uniqueActivities || 0}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Variants"
                value={stats?.variantCount || log?.variantCount || 0}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Performance Stats */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Avg Case Duration"
                value={formatDurationFromSeconds(stats?.avgCaseDurationSeconds || 0)}
                prefix={<CalendarOutlined />}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Median Duration"
                value={formatDurationFromSeconds(stats?.medianCaseDurationSeconds || 0)}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {statsLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Resources"
                value={stats?.resourceCount || log?.uniqueResources || 0}
                prefix={<UserOutlined />}
              />
            )}
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card size="small">
            {qualityLoading ? (
              <Skeleton.Input active />
            ) : (
              <Statistic
                title="Quality Score"
                value={quality?.overallScore || 0}
                suffix="%"
                valueStyle={{
                  color:
                    (quality?.overallScore || 0) >= 80
                      ? '#52c41a'
                      : (quality?.overallScore || 0) >= 60
                      ? '#faad14'
                      : '#ff4d4f',
                }}
              />
            )}
          </Card>
        </Col>
      </Row>

      {/* Tabs */}
      <Card>
        <Tabs items={tabItems} />
      </Card>
    </div>
  );
};
