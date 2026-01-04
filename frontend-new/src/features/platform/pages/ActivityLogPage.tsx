import { useState, useMemo, useEffect } from 'react';
import { Table, Select, Button, Space, Tag, Typography } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { PageHeader, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const log = createLogger('Activity');
const { Text } = Typography;

interface ActivityItem {
  id: string;
  action: 'upload' | 'view' | 'settings' | 'login' | 'logout' | 'delete' | 'export';
  description: string;
  timestamp: Date;
}

const actionColors: Record<ActivityItem['action'], string> = {
  upload: 'blue',
  view: 'green',
  settings: 'purple',
  login: 'cyan',
  logout: 'default',
  delete: 'red',
  export: 'orange',
};

const actionLabels: Record<ActivityItem['action'], string> = {
  upload: 'Upload',
  view: 'View',
  settings: 'Settings',
  login: 'Login',
  logout: 'Logout',
  delete: 'Delete',
  export: 'Export',
};

// Mock activity data
const mockActivities: ActivityItem[] = [
  { id: '1', action: 'upload', description: 'Uploaded Orders.csv', timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000) },
  { id: '2', action: 'view', description: 'Viewed process map for Claims_Process', timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000) },
  { id: '3', action: 'settings', description: 'Updated profile settings', timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000) },
  { id: '4', action: 'export', description: 'Exported process map as SVG', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000) },
  { id: '5', action: 'login', description: 'Signed in from new device', timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000) },
  { id: '6', action: 'upload', description: 'Uploaded Purchase_Orders.csv', timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000) },
  { id: '7', action: 'view', description: 'Viewed variant analysis', timestamp: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000) },
  { id: '8', action: 'delete', description: 'Deleted old_data.csv', timestamp: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000) },
  { id: '9', action: 'settings', description: 'Changed notification preferences', timestamp: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000) },
  { id: '10', action: 'login', description: 'Signed in', timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) },
  { id: '11', action: 'upload', description: 'Uploaded Support_Tickets.xes', timestamp: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000) },
  { id: '12', action: 'view', description: 'Viewed performance dashboard', timestamp: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000) },
];

const dateRangeOptions = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: 'all', label: 'All time' },
];

const actionTypeOptions = [
  { value: 'all', label: 'All actions' },
  { value: 'upload', label: 'Upload' },
  { value: 'view', label: 'View' },
  { value: 'settings', label: 'Settings' },
  { value: 'login', label: 'Login' },
  { value: 'delete', label: 'Delete' },
  { value: 'export', label: 'Export' },
];

function formatRelativeTime(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  if (diffHours < 24) return `${diffHours} hours ago`;
  if (diffDays < 7) return `${diffDays} days ago`;
  return date.toLocaleDateString();
}

export function ActivityLogPage() {
  const [dateRange, setDateRange] = useState('7');
  const [actionType, setActionType] = useState('all');

  useEffect(() => {
    log.info('Activity log page viewed');
  }, []);

  const filteredActivities = useMemo(() => {
    let result = [...mockActivities];

    // Filter by date range
    if (dateRange !== 'all') {
      const days = parseInt(dateRange, 10);
      const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      result = result.filter((a) => a.timestamp >= cutoff);
    }

    // Filter by action type
    if (actionType !== 'all') {
      result = result.filter((a) => a.action === actionType);
    }

    return result;
  }, [dateRange, actionType]);

  const handleExport = () => {
    log.info('Export requested');
    toast.info('Export functionality coming soon');
  };

  const handleDateRangeChange = (value: string) => {
    log.debug('Date range filter changed', { value });
    setDateRange(value);
  };

  const handleActionTypeChange = (value: string) => {
    log.debug('Action type filter changed', { value });
    setActionType(value);
  };

  const columns: ColumnsType<ActivityItem> = [
    {
      title: 'Action',
      dataIndex: 'action',
      key: 'action',
      width: 120,
      render: (action: ActivityItem['action']) => (
        <Tag color={actionColors[action]}>{actionLabels[action]}</Tag>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Date',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 150,
      render: (timestamp: Date) => (
        <Text type="secondary">{formatRelativeTime(timestamp)}</Text>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Activity Log"
        description="View your recent actions and activity history"
      />

      {/* Filters */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing[4],
          padding: tokens.spacing[4],
          backgroundColor: tokens.colors.neutral[50],
          borderRadius: tokens.radius.md,
        }}
      >
        <Space>
          <Select
            value={dateRange}
            onChange={handleDateRangeChange}
            options={dateRangeOptions}
            style={{ width: 150 }}
          />
          <Select
            value={actionType}
            onChange={handleActionTypeChange}
            options={actionTypeOptions}
            style={{ width: 150 }}
          />
        </Space>
        <Button icon={<DownloadOutlined />} onClick={handleExport}>
          Export
        </Button>
      </div>

      {/* Table */}
      <Table
        dataSource={filteredActivities}
        columns={columns}
        rowKey="id"
        pagination={{
          pageSize: 10,
          showSizeChanger: false,
          showTotal: (total) => `${total} activities`,
        }}
        locale={{
          emptyText: 'No activity found for the selected filters',
        }}
      />
    </div>
  );
}

export default ActivityLogPage;
