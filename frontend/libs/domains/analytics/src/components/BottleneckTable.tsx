import React, { useMemo } from 'react';
import {
  Card,
  Table,
  Progress,
  Tag,
  Typography,
  Space,
  Alert,
  Spin,
  Tooltip,
  Empty,
} from 'antd';
import {
  WarningOutlined,
  ClockCircleOutlined,
  FireOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useBottlenecks } from '../hooks';

const { Text } = Typography;

interface BottleneckTableProps {
  logId: string;
  onActivityClick?: (activity: string) => void;
  maxRows?: number;
  showTitle?: boolean;
}

interface BottleneckRow {
  activity: string;
  waitingTime: number;
  frequency: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  percentOfMax: number;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

function getSeverity(percentOfMax: number): 'critical' | 'high' | 'medium' | 'low' {
  if (percentOfMax >= 80) return 'critical';
  if (percentOfMax >= 50) return 'high';
  if (percentOfMax >= 25) return 'medium';
  return 'low';
}

function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'critical':
      return '#ff4d4f';
    case 'high':
      return '#fa8c16';
    case 'medium':
      return '#faad14';
    default:
      return '#52c41a';
  }
}

export const BottleneckTable: React.FC<BottleneckTableProps> = ({
  logId,
  onActivityClick,
  maxRows,
  showTitle = true,
}) => {
  const { data, isLoading, error } = useBottlenecks(logId);

  const tableData = useMemo<BottleneckRow[]>(() => {
    if (!data?.bottlenecks || data.bottlenecks.length === 0) return [];

    const maxWaitingTime = Math.max(...data.bottlenecks.map((b: { waitingTime: number }) => b.waitingTime));
    const rows = data.bottlenecks.map((b: { activity: string; waitingTime: number; frequency: number }) => {
      const percentOfMax = maxWaitingTime > 0 ? (b.waitingTime / maxWaitingTime) * 100 : 0;
      return {
        activity: b.activity,
        waitingTime: b.waitingTime,
        frequency: b.frequency,
        severity: getSeverity(percentOfMax),
        percentOfMax,
      };
    });

    return maxRows ? rows.slice(0, maxRows) : rows;
  }, [data, maxRows]);

  const columns: ColumnsType<BottleneckRow> = [
    {
      title: '#',
      dataIndex: 'rank',
      key: 'rank',
      width: 50,
      render: (_, __, index) => (
        <Text type="secondary">{index + 1}</Text>
      ),
    },
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (activity: string, record) => (
        <Space>
          {record.severity === 'critical' && (
            <FireOutlined style={{ color: '#ff4d4f' }} />
          )}
          <Text
            strong
            style={{
              cursor: onActivityClick ? 'pointer' : 'default',
              color: onActivityClick ? '#0052cc' : undefined,
            }}
            onClick={() => onActivityClick?.(activity)}
          >
            {activity}
          </Text>
        </Space>
      ),
    },
    {
      title: (
        <Tooltip title="Average waiting time before this activity">
          <Space>
            <ClockCircleOutlined />
            Waiting Time
          </Space>
        </Tooltip>
      ),
      dataIndex: 'waitingTime',
      key: 'waitingTime',
      width: 180,
      sorter: (a, b) => a.waitingTime - b.waitingTime,
      defaultSortOrder: 'descend',
      render: (waitingTime: number, record) => (
        <Space direction="vertical" size={2} style={{ width: '100%' }}>
          <Text strong>{formatDuration(waitingTime)}</Text>
          <Progress
            percent={record.percentOfMax}
            size="small"
            showInfo={false}
            strokeColor={getSeverityColor(record.severity)}
            style={{ margin: 0, width: 100 }}
          />
        </Space>
      ),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      filters: [
        { text: 'Critical', value: 'critical' },
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      onFilter: (value, record) => record.severity === value,
      render: (severity: string) => {
        const colors: Record<string, string> = {
          critical: 'error',
          high: 'warning',
          medium: 'gold',
          low: 'success',
        };
        return (
          <Tag color={colors[severity]}>
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </Tag>
        );
      },
    },
    {
      title: 'Frequency',
      dataIndex: 'frequency',
      key: 'frequency',
      width: 100,
      sorter: (a, b) => a.frequency - b.frequency,
      render: (frequency: number) => (
        <Text>{frequency.toLocaleString()}</Text>
      ),
    },
  ];

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load bottlenecks"
        description="Could not retrieve bottleneck data."
      />
    );
  }

  const content = (
    <Spin spinning={isLoading}>
      {tableData.length === 0 && !isLoading ? (
        <Empty
          description="No bottlenecks detected"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      ) : (
        <Table
          columns={columns}
          dataSource={tableData}
          rowKey="activity"
          size="small"
          pagination={
            tableData.length > 10
              ? { pageSize: 10, showSizeChanger: false }
              : false
          }
        />
      )}
    </Spin>
  );

  if (!showTitle) {
    return content;
  }

  return (
    <Card
      title={
        <Space>
          <WarningOutlined style={{ color: '#faad14' }} />
          Bottleneck Analysis
          {data && (
            <Tag color="default">{data.bottlenecks?.length || 0} detected</Tag>
          )}
        </Space>
      }
      styles={{ body: { padding: tableData.length === 0 ? 24 : 0 } }}
    >
      {content}
    </Card>
  );
};
