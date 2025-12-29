import React, { useState, useMemo } from 'react';
import {
  Table,
  Card,
  Input,
  Space,
  Button,
  Tooltip,
  Progress,
  Typography,
  Checkbox,
  Alert,
  Spin,
  Empty,
} from 'antd';
import {
  SearchOutlined,
  BarChartOutlined,
  ClockCircleOutlined,
  SwapOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import type { ProcessVariant } from 'process-mining-sdk';
import { useVariants } from '../hooks';
import { HappyPathBadge } from './HappyPathBadge';
import { VariantTrace } from './VariantTrace';

const { Text } = Typography;

interface VariantListProps {
  logId: string;
  onVariantSelect?: (variant: ProcessVariant) => void;
  onCompare?: (variants: ProcessVariant[]) => void;
  selectedVariantKey?: string;
  showCompareButton?: boolean;
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined || seconds === null) return '-';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

export const VariantList: React.FC<VariantListProps> = ({
  logId,
  onVariantSelect,
  onCompare,
  selectedVariantKey,
  showCompareButton = true,
}) => {
  const { data, isLoading, error } = useVariants(logId);
  const [searchText, setSearchText] = useState('');
  const [selectedKeys, setSelectedKeys] = useState<string[]>([]);

  const filteredVariants = useMemo(() => {
    if (!data?.variants) return [] as ProcessVariant[];
    if (!searchText) return data.variants;
    const lower = searchText.toLowerCase();
    return data.variants.filter(
      (v: ProcessVariant) =>
        v.activities.some((a: string) => a.toLowerCase().includes(lower)) ||
        v.key.toLowerCase().includes(lower)
    );
  }, [data?.variants, searchText]);

  const totalCases = useMemo(
    () => data?.variants?.reduce((sum: number, v: ProcessVariant) => sum + v.caseCount, 0) || 0,
    [data?.variants]
  );

  const handleRowSelect = (variant: ProcessVariant, checked: boolean) => {
    if (checked) {
      setSelectedKeys((prev) => [...prev, variant.key]);
    } else {
      setSelectedKeys((prev) => prev.filter((k) => k !== variant.key));
    }
  };

  const handleCompare = () => {
    if (onCompare && data?.variants) {
      const selectedVariants = data.variants.filter((v: ProcessVariant) =>
        selectedKeys.includes(v.key)
      );
      onCompare(selectedVariants);
    }
  };

  const columns: ColumnsType<ProcessVariant> = [
    {
      title: '',
      dataIndex: 'select',
      width: 40,
      render: (_, record) =>
        showCompareButton && (
          <Checkbox
            checked={selectedKeys.includes(record.key)}
            onChange={(e) => handleRowSelect(record, e.target.checked)}
            onClick={(e) => e.stopPropagation()}
          />
        ),
    },
    {
      title: '#',
      dataIndex: 'rank',
      width: 50,
      render: (_, __, index) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {index + 1}
        </Text>
      ),
    },
    {
      title: 'Variant',
      dataIndex: 'activities',
      key: 'activities',
      render: (activities: string[], record) => (
        <Space direction="vertical" size={4}>
          <Space>
            <Text strong style={{ fontSize: 13 }}>
              {record.key}
            </Text>
            <HappyPathBadge isHappyPath={record.isHappyPath} size="small" />
          </Space>
          <VariantTrace activities={activities} compact maxVisible={5} />
        </Space>
      ),
    },
    {
      title: (
        <Tooltip title="Number of cases following this variant">
          <Space>
            <BarChartOutlined />
            Cases
          </Space>
        </Tooltip>
      ),
      dataIndex: 'caseCount',
      key: 'caseCount',
      width: 140,
      sorter: (a, b) => a.caseCount - b.caseCount,
      defaultSortOrder: 'descend',
      render: (count: number, record) => {
        const percentage = totalCases > 0 ? (count / totalCases) * 100 : 0;
        return (
          <Space direction="vertical" size={2} style={{ width: '100%' }}>
            <Text strong>{count.toLocaleString()}</Text>
            <Progress
              percent={percentage}
              size="small"
              showInfo={false}
              strokeColor="#0052cc"
              style={{ margin: 0, width: 80 }}
            />
            <Text type="secondary" style={{ fontSize: 11 }}>
              {percentage.toFixed(1)}%
            </Text>
          </Space>
        );
      },
    },
    {
      title: (
        <Tooltip title="Number of activities in this variant">
          <Space>
            <SwapOutlined />
            Steps
          </Space>
        </Tooltip>
      ),
      dataIndex: 'length',
      key: 'length',
      width: 80,
      sorter: (a, b) => a.length - b.length,
      render: (length: number) => (
        <Text style={{ fontSize: 13 }}>{length}</Text>
      ),
    },
    {
      title: (
        <Tooltip title="Average duration for cases of this variant">
          <Space>
            <ClockCircleOutlined />
            Avg Duration
          </Space>
        </Tooltip>
      ),
      dataIndex: 'avgDurationSeconds',
      key: 'avgDurationSeconds',
      width: 110,
      sorter: (a, b) =>
        (a.avgDurationSeconds || 0) - (b.avgDurationSeconds || 0),
      render: (duration?: number) => (
        <Text style={{ fontSize: 13 }}>{formatDuration(duration)}</Text>
      ),
    },
  ];

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load variants"
        description="Could not retrieve variant data for this log."
      />
    );
  }

  return (
    <Card
      title={
        <Space>
          <span>Process Variants</span>
          {data && (
            <Text type="secondary" style={{ fontWeight: 'normal', fontSize: 13 }}>
              ({data.totalVariants} variants, {totalCases.toLocaleString()} cases)
            </Text>
          )}
        </Space>
      }
      extra={
        <Space>
          <Input
            placeholder="Search activities..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 200 }}
            allowClear
          />
          {showCompareButton && (
            <Button
              type="primary"
              disabled={selectedKeys.length < 2}
              onClick={handleCompare}
            >
              Compare ({selectedKeys.length})
            </Button>
          )}
        </Space>
      }
      styles={{ body: { padding: 0 } }}
    >
      <Spin spinning={isLoading}>
        {filteredVariants.length === 0 && !isLoading ? (
          <Empty
            description={searchText ? 'No matching variants' : 'No variants found'}
            style={{ padding: 40 }}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={filteredVariants}
            rowKey="key"
            size="small"
            pagination={{
              pageSize: 20,
              showSizeChanger: true,
              showTotal: (total) => `${total} variants`,
            }}
            onRow={(record) => ({
              onClick: () => onVariantSelect?.(record),
              style: {
                cursor: onVariantSelect ? 'pointer' : 'default',
                backgroundColor:
                  record.key === selectedVariantKey ? '#e6f4ff' : undefined,
              },
            })}
            scroll={{ x: 700 }}
          />
        )}
      </Spin>
    </Card>
  );
};
