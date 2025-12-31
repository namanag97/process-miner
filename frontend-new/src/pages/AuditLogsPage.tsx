import React, { useState, useMemo, useEffect } from 'react';
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
  DatePicker,
  Tooltip,
  Badge,
} from 'antd';
import {
  DownloadOutlined,
  SearchOutlined,
  InfoCircleOutlined,
  SettingOutlined,
  EyeOutlined,
  UserOutlined,
  ClockCircleOutlined,
  GlobalOutlined,
  FilterOutlined,
  ReloadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { PageHeader, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../utils/logger';
import dayjs from 'dayjs';

const log = createLogger('AuditLogs');
const { Text, Paragraph } = Typography;
const { RangePicker } = DatePicker;

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
  | 'PERMISSIONS_UPDATED';

type UserRole = 'ADMIN' | 'USER' | 'VIEWER';

interface AuditLogEntry {
  id: string;
  userId: string;
  userEmail: string;
  event: AuditEventType;
  userRole: UserRole;
  timestamp: Date;
  message: Record<string, unknown>;
  ipAddress?: string;
  changeDetails?: {
    before?: Record<string, unknown>;
    after?: Record<string, unknown>;
  };
}

// ============ MOCK DATA ============

const generateMockAuditLogs = (): AuditLogEntry[] => {
  const events: AuditEventType[] = [
    'FILE_UPLOADED',
    'PROCESS_VIEWED',
    'SETTINGS_UPDATED',
    'USER_LOGIN',
    'PROCESS_EXPORTED',
    'FILTER_APPLIED',
    'ANALYSIS_CREATED',
    'PERMISSIONS_UPDATED',
    'FILE_DELETED',
    'USER_LOGOUT',
  ];

  const users = [
    { id: '7abcf0f9-daec-42d1-82ed-c21af088171', email: 'naman.agarwal@example.com', role: 'ADMIN' as UserRole },
    { id: '8bcdf1a0-dbfd-43e2-93fe-d32bf199282', email: 'sarah.chen@example.com', role: 'USER' as UserRole },
    { id: '9cdeg2b1-ecge-44f3-a4gf-e43cg2aa393', email: 'mike.johnson@example.com', role: 'VIEWER' as UserRole },
  ];

  const ipAddresses = ['192.168.1.100', '10.0.0.55', '172.16.0.25', '203.0.113.45'];

  const logs: AuditLogEntry[] = [];

  for (let i = 0; i < 65; i++) {
    const user = users[Math.floor(Math.random() * users.length)];
    const event = events[Math.floor(Math.random() * events.length)];
    const daysAgo = Math.floor(Math.random() * 30);
    const hoursAgo = Math.floor(Math.random() * 24);
    const minutesAgo = Math.floor(Math.random() * 60);

    logs.push({
      id: `log-${i + 1}`,
      userId: user.id,
      userEmail: user.email,
      event,
      userRole: user.role,
      timestamp: new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000 - hoursAgo * 60 * 60 * 1000 - minutesAgo * 60 * 1000),
      ipAddress: ipAddresses[Math.floor(Math.random() * ipAddresses.length)],
      message: generateEventMessage(event),
      changeDetails: generateChangeDetails(event),
    });
  }

  return logs.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

function generateEventMessage(event: AuditEventType): Record<string, unknown> {
  switch (event) {
    case 'FILE_UPLOADED':
      return { fileName: 'Orders_Q4.csv', fileSize: '2.4MB', columns: 12 };
    case 'FILE_DELETED':
      return { fileName: 'old_data.csv', reason: 'User requested' };
    case 'PROCESS_VIEWED':
      return { processId: 'proc-123', processName: 'Order Processing', duration: '45s' };
    case 'PROCESS_EXPORTED':
      return { format: 'PNG', processName: 'Claims Workflow', resolution: '1920x1080' };
    case 'SETTINGS_UPDATED':
      return { section: 'notifications', field: 'emailAlerts' };
    case 'USER_LOGIN':
      return { method: 'password', browser: 'Chrome 120', os: 'macOS' };
    case 'USER_LOGOUT':
      return { sessionDuration: '2h 15m' };
    case 'FILTER_APPLIED':
      return { filterType: 'timeRange', from: '2024-01-01', to: '2024-12-31' };
    case 'ANALYSIS_CREATED':
      return { analysisType: 'variant', casesIncluded: 1250 };
    case 'PERMISSIONS_UPDATED':
      return { targetUser: 'viewer@example.com', newPermissions: ['VIEW', 'EXPORT'] };
    default:
      return {};
  }
}

function generateChangeDetails(event: AuditEventType): AuditLogEntry['changeDetails'] | undefined {
  if (event === 'SETTINGS_UPDATED') {
    return {
      before: { emailAlerts: false, frequency: 'daily' },
      after: { emailAlerts: true, frequency: 'immediate' },
    };
  }
  if (event === 'PERMISSIONS_UPDATED') {
    return {
      before: { permissions: ['VIEW'] },
      after: { permissions: ['VIEW', 'EXPORT', 'ANALYZE'] },
    };
  }
  return undefined;
}

const mockAuditLogs = generateMockAuditLogs();

// ============ CONSTANTS ============

const eventColors: Record<AuditEventType, string> = {
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
  { value: 'custom', label: 'Custom range' },
];

// ============ HELPERS ============

function formatTimestamp(date: Date): string {
  return dayjs(date).format('MM/DD/YY, h:mm:ss A [GMT]Z');
}

// ============ COMPONENTS ============

const DetailDrawer: React.FC<{
  entry: AuditLogEntry | null;
  open: boolean;
  onClose: () => void;
}> = ({ entry, open, onClose }) => {
  if (!entry) return null;

  return (
    <Drawer
      title="Change Details"
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
              <Tag color={eventColors[entry.event]}>{entry.event}</Tag>
            </Col>
            <Col span={8}>
              <Text type="secondary">User</Text>
            </Col>
            <Col span={16}>
              <Text copyable>{entry.userEmail}</Text>
            </Col>
            <Col span={8}>
              <Text type="secondary">Role</Text>
            </Col>
            <Col span={16}>
              <Tag color={roleColors[entry.userRole]}>{entry.userRole}</Tag>
            </Col>
            <Col span={8}>
              <Text type="secondary">Time</Text>
            </Col>
            <Col span={16}>
              <Text>{formatTimestamp(entry.timestamp)}</Text>
            </Col>
            {entry.ipAddress && (
              <>
                <Col span={8}>
                  <Text type="secondary">IP Address</Text>
                </Col>
                <Col span={16}>
                  <Text code>{entry.ipAddress}</Text>
                </Col>
              </>
            )}
          </Row>
        </Card>

        <Card size="small" title="Event Message">
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
            {JSON.stringify(entry.message, null, 2)}
          </pre>
        </Card>

        {entry.changeDetails && (
          <Card size="small" title="Changes">
            <Row gutter={16}>
              <Col span={12}>
                <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                  Before
                </Text>
                <pre
                  style={{
                    backgroundColor: tokens.colors.error[50],
                    padding: tokens.spacing[2],
                    borderRadius: tokens.radius.sm,
                    fontSize: tokens.fontSize.xs,
                    margin: 0,
                  }}
                >
                  {JSON.stringify(entry.changeDetails.before, null, 2)}
                </pre>
              </Col>
              <Col span={12}>
                <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                  After
                </Text>
                <pre
                  style={{
                    backgroundColor: tokens.colors.success[50],
                    padding: tokens.spacing[2],
                    borderRadius: tokens.radius.sm,
                    fontSize: tokens.fontSize.xs,
                    margin: 0,
                  }}
                >
                  {JSON.stringify(entry.changeDetails.after, null, 2)}
                </pre>
              </Col>
            </Row>
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

  useEffect(() => {
    log.info('Audit logs page viewed');
  }, []);

  const filteredLogs = useMemo(() => {
    let result = [...mockAuditLogs];

    // Filter by date period
    if (datePeriod !== 'all' && datePeriod !== 'custom') {
      const days = parseInt(datePeriod, 10);
      const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      result = result.filter((entry) => entry.timestamp >= cutoff);
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (entry) =>
          entry.userEmail.toLowerCase().includes(query) ||
          entry.event.toLowerCase().includes(query) ||
          entry.userId.toLowerCase().includes(query) ||
          JSON.stringify(entry.message).toLowerCase().includes(query)
      );
    }

    return result;
  }, [datePeriod, searchQuery]);

  const handleExport = () => {
    log.info('Export audit logs requested');
    toast.success('Audit logs exported successfully');
  };

  const handleRefresh = () => {
    log.info('Refresh audit logs');
    toast.info('Audit logs refreshed');
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
        <Space direction="vertical" size={0}>
          <Text
            copyable={{ tooltips: ['Copy ID', 'Copied!'] }}
            style={{ fontSize: tokens.fontSize.xs, fontFamily: 'monospace' }}
          >
            {record.userId.substring(0, 20)}...
          </Text>
          <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
            ({record.userEmail})
          </Text>
        </Space>
      ),
    },
    {
      title: 'Event',
      dataIndex: 'event',
      key: 'event',
      width: 180,
      render: (event: AuditEventType) => (
        <Tag color={eventColors[event]} style={{ fontFamily: 'monospace', fontSize: 11 }}>
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
      title: 'User Role',
      dataIndex: 'userRole',
      key: 'userRole',
      width: 100,
      render: (role: UserRole) => <Tag color={roleColors[role]}>{role}</Tag>,
      filters: Object.keys(roleColors).map((role) => ({
        text: role,
        value: role,
      })),
      onFilter: (value, record) => record.userRole === value,
    },
    {
      title: 'Date',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (timestamp: Date) => (
        <Space>
          <ClockCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
          <Text style={{ fontSize: tokens.fontSize.sm }}>{formatTimestamp(timestamp)}</Text>
        </Space>
      ),
      sorter: (a, b) => a.timestamp.getTime() - b.timestamp.getTime(),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Message',
      dataIndex: 'message',
      key: 'message',
      ellipsis: true,
      render: (message: Record<string, unknown>) => (
        <Tooltip title={JSON.stringify(message, null, 2)}>
          <Text
            style={{
              fontFamily: 'monospace',
              fontSize: tokens.fontSize.xs,
              color: tokens.colors.neutral[600],
            }}
          >
            {JSON.stringify(message).substring(0, 60)}
            {JSON.stringify(message).length > 60 ? '...' : ''}
          </Text>
        </Tooltip>
      ),
    },
    ...(showIpColumn
      ? [
          {
            title: (
              <Space>
                <GlobalOutlined />
                IP Address
              </Space>
            ),
            dataIndex: 'ipAddress',
            key: 'ipAddress',
            width: 130,
            render: (ip: string) => <Text code>{ip || '-'}</Text>,
          } as ColumnsType<AuditLogEntry>[0],
        ]
      : []),
    {
      title: 'Change Details',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          icon={<EyeOutlined />}
          onClick={() => handleViewDetails(record)}
          disabled={!record.changeDetails}
        >
          {record.changeDetails ? 'See Details' : '-'}
        </Button>
      ),
    },
  ];

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
              {mockAuditLogs.length}
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
                  placeholder="Search by user, event, or message..."
                  prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  allowClear
                  style={{ maxWidth: 400 }}
                />
              </Col>
              <Col>
                <Space>
                  <Tooltip title="Show IP Address column">
                    <Button
                      icon={<GlobalOutlined />}
                      type={showIpColumn ? 'primary' : 'default'}
                      onClick={() => setShowIpColumn(!showIpColumn)}
                    />
                  </Tooltip>
                  <Tooltip title="Refresh">
                    <Button icon={<ReloadOutlined />} onClick={handleRefresh} />
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
        type="warning"
        icon={<InfoCircleOutlined />}
        message="Only the last 500 entries will be shown in the list view and search. You can download configuration events for a selected period by clicking download."
        style={{ marginBottom: tokens.spacing[4] }}
        showIcon
      />

      {/* Data Table */}
      <Card bodyStyle={{ padding: 0 }}>
        <Table
          dataSource={filteredLogs}
          columns={columns}
          rowKey="id"
          size="middle"
          scroll={{ x: 1200 }}
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
