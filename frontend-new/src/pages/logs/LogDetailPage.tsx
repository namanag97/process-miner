import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Tabs,
  Card,
  Row,
  Col,
  Table,
  Button,
  Dropdown,
  Descriptions,
  Space,
  Tag,
  Spin,
  Alert,
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
import { PageHeader, MetricCard, tokens, toast, useProcess, useProcessStatistics, useDeleteProcess, formatDurationFromSeconds } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('LogDetailPage');

export function LogDetailPage() {
  const navigate = useNavigate();
  const { id: logId } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch log details via standardized hook
  const { data: logDetail, isLoading, error } = useProcess(logId || '');

  // Fetch log statistics via standardized hook
  const { data: stats } = useProcessStatistics(logId || '');

  // Delete mutation via standardized hook
  const deleteMutation = useDeleteProcess();

  log.debug('Rendering LogDetailPage', { logId, activeTab });

  const handleExport = () => {
    log.info('Exporting log', { logId });
    toast.info('Export feature coming soon');
  };

  const handleDelete = () => {
    if (logId) {
      log.info('Deleting log', { logId });
      deleteMutation.mutate(logId, {
        onSuccess: () => {
          navigate('/processes');
        }
      });
    }
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

  // Error state
  if (error) {
    return (
      <div>
        <PageHeader
          title="Event Log"
          breadcrumb={[{ label: 'Event Logs', href: '/processes' }, { label: 'Error' }]}
        />
        <Alert
          message="Failed to load event log"
          description={(error as Error).message}
          type="error"
          showIcon
        />
      </div>
    );
  }

  // Loading state
  if (isLoading || !logDetail) {
    return (
      <div>
        <PageHeader
          title="Loading..."
          breadcrumb={[{ label: 'Event Logs', href: '/processes' }, { label: 'Loading' }]}
        />
        <div style={{ display: 'flex', justifyContent: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      </div>
    );
  }

  // Get statistics from response
  const statistics = (stats || logDetail.statistics || {}) as Record<string, unknown>;
  const totalVariants = (statistics.total_variants ?? statistics.totalVariants ?? 0) as number;
  const avgCaseDuration = (statistics.avg_case_duration_seconds ?? statistics.avgCaseDurationSeconds) as number | undefined;
  const dateRange = statistics.date_range as { start?: string; end?: string } | undefined;

  // Overview Tab
  const OverviewTab = () => (
    <div>
      {/* Key Metrics */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Total Cases"
            value={logDetail.totalCases.toLocaleString()}
            status="default"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Total Events"
            value={logDetail.totalEvents.toLocaleString()}
            status="default"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Unique Activities"
            value={logDetail.totalActivities ?? logDetail.activities?.length ?? 0}
            status="success"
          />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <MetricCard
            title="Process Variants"
            value={totalVariants}
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
              {logDetail.sourceFile ?? 'N/A'}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Uploaded">
            {new Date(logDetail.createdAt).toLocaleDateString()}
          </Descriptions.Item>
          <Descriptions.Item label="Date Range">
            <Space>
              <CalendarOutlined />
              {dateRange?.start && dateRange?.end
                ? `${dateRange.start} to ${dateRange.end}`
                : 'N/A'}
            </Space>
          </Descriptions.Item>
          <Descriptions.Item label="Avg. Case Duration">
            {avgCaseDuration
              ? formatDurationFromSeconds(avgCaseDuration)
              : 'N/A'}
          </Descriptions.Item>
          <Descriptions.Item label="Format">
            <Tag>{logDetail.sourceFormat?.toUpperCase() ?? 'N/A'}</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );

  // Statistics Tab
  const StatisticsTab = () => (
    <Row gutter={24}>
      <Col xs={24} lg={12}>
        <Card title="Activities" style={{ marginBottom: tokens.spacing[4] }}>
          <Table
            dataSource={(logDetail.activities || []).map((name, i) => ({ 
              name, 
              index: i + 1,
            }))}
            columns={[
              { title: '#', dataIndex: 'index', key: 'index', width: 50 },
              { title: 'Activity Name', dataIndex: 'name', key: 'name' },
            ]}
            rowKey="name"
            pagination={false}
            size="small"
          />
        </Card>
      </Col>
      <Col xs={24} lg={12}>
        <Card title="Quick Actions">
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button 
              block 
              icon={<SearchOutlined />}
              onClick={() => navigate(`/explorer/${logId}`)}
            >
              Open Process Explorer
            </Button>
            <Button 
              block 
              onClick={() => navigate(`/analytics?logId=${logId}`)}
            >
              View Analytics
            </Button>
          </Space>
        </Card>
      </Col>
    </Row>
  );

  const tabItems = [
    { key: 'overview', label: 'Overview', children: <OverviewTab /> },
    { key: 'statistics', label: 'Statistics', children: <StatisticsTab /> },
  ];

  return (
    <div>
      <PageHeader
        title={logDetail.name}
        description={`${logDetail.totalCases.toLocaleString()} cases • ${logDetail.totalEvents.toLocaleString()} events`}
        breadcrumb={[
          { label: 'Event Logs', href: '/processes' },
          { label: logDetail.name },
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
