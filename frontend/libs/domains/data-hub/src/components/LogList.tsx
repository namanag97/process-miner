import React, { useState } from 'react';
import { Table, Input, Button, Space, Tag, Dropdown, Modal, message } from 'antd';
import {
  SearchOutlined,
  MoreOutlined,
  PlayCircleOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useLogs, useDeleteLog } from '../hooks';
import type { EventLog } from 'process-mining-sdk';
import { formatCompactNumber, formatDuration } from '@lumina/design-system';

interface LogListProps {
  onLogSelect?: (logId: string) => void;
}

export const LogList: React.FC<LogListProps> = ({ onLogSelect }) => {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [logToDelete, setLogToDelete] = useState<EventLog | null>(null);

  const { data, isLoading, error } = useLogs({
    page,
    pageSize,
    search: search || undefined,
    sortBy: 'created_at',
    sortOrder: 'desc',
  });

  const deleteMutation = useDeleteLog();

  const handleDelete = async () => {
    if (!logToDelete) return;

    try {
      await deleteMutation.mutateAsync(logToDelete.id);
      message.success(`Log "${logToDelete.name}" deleted successfully`);
      setDeleteModalOpen(false);
      setLogToDelete(null);
    } catch (err) {
      message.error('Failed to delete log');
    }
  };

  const getActions = (record: EventLog) => [
    {
      key: 'view',
      label: 'View Details',
      icon: <EyeOutlined />,
      onClick: () => navigate(`/data/logs/${record.id}`),
    },
    {
      key: 'explore',
      label: 'Process Explorer',
      icon: <PlayCircleOutlined />,
      onClick: () => navigate(`/explorer/${record.id}`),
    },
    {
      key: 'analytics',
      label: 'Analytics',
      icon: <BarChartOutlined />,
      onClick: () => navigate(`/analytics/${record.id}`),
    },
    {
      key: 'conformance',
      label: 'Conformance',
      icon: <CheckCircleOutlined />,
      onClick: () => navigate(`/conformance/${record.id}`),
    },
    { type: 'divider' as const },
    {
      key: 'delete',
      label: 'Delete',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => {
        setLogToDelete(record);
        setDeleteModalOpen(true);
      },
    },
  ];

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: EventLog) => (
        <a onClick={() => onLogSelect?.(record.id) || navigate(`/data/logs/${record.id}`)}>
          {name}
        </a>
      ),
    },
    {
      title: 'Cases',
      dataIndex: 'totalCases',
      key: 'totalCases',
      width: 100,
      render: (value: number) => formatCompactNumber(value),
    },
    {
      title: 'Events',
      dataIndex: 'totalEvents',
      key: 'totalEvents',
      width: 100,
      render: (value: number) => formatCompactNumber(value),
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 150,
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Source',
      dataIndex: 'sourceFile',
      key: 'sourceFile',
      width: 150,
      ellipsis: true,
      render: (file: string) => (
        <Tag color="blue">{file || 'Uploaded'}</Tag>
      ),
    },
    {
      title: '',
      key: 'actions',
      width: 50,
      render: (_: unknown, record: EventLog) => (
        <Dropdown
          menu={{ items: getActions(record) }}
          trigger={['click']}
          placement="bottomRight"
        >
          <Button type="text" icon={<MoreOutlined />} />
        </Dropdown>
      ),
    },
  ];

  if (error) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <p>Failed to load event logs. Please try again.</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  return (
    <>
      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="Search logs..."
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
      </div>

      <Table
        columns={columns}
        dataSource={data?.items || []}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total || 0,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
          showSizeChanger: true,
          showTotal: (total) => `${total} logs`,
        }}
      />

      <Modal
        title="Delete Event Log"
        open={deleteModalOpen}
        onOk={handleDelete}
        onCancel={() => {
          setDeleteModalOpen(false);
          setLogToDelete(null);
        }}
        okText="Delete"
        okButtonProps={{ danger: true, loading: deleteMutation.isPending }}
      >
        <p>
          Are you sure you want to delete <strong>{logToDelete?.name}</strong>?
        </p>
        <p>This action cannot be undone. All associated analysis results will be lost.</p>
      </Modal>
    </>
  );
};
