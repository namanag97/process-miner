import React, { useState, useMemo } from 'react';
import {
  Table,
  Input,
  Button,
  Space,
  Modal,
  Dropdown,
  Typography,
  Tag,
} from 'antd';
import type { TableProps, MenuProps } from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  EyeOutlined,
  DownloadOutlined,
  DeleteOutlined,
  MoreOutlined,
  FileOutlined,
  FolderOpenOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, EmptyState, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('EventLogsPage');
const { Text } = Typography;

// Mock data - in a real app this comes from SDK
const mockEventLogs = [
  {
    id: '1',
    name: 'Orders_2024.csv',
    totalCases: 1250,
    totalEvents: 45000,
    createdAt: '2024-12-28T10:30:00Z',
    sourceFile: 'Orders_2024.csv',
  },
  {
    id: '2',
    name: 'Claims_Process.xes',
    totalCases: 890,
    totalEvents: 23400,
    createdAt: '2024-12-27T14:15:00Z',
    sourceFile: 'Claims_Process.xes',
  },
  {
    id: '3',
    name: 'Purchase_Orders.csv',
    totalCases: 3200,
    totalEvents: 98000,
    createdAt: '2024-12-25T09:00:00Z',
    sourceFile: 'Purchase_Orders.csv',
  },
  {
    id: '4',
    name: 'Support_Tickets.csv',
    totalCases: 560,
    totalEvents: 8900,
    createdAt: '2024-12-20T16:45:00Z',
    sourceFile: 'Support_Tickets.csv',
  },
];

interface EventLog {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  createdAt: string;
  sourceFile?: string;
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays === 1) return 'Yesterday';
  return `${diffDays} days ago`;
}

export function EventLogsPage() {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [logToDelete, setLogToDelete] = useState<EventLog | null>(null);
  const [logs, setLogs] = useState<EventLog[]>(mockEventLogs);

  log.debug('Rendering EventLogsPage', { logCount: logs.length });

  // Filter logs based on search
  const filteredLogs = useMemo(() => {
    if (!searchText) return logs;
    const lower = searchText.toLowerCase();
    return logs.filter((log) => log.name.toLowerCase().includes(lower));
  }, [logs, searchText]);

  const handleSearch = (value: string) => {
    log.debug('Searching logs', { query: value });
    setSearchText(value);
  };

  const handleView = (record: EventLog) => {
    log.info('Viewing log', { logId: record.id, name: record.name });
    navigate(`/logs/${record.id}`);
  };

  const handleDownload = (record: EventLog) => {
    log.info('Downloading log', { logId: record.id, name: record.name });
    toast.info('Download feature coming soon');
  };

  const handleDeleteClick = (record: EventLog) => {
    log.debug('Delete requested', { logId: record.id, name: record.name });
    setLogToDelete(record);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (logToDelete) {
      log.info('Deleting log', { logId: logToDelete.id, name: logToDelete.name });
      setLogs((prev) => prev.filter((l) => l.id !== logToDelete.id));
      toast.success(`"${logToDelete.name}" has been deleted`);
      setDeleteModalOpen(false);
      setLogToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    log.debug('Delete cancelled');
    setDeleteModalOpen(false);
    setLogToDelete(null);
  };

  const getRowActions = (record: EventLog): MenuProps['items'] => [
    {
      key: 'view',
      icon: <EyeOutlined />,
      label: 'View',
      onClick: () => handleView(record),
    },
    {
      key: 'download',
      icon: <DownloadOutlined />,
      label: 'Download',
      onClick: () => handleDownload(record),
    },
    {
      type: 'divider',
    },
    {
      key: 'delete',
      icon: <DeleteOutlined />,
      label: 'Delete',
      danger: true,
      onClick: () => handleDeleteClick(record),
    },
  ];

  const columns: TableProps<EventLog>['columns'] = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
      render: (name: string, record) => (
        <Space>
          <FileOutlined style={{ color: tokens.colors.primary[500] }} />
          <Text strong style={{ cursor: 'pointer' }} onClick={() => handleView(record)}>
            {name}
          </Text>
        </Space>
      ),
    },
    {
      title: 'Cases',
      dataIndex: 'totalCases',
      key: 'totalCases',
      sorter: (a, b) => a.totalCases - b.totalCases,
      render: (cases: number) => (
        <Tag color="blue">{cases.toLocaleString()}</Tag>
      ),
      width: 120,
    },
    {
      title: 'Events',
      dataIndex: 'totalEvents',
      key: 'totalEvents',
      sorter: (a, b) => a.totalEvents - b.totalEvents,
      render: (events: number) => (
        <Text>{events.toLocaleString()}</Text>
      ),
      width: 120,
    },
    {
      title: 'Uploaded',
      dataIndex: 'createdAt',
      key: 'createdAt',
      sorter: (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(),
      render: (date: string) => (
        <Text type="secondary">{formatRelativeTime(date)}</Text>
      ),
      width: 150,
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      render: (_, record) => (
        <Dropdown menu={{ items: getRowActions(record) }} trigger={['click']}>
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Event Logs"
        description="Manage your uploaded event log files"
        actions={
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => {
              log.info('Navigating to upload');
              navigate('/logs/upload');
            }}
          >
            Upload File
          </Button>
        }
      />

      {logs.length > 0 ? (
        <>
          {/* Search Bar */}
          <div style={{ marginBottom: tokens.spacing[4] }}>
            <Input
              placeholder="Search event logs..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => handleSearch(e.target.value)}
              allowClear
              style={{ maxWidth: 320 }}
            />
          </div>

          {/* Table */}
          <Table
            columns={columns}
            dataSource={filteredLogs}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: true,
              showTotal: (total, range) =>
                `${range[0]}-${range[1]} of ${total} logs`,
            }}
            onRow={(record) => ({
              style: { cursor: 'pointer' },
              onClick: () => handleView(record),
            })}
          />
        </>
      ) : (
        <EmptyState
          icon={<FolderOpenOutlined />}
          title="No event logs yet"
          description="Upload your first event log file to start analyzing your process"
          actionLabel="Upload File"
          onAction={() => navigate('/logs/upload')}
        />
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        title="Delete Event Log"
        open={deleteModalOpen}
        onOk={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        okText="Delete"
        okButtonProps={{ danger: true }}
        cancelText="Cancel"
      >
        <p>
          Are you sure you want to delete <strong>"{logToDelete?.name}"</strong>?
        </p>
        <p style={{ color: tokens.colors.neutral[500] }}>
          This action cannot be undone. The event log and all associated data will be permanently deleted.
        </p>
      </Modal>
    </div>
  );
}

export default EventLogsPage;
