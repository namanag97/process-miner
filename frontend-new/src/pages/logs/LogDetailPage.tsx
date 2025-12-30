import React, { useState } from 'react';
import {
  Tabs,
  Card,
  Row,
  Col,
  Table,
  Button,
  Dropdown,
  Typography,
  Descriptions,
  Statistic,
  Space,
  Tag,
} from 'antd';
import type { MenuProps } from 'antd';
import {
  DownloadOutlined,
  DeleteOutlined,
  SearchOutlined,
  MoreOutlined,
  CalendarOutlined,
  FileOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader, MetricCard, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('LogDetailPage');
const { Text, Title } = Typography;

// Mock log data
const mockLogDetail = {
  id: '1',
  name: 'Orders_2024.csv',
  sourceFile: 'Orders_2024.csv',
  totalCases: 1250,
  totalEvents: 45000,
  uniqueActivities: 12,
  uniqueResources: 8,
  variantCount: 156,
  createdAt: '2024-12-28T10:30:00Z',
  dateRange: {
    start: '2024-01-01',
    end: '2024-12-15',
  },
  avgCaseDuration: '4.2 days',
};

// Mock sample data
const mockSampleData = [
  { case_id: 'C001', activity: 'Register Order', timestamp: '2024-01-15 09:00:00', resource: 'John' },
  { case_id: 'C001', activity: 'Check Inventory', timestamp: '2024-01-15 09:30:00', resource: 'Sarah' },
  { case_id: 'C001', activity: 'Prepare Shipment', timestamp: '2024-01-15 11:00:00', resource: 'Mike' },
  { case_id: 'C001', activity: 'Ship Order', timestamp: '2024-01-15 14:00:00', resource: 'Mike' },
  { case_id: 'C001', activity: 'Complete', timestamp: '2024-01-16 10:00:00', resource: 'System' },
  { case_id: 'C002', activity: 'Register Order', timestamp: '2024-01-15 10:00:00', resource: 'John' },
  { case_id: 'C002', activity: 'Check Inventory', timestamp: '2024-01-15 10:45:00', resource: 'Sarah' },
  { case_id: 'C002', activity: 'Back Order', timestamp: '2024-01-15 11:00:00', resource: 'Sarah' },
  { case_id: 'C002', activity: 'Notify Customer', timestamp: '2024-01-15 11:30:00', resource: 'Emma' },
  { case_id: 'C003', activity: 'Register Order', timestamp: '2024-01-15 11:00:00', resource: 'Lisa' },
];

// Mock statistics
const mockStatistics = {
  activities: [
    { name: 'Register Order', count: 1250, percent: 100 },
    { name: 'Check Inventory', count: 1248, percent: 99.8 },
    { name: 'Prepare Shipment', count: 1100, percent: 88 },
    { name: 'Ship Order', count: 1050, percent: 84 },
    { name: 'Complete', count: 980, percent: 78.4 },
    { name: 'Back Order', count: 150, percent: 12 },
    { name: 'Notify Customer', count: 150, percent: 12 },
    { name: 'Cancel Order', count: 45, percent: 3.6 },
  ],
  topVariants: [
    { path: 'Register → Check → Prepare → Ship → Complete', count: 680, percent: 54.4 },
    { path: 'Register → Check → Back Order → Notify → ...', count: 120, percent: 9.6 },
    { path: 'Register → Check → Prepare → Back Order → ...', count: 85, percent: 6.8 },
  ],
};

export function LogDetailPage() {
  const navigate = useNavigate();
  const { id: logId } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('overview');

  log.debug('Rendering LogDetailPage', { logId, activeTab });

  const handleExport = () => {
    log.info('Exporting log', { logId });
    toast.info('Export feature coming soon');
  };

  const handleDelete = () => {
    log.info('Deleting log', { logId });
    toast.success(`"${mockLogDetail.name}" has been deleted`);
    navigate('/logs');
  };

  const handleOpenExplorer = () => {
    log.info('Opening in Process Explorer', { logId });
    navigate(`/explorer/${logId}`);
  };

  const actionMenuItems: MenuProps['items'] = [
    {
      key: 'export',
      icon: <DownloadOutlined />,
      label: 'Export',
      onClick: handleExport,
    },
    {
      key: 'explorer',
      icon: <SearchOutlined />,
      label: 'Open in Explorer',
      onClick: handleOpenExplorer,
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: 'Delete',
      danger: true,
      onClick: handleDelete,
    },
  ];

  // Overview Tab
  const OverviewTab = () => (
    <div>
      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Total Cases"
            value={mockLogDetail.totalCases.toLocaleString()}
            status="default"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Total Events"
            value={mockLogDetail.totalEvents.toLocaleString()}
            status="default"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Unique Activities"
            value={mockLogDetail.uniqueActivities}
            status="success"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Process Variants"
            value={mockLogDetail.variantCount}
            status="default"
          />
        </Col>
      </Row>

      {/* Details Card */}
      <Card title="Log Details">
        <Descriptions column={{ xs: 1, sm: 2 }}>
          <Descriptions.Item label="Source File">
            <Space>
              <FileOutlined />
              {mockLogDetail.sourceFile}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Uploaded">
            {new Date(mockLogDetail.createdAt).toLocaleDateString()}
          </Descriptions.Item>
          <Descriptions.Item label="Date Range">
            <Space>
              <CalendarOutlined />
              {mockLogDetail.dateRange.start} to {mockLogDetail.dateRange.end}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Avg. Case Duration">
            {mockLogDetail.avgCaseDuration}
          </Descriptions.Item>
          <Descriptions.Item label="Unique Resources">
            {mockLogDetail.uniqueResources}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );

  // Preview Tab
  const PreviewTab = () => (
    <Card title="Sample Data (First 10 Events)">
      <Table
        dataSource={mockSampleData}
        columns={[
          { title: 'Case ID', dataIndex: 'case_id', key: 'case_id' },
          { title: 'Activity', dataIndex: 'activity', key: 'activity' },
          { title: 'Timestamp', dataIndex: 'timestamp', key: 'timestamp' },
          { title: 'Resource', dataIndex: 'resource', key: 'resource' },
        ]}
        rowKey={(_, index) => String(index)}
        pagination={false}
        size="middle"
      />
    </Card>
  );

  // Statistics Tab
  const StatisticsTab = () => (
    <Row gutter={24}>
      <Col xs={24} lg={12}>
        <Card title="Activity Frequency" style={{ marginBottom: tokens.spacing[4] }}>
          <Table
            dataSource={mockStatistics.activities}
            columns={[
              { title: 'Activity', dataIndex: 'name', key: 'name' },
              {
                title: 'Cases',
                dataIndex: 'count',
                key: 'count',
                render: (count: number) => count.toLocaleString(),
              },
              {
                title: '% of Cases',
                dataIndex: 'percent',
                key: 'percent',
                render: (percent: number) => (
                  <Tag color={percent > 50 ? 'green' : percent > 20 ? 'blue' : 'default'}>
                    {percent}%
                  </Tag>
                ),
              },
            ]}
            rowKey="name"
            pagination={false}
            size="small"
          />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Top Variants">
          <Table
            dataSource={mockStatistics.topVariants}
            columns={[
              {
                title: 'Path',
                dataIndex: 'path',
                key: 'path',
                render: (path: string) => (
                  <Text style={{ fontSize: 12 }}>{path}</Text>
                ),
              },
              {
                title: 'Cases',
                dataIndex: 'count',
                key: 'count',
                width: 80,
              },
              {
                title: '%',
                dataIndex: 'percent',
                key: 'percent',
                width: 60,
                render: (percent: number) => `${percent}%`,
              },
            ]}
            rowKey="path"
            pagination={false}
            size="small"
          />
          <Button
            type="link"
            style={{ marginTop: tokens.spacing[2], padding: 0 }}
            onClick={() => navigate(`/explorer/${logId}/variants`)}
          >
            View all {mockLogDetail.variantCount} variants →
          </Button>
        </Card>
      </Col>
    </Row>
  );

  const tabItems = [
    { key: 'overview', label: 'Overview', children: <OverviewTab /> },
    { key: 'preview', label: 'Preview', children: <PreviewTab /> },
    { key: 'statistics', label: 'Statistics', children: <StatisticsTab /> },
  ];

  return (
    <div>
      <PageHeader
        title={mockLogDetail.name}
        description={`${mockLogDetail.totalCases.toLocaleString()} cases • ${mockLogDetail.totalEvents.toLocaleString()} events`}
        breadcrumb={[
          { label: 'Event Logs', href: '/logs' },
          { label: mockLogDetail.name },
        ]}
        actions={
          <Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleOpenExplorer}
            >
              Explore Process
            </Button>
            <Dropdown menu={{ items: actionMenuItems }} trigger={['click']}>
              <Button icon={<MoreOutlined />} />
            </Dropdown>
          </Space>
        }
      />

      <Tabs
        activeKey={activeTab}
        onChange={(key) => {
          log.debug('Tab changed', { from: activeTab, to: key });
          setActiveTab(key);
        }}
        items={tabItems}
      />
    </div>
  );
}

export default LogDetailPage;
