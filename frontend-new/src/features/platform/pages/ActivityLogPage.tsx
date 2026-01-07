import { useState, useMemo, useEffect } from 'react';
import { Table, Select, Button, Space, Tag, Typography, Alert } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { PageHeader, tokens, toast, logAction } from '@lumina/design-system';
import { createLogger } from '../../../shared/lib/logger';
import { useQuery } from '@tanstack/react-query';
import { sdk } from '../../../api/sdk';

const log = createLogger('Activity');
const { Text } = Typography;

type ActionType = 'upload' | 'view' | 'settings' | 'login' | 'logout' | 'delete' | 'export' | 'create' | 'update' | 'analyze';

interface ActivityItem {
  id: string;
  action: ActionType;
  description: string;
  timestamp: Date;
}

const actionColors: Record<ActionType, string> = {
  upload: 'blue',
  view: 'green',
  settings: 'purple',
  login: 'cyan',
  logout: 'default',
  delete: 'red',
  export: 'orange',
  create: 'geekblue',
  update: 'gold',
  analyze: 'magenta',
};

const actionLabels: Record<ActionType, string> = {
  upload: 'Upload',
  view: 'View',
  settings: 'Settings',
  login: 'Login',
  logout: 'Logout',
  delete: 'Delete',
  export: 'Export',
  create: 'Create',
  update: 'Update',
  analyze: 'Analyze',
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

  // Fetch audit logs from backend
  const { data: auditData, isLoading, error } = useQuery({
    queryKey: ['audit', 'logs', dateRange],
    queryFn: async () => {
      // Calculate date range for query
      const endDate = new Date().toISOString();
      let startDate: string | undefined;
      if (dateRange !== 'all') {
        const days = parseInt(dateRange, 10);
        startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
      }
      return sdk.audit.list({ startDate, endDate, pageSize: 100 });
    },
    staleTime: 60 * 1000, // 1 minute
  });

  useEffect(() => {
    log.info('Activity log page viewed');
    logAction('ActivityLogPage', 'page_viewed', { dateRange, actionType });
  }, [dateRange, actionType]);

  // Transform API data or fall back to mock data
  const activities = useMemo((): ActivityItem[] => {
    // If we have data from the API, transform it
    if (auditData?.items && auditData.items.length > 0) {
      return auditData.items.map((item: { id: string; action_type?: string; description?: string; created_at?: string }) => ({
        id: item.id,
        action: (item.action_type?.toLowerCase() || 'view') as ActionType,
        description: item.description || 'Activity recorded',
        timestamp: new Date(item.created_at || Date.now()),
      }));
    }
    // Fall back to mock data (backend audit is a stub that returns empty)
    return mockActivities;
  }, [auditData]);

  const filteredActivities = useMemo(() => {
    let result = [...activities];

    // Filter by date range (client-side for mock data)
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
  }, [activities, dateRange, actionType]);

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

  // Show error state
  if (error) {
    log.error('Failed to load audit logs', { error: (error as Error).message });
  }

  return (
    <div>
      <PageHeader
        title="Activity Log"
        description="View your recent actions and activity history"
      />

      {/* Error alert */}
      {error && (
        <Alert
          type="warning"
          message="Unable to fetch activity logs from server"
          description="Showing cached demo data. Activity logging will be available in a future release."
          showIcon
          closable
          style={{ marginBottom: tokens.spacing[4] }}
        />
      )}

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
        loading={isLoading}
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
