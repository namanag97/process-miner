import React from 'react';
import { Row, Col, Card, Table, Progress, Typography, Space, Tooltip, Skeleton, Empty } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  SwapOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { MetricCard, tokens, formatDurationFromSeconds, useSDK } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text, Title } = Typography;
const log = createLogger('ResourcesTab');

interface ResourceData {
  name: string;
  caseCount: number;
  eventCount: number;
  avgDuration: number | null;
  workloadPercent: number;
}

interface HandoverData {
  from: string;
  to: string;
  frequency: number;
}

interface ResourcesTabProps {
  logId: string | null;
}

export function ResourcesTab({ logId }: ResourcesTabProps) {
  const sdk = useSDK();

  // Fetch workload distribution
  const { data: workloadData, isLoading: workloadLoading } = useQuery({
    queryKey: ['organizational', 'workload', logId],
    queryFn: () => sdk.organizational.getWorkload(logId!),
    enabled: !!logId,
  });

  // Fetch handover network
  const { data: handoverData, isLoading: handoverLoading } = useQuery({
    queryKey: ['organizational', 'handover', logId],
    queryFn: () => sdk.organizational.getHandoverNetwork(logId!),
    enabled: !!logId,
  });

  const isLoading = workloadLoading || handoverLoading;

  log.debug('Rendering ResourcesTab', { logId, hasWorkload: !!workloadData, hasHandover: !!handoverData });

  if (isLoading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  }

  if (!logId) {
    return (
      <Card>
        <Text type="secondary">Select an event log to view resource analytics</Text>
      </Card>
    );
  }

  // Transform the data
  const resources: ResourceData[] = (workloadData?.resources ?? []).map(r => ({
    name: r.resource,
    caseCount: r.caseCount,
    eventCount: r.eventCount,
    avgDuration: r.avgDuration,
    workloadPercent: r.workloadPercent,
  }));

  const handovers: HandoverData[] = (handoverData?.edges ?? []).map(e => ({
    from: e.source,
    to: e.target,
    frequency: e.frequency,
  })).sort((a, b) => b.frequency - a.frequency);

  const uniqueResources = resources.length;
  const totalHandovers = handovers.reduce((sum, h) => sum + h.frequency, 0);
  const isBalanced = workloadData?.isBalanced ?? true;

  const resourceColumns = [
    {
      title: 'Resource',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <UserOutlined style={{ color: tokens.colors.primary[500] }} />
          <Text strong>{text}</Text>
        </Space>
      ),
    },
    {
      title: 'Cases',
      dataIndex: 'caseCount',
      key: 'caseCount',
      sorter: (a: ResourceData, b: ResourceData) => a.caseCount - b.caseCount,
      render: (val: number) => val.toLocaleString(),
    },
    {
      title: 'Events',
      dataIndex: 'eventCount',
      key: 'eventCount',
      sorter: (a: ResourceData, b: ResourceData) => a.eventCount - b.eventCount,
      render: (val: number) => val.toLocaleString(),
    },
    {
      title: 'Avg Duration',
      dataIndex: 'avgDuration',
      key: 'avgDuration',
      sorter: (a: ResourceData, b: ResourceData) => (a.avgDuration ?? 0) - (b.avgDuration ?? 0),
      render: (seconds: number | null) => 
        seconds != null ? formatDurationFromSeconds(seconds) : '—',
    },
    {
      title: 'Workload',
      dataIndex: 'workloadPercent',
      key: 'workloadPercent',
      sorter: (a: ResourceData, b: ResourceData) => a.workloadPercent - b.workloadPercent,
      render: (val: number) => (
        <Tooltip title={`${val.toFixed(1)}% of total workload`}>
          <Progress
            percent={Math.round(val)}
            size="small"
            strokeColor={val > 30 ? tokens.colors.warning[500] : tokens.colors.primary[500]}
            showInfo
            style={{ width: 100 }}
          />
        </Tooltip>
      ),
    },
  ];

  const handoverColumns = [
    {
      title: 'From',
      dataIndex: 'from',
      key: 'from',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: '',
      key: 'arrow',
      width: 50,
      render: () => <SwapOutlined style={{ color: tokens.colors.neutral[400] }} />,
    },
    {
      title: 'To',
      dataIndex: 'to',
      key: 'to',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Frequency',
      dataIndex: 'frequency',
      key: 'frequency',
      sorter: (a: HandoverData, b: HandoverData) => a.frequency - b.frequency,
      defaultSortOrder: 'descend' as const,
      render: (val: number) => (
        <Space>
          <Text strong>{val.toLocaleString()}</Text>
          <Progress
            percent={Math.round((val / (handovers[0]?.frequency ?? 1)) * 100)}
            size="small"
            strokeColor={tokens.colors.primary[500]}
            showInfo={false}
            style={{ width: 60 }}
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      {/* KPI Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Unique Resources"
            value={uniqueResources}
            status="default"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Total Handovers"
            value={totalHandovers.toLocaleString()}
            status={totalHandovers > 1000 ? 'warning' : 'default'}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Workload Balanced"
            value={isBalanced ? 'Yes' : 'No'}
            status={isBalanced ? 'success' : 'warning'}
          />
        </Col>
      </Row>

      <Row gutter={24}>
        {/* Resource Performance Table */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <TeamOutlined style={{ color: tokens.colors.primary[500] }} />
                <span>Resource Performance</span>
                <Tooltip title="Summary of processing metrics for each resource">
                  <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                </Tooltip>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            {resources.length > 0 ? (
              <Table
                dataSource={resources}
                columns={resourceColumns}
                rowKey="name"
                pagination={{ pageSize: 10 }}
                size="middle"
              />
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="No resource data available"
              />
            )}
          </Card>
        </Col>

        {/* Handover Analysis */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <SwapOutlined style={{ color: tokens.colors.warning[500] }} />
                <span>Top Handovers</span>
                <Tooltip title="Most frequent work handoffs between resources">
                  <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                </Tooltip>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            {handovers.length > 0 ? (
              <Table
                dataSource={handovers.slice(0, 10)}
                columns={handoverColumns}
                rowKey={(r) => `${r.from}-${r.to}`}
                pagination={false}
                size="small"
              />
            ) : (
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description="No handover data available"
              />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default ResourcesTab;
