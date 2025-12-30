import React, { useState, useMemo } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Table,
  Input,
  Button,
  Space,
  Modal,
  Dropdown,
  Typography,
  Tag,
  Spin,
  Alert,
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
import { PageHeader, EmptyState, tokens, toast, useSDK, type EventLog } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('EventLogsPage');
const { Text } = Typography;

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
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  const [searchText, setSearchText] = useState('');
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [logToDelete, setLogToDelete] = useState<EventLog | null>(null);

  // Fetch logs from API
  const { data, isLoading, error } = useQuery({
    queryKey: ['processes'],
    queryFn: () => sdk.processes.list({ pageSize: 100 }),
  });

  const logs = data?.items ?? [];

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => sdk.processes.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processes'] });
      toast.success(`"${logToDelete?.name}" has been deleted`);
      setDeleteModalOpen(false);
      setLogToDelete(null);
    },
    onError: (err) => {
      toast.error(`Failed to delete: ${(err as Error).message}`);
    },
  });

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
    navigate(`/processes/${record.id}`);
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
      deleteMutation.mutate(logToDelete.id);
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

  // Error state
  if (error) {
    return (
      <div>
        <PageHeader
          title="Event Logs"
          description="Manage your uploaded event log files"
        />
        <Alert
          message="Failed to load event logs"
          description={(error as Error).message}
          type="error"
          showIcon
        />
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div>
        <PageHeader
          title="Event Logs"
          description="Manage your uploaded event log files"
        />
        <div style={{ display: 'flex', justifyContent: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      </div>
    );
  }

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
              navigate('/processes/upload');
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
          onAction={() => navigate('/processes/upload')}
        />
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        title="Delete Event Log"
        open={deleteModalOpen}
        onOk={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        okText="Delete"
        okButtonProps={{ danger: true, loading: deleteMutation.isPending }}
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
