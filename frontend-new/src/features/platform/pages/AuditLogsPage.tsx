import React, { useState, useMemo } from 'react';
import {
  Table,
  Select,
  Button,
  Space,
  Tag,
  Typography,
  Input,
  Card,
  Switch,
  Row,
  Col,
  Drawer,
  Alert,
  Tooltip,
} from 'antd';
import {
  DownloadOutlined,
  SearchOutlined,
  InfoCircleOutlined,
  SettingOutlined,
  EyeOutlined,
  ClockCircleOutlined,
  FilterOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  PageHeader,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  toast,
  useAuditLogs,
  type AuditLogEntry,
} from '@lumina/design-system';
import dayjs from 'dayjs';

const { Text } = Typography;

// ============ TYPES ============

type AuditEventType =
  | 'FILE_UPLOADED'
  | 'FILE_DELETED'
  | 'PROCESS_VIEWED'
  | 'PROCESS_EXPORTED'
  | 'SETTINGS_UPDATED'
  | 'USER_LOGIN'
  | 'USER_LOGOUT'
  | 'FILTER_APPLIED'
  | 'ANALYSIS_CREATED'
  | 'PERMISSIONS_UPDATED'
  | 'project.created'
  | 'project.deleted'
  | 'process.uploaded'
  | 'process.deleted'
  | 'explorer.viewed'
  | 'kpi.viewed';

type UserRole = 'ADMIN' | 'USER' | 'VIEWER';

// ============ CONSTANTS ============

const eventColors: Record<string, string> = {
  FILE_UPLOADED: 'blue',
  FILE_DELETED: 'red',
  PROCESS_VIEWED: 'green',
  PROCESS_EXPORTED: 'orange',
  SETTINGS_UPDATED: 'purple',
  USER_LOGIN: 'cyan',
  USER_LOGOUT: 'default',
  FILTER_APPLIED: 'geekblue',
  ANALYSIS_CREATED: 'magenta',
  PERMISSIONS_UPDATED: 'gold',
  'project.created': 'green',
  'project.deleted': 'red',
  'process.uploaded': 'blue',
  'process.deleted': 'red',
  'explorer.viewed': 'cyan',
  'kpi.viewed': 'purple',
};

const roleColors: Record<UserRole, string> = {
  ADMIN: 'red',
  USER: 'blue',
  VIEWER: 'default',
};

const retentionOptions = [
  { value: 'no-deletion', label: 'No deletion' },
  { value: '30', label: '30 days' },
  { value: '60', label: '60 days' },
  { value: '90', label: '90 days' },
];

const periodOptions = [
  { value: '7', label: 'Last 7 days' },
  { value: '30', label: 'Last 30 days' },
  { value: '90', label: 'Last 90 days' },
  { value: 'all', label: 'All time' },
];

// ============ HELPERS ============

function formatTimestamp(date: Date | string): string {
  return dayjs(date).format('MM/DD/YY, h:mm:ss A [GMT]Z');
}

// ============ COMPONENTS ============

interface DetailDrawerProps {
  entry: AuditLogEntry | null;
  open: boolean;
  onClose: () => void;
}

const DetailDrawer: React.FC<DetailDrawerProps> = ({ entry, open, onClose }) => {
  if (!entry) return null;

  return (
    <Drawer
      title="Event Details"
      placement="right"
      onClose={onClose}
      open={open}
      width={480}
    >
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        <Card size="small" title="Event Information">
          <Row gutter={[16, 12]}>
            <Col span={8}>
              <Text type="secondary">Event</Text>
            </Col>
            <Col span={16}>
              <Tag color={eventColors[entry.event] || 'default'}>{entry.event}</Tag>
            </Col>
            <Col span={8}>
              <Text type="secondary">User</Text>
            </Col>
            <Col span={16}>
              <Text copyable>{entry.userId}</Text>
            </Col>
            <Col span={8}>
              <Text type="secondary">Time</Text>
            </Col>
            <Col span={16}>
              <Text>{formatTimestamp(entry.timestamp)}</Text>
            </Col>
          </Row>
        </Card>

        {entry.data && Object.keys(entry.data).length > 0 && (
          <Card size="small" title="Event Data">
            <pre
              style={{
                backgroundColor: tokens.colors.neutral[50],
                padding: tokens.spacing[3],
                borderRadius: tokens.radius.md,
                fontSize: tokens.fontSize.sm,
                overflow: 'auto',
                margin: 0,
              }}
            >
              {JSON.stringify(entry.data, null, 2)}
            </pre>
          </Card>
        )}
      </Space>
    </Drawer>
  );
};

// ============ MAIN COMPONENT ============

export function AuditLogsPage() {
  const [ipTrackingEnabled, setIpTrackingEnabled] = useState(false);
  const [retentionPeriod, setRetentionPeriod] = useState('no-deletion');
  const [datePeriod, setDatePeriod] = useState('30');
  const [searchQuery, setSearchQuery] = useState('');
  const [showIpColumn, setShowIpColumn] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<AuditLogEntry | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Calculate date filter
  const dateFilter = useMemo(() => {
    if (datePeriod === 'all') return undefined;
    const days = parseInt(datePeriod, 10);
    const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
    return { startDate: startDate.toISOString() };
  }, [datePeriod]);

  // Fetch audit logs from API
  const { data: auditData, isLoading, error, refetch } = useAuditLogs(dateFilter);

  const logs = auditData?.items ?? [];

  const filteredLogs = useMemo(() => {
    if (!searchQuery) return logs;
    const query = searchQuery.toLowerCase();
    return logs.filter(
      (entry: AuditLogEntry) =>
        entry.userId.toLowerCase().includes(query) ||
        entry.event.toLowerCase().includes(query) ||
        JSON.stringify(entry.data).toLowerCase().includes(query)
    );
  }, [logs, searchQuery]);

  const handleExport = () => {
    const csvContent = [
      ['ID', 'User ID', 'Event', 'Timestamp', 'Data'].join(','),
      ...filteredLogs.map((log: AuditLogEntry) =>
        [
          log.id,
          log.userId,
          log.event,
          log.timestamp,
          JSON.stringify(log.data).replace(/,/g, ';'),
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success('Audit logs exported successfully');
  };

  const handleViewDetails = (entry: AuditLogEntry) => {
    setSelectedEntry(entry);
    setDrawerOpen(true);
  };

  const columns: ColumnsType<AuditLogEntry> = [
    {
      title: 'User ID',
      key: 'user',
      width: 220,
      render: (_, record) => (
        <Text
          copyable={{ tooltips: ['Copy ID', 'Copied!'] }}
          style={{ fontSize: tokens.fontSize.xs, fontFamily: 'monospace' }}
        >
          {record.userId.substring(0, 24)}...
        </Text>
      ),
    },
    {
      title: 'Event',
      dataIndex: 'event',
      key: 'event',
      width: 180,
      render: (event: string) => (
        <Tag color={eventColors[event] || 'default'} style={{ fontFamily: 'monospace', fontSize: 11 }}>
          {event}
        </Tag>
      ),
      filters: Object.keys(eventColors).map((event) => ({
        text: event,
        value: event,
      })),
      onFilter: (value, record) => record.event === value,
    },
    {
      title: 'Date',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 200,
      render: (timestamp: string) => (
        <Space>
          <ClockCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
          <Text style={{ fontSize: tokens.fontSize.sm }}>{formatTimestamp(timestamp)}</Text>
        </Space>
      ),
      sorter: (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Data',
      dataIndex: 'data',
      key: 'data',
      ellipsis: true,
      render: (data: Record<string, unknown>) => (
        <Tooltip title={JSON.stringify(data, null, 2)}>
          <Text
            style={{
              fontFamily: 'monospace',
              fontSize: tokens.fontSize.xs,
              color: tokens.colors.neutral[600],
            }}
          >
            {JSON.stringify(data).substring(0, 60)}
            {JSON.stringify(data).length > 60 ? '...' : ''}
          </Text>
        </Tooltip>
      ),
    },
    {
      title: 'Details',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
        >
          View
        </Button>
      ),
    },
  ];

  if (error) {
    return (
      <div>
        <PageHeader
          title="Audit Logs"
          description="Track and monitor all user activities and system changes"
        />
        <QueryError error={error} onRetry={() => refetch()} variant="card" />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Audit Logs"
        description="Track and monitor all user activities and system changes"
        actions={
          <Space>
            <Switch
              checked={ipTrackingEnabled}
              onChange={setIpTrackingEnabled}
              checkedChildren="IP Tracking ON"
              unCheckedChildren="IP Tracking OFF"
            />
            <Select
              value={retentionPeriod}
              onChange={setRetentionPeriod}
              options={retentionOptions}
              style={{ width: 130 }}
              prefix={<SettingOutlined />}
            />
          </Space>
        }
      />

      {/* Summary and Filters Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[4] }}>
        <Col>
          <Card
            size="small"
            style={{
              background: `linear-gradient(135deg, ${tokens.colors.primary[50]} 0%, ${tokens.colors.neutral[0]} 100%)`,
              border: `1px solid ${tokens.colors.primary[100]}`,
            }}
            bodyStyle={{ padding: tokens.spacing[4] }}
          >
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block' }}>
              Total count of Audit Logs
            </Text>
            <Text strong style={{ fontSize: tokens.fontSize['2xl'], color: tokens.colors.primary[600] }}>
              {logs.length}
            </Text>
          </Card>
        </Col>
        <Col flex="auto">
          <Card size="small" bodyStyle={{ padding: tokens.spacing[3] }}>
            <Row gutter={16} align="middle">
              <Col>
                <Space>
                  <FilterOutlined style={{ color: tokens.colors.neutral[400] }} />
                  <Select
                    value={datePeriod}
                    onChange={setDatePeriod}
                    options={periodOptions}
                    style={{ width: 150 }}
                    placeholder="Define Period"
                  />
                </Space>
              </Col>
              <Col flex="auto">
                <Input
                  placeholder="Search by user, event, or data..."
                  prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  allowClear
                  style={{ maxWidth: 400 }}
                />
              </Col>
              <Col>
                <Space>
                  <Tooltip title="Refresh">
                    <Button icon={<ReloadOutlined />} onClick={() => refetch()} loading={isLoading} />
                  </Tooltip>
                  <Button type="primary" icon={<DownloadOutlined />} onClick={handleExport}>
                    Download
                  </Button>
                </Space>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* Info Alert */}
      <Alert
        type="info"
        icon={<InfoCircleOutlined />}
        message="Audit logs are fetched from the server. You can filter by date range and search across all fields."
        style={{ marginBottom: tokens.spacing[4] }}
        showIcon
      />

      {/* Data Table */}
      <Card bodyStyle={{ padding: 0 }}>
        {isLoading ? (
          <div style={{ padding: tokens.spacing[6] }}>
            <LoadingState type="skeleton" rows={5} />
          </div>
        ) : logs.length === 0 ? (
          <div style={{ padding: tokens.spacing[6] }}>
            <EmptyState
              title="No audit logs found"
              description="No events have been logged yet. Actions in the app will be recorded here."
            />
          </div>
        ) : (
          <Table
            dataSource={filteredLogs}
            columns={columns}
            rowKey="id"
            size="middle"
            scroll={{ x: 1000 }}
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50'],
              showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} entries`,
              showQuickJumper: true,
            }}
            locale={{
              emptyText: 'No audit logs found for the selected filters',
            }}
          />
        )}
      </Card>

      {/* Detail Drawer */}
      <DetailDrawer
        entry={selectedEntry}
        open={drawerOpen}
        onClose={() => {
          setDrawerOpen(false);
          setSelectedEntry(null);
        }}
      />
    </div>
  );
}

export default AuditLogsPage;
