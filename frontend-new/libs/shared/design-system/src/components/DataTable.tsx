import React, { useMemo } from 'react';
import { Table, Input, Space, Button, Typography } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';
import type { TableProps, ColumnsType } from 'antd/es/table';
import { tokens } from '../theme';

const { Text } = Typography;

export interface DataTableColumn<T> {
  key: string;
  title: string;
  dataIndex: keyof T | string[];
  width?: number | string;
  render?: (value: unknown, record: T, index: number) => React.ReactNode;
  sorter?: boolean | ((a: T, b: T) => number);
  filters?: { text: string; value: string }[];
  onFilter?: (value: string, record: T) => boolean;
  align?: 'left' | 'center' | 'right';
  ellipsis?: boolean;
  fixed?: 'left' | 'right';
}

export interface DataTableProps<T extends { id?: string; key?: string }> {
  columns: DataTableColumn<T>[];
  data: T[];
  loading?: boolean;
  searchable?: boolean;
  searchPlaceholder?: string;
  onRowClick?: (record: T) => void;
  onRefresh?: () => void;
  rowSelection?: TableProps<T>['rowSelection'];
  pagination?: TableProps<T>['pagination'] | false;
  scroll?: TableProps<T>['scroll'];
  size?: 'small' | 'middle' | 'large';
  emptyText?: string;
  title?: React.ReactNode;
  extra?: React.ReactNode;
  sticky?: boolean;
}

/**
 * DataTable - Reusable table component with search, sorting, and filtering
 * Wraps Ant Design Table with consistent styling
 */
export function DataTable<T extends { id?: string; key?: string }>({
  columns,
  data,
  loading = false,
  searchable = false,
  searchPlaceholder = 'Search...',
  onRowClick,
  onRefresh,
  rowSelection,
  pagination = { pageSize: 10, showSizeChanger: true, showTotal: (total) => `${total} items` },
  scroll,
  size = 'middle',
  emptyText = 'No data available',
  title,
  extra,
  sticky = false,
}: DataTableProps<T>) {
  const [searchText, setSearchText] = React.useState('');

  const filteredData = useMemo(() => {
    if (!searchText) return data;
    const lowerSearch = searchText.toLowerCase();
    return data.filter((record) => {
      return columns.some((col) => {
        const value = Array.isArray(col.dataIndex)
          ? col.dataIndex.reduce((obj, key) => (obj as Record<string, unknown>)?.[key], record as unknown)
          : (record as Record<string, unknown>)[col.dataIndex as string];
        return String(value ?? '').toLowerCase().includes(lowerSearch);
      });
    });
  }, [data, searchText, columns]);

  const antColumns: ColumnsType<T> = columns.map((col) => ({
    key: col.key,
    title: col.title,
    dataIndex: col.dataIndex,
    width: col.width,
    render: col.render,
    sorter: col.sorter,
    filters: col.filters,
    onFilter: col.onFilter as ColumnsType<T>[number]['onFilter'],
    align: col.align,
    ellipsis: col.ellipsis,
    fixed: col.fixed,
  }));

  return (
    <div>
      {(title || searchable || onRefresh || extra) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: tokens.spacing[4],
            flexWrap: 'wrap',
            gap: tokens.spacing[3],
          }}
        >
          <div>{title && <Text strong style={{ fontSize: tokens.fontSize.lg }}>{title}</Text>}</div>
          <Space wrap>
            {searchable && (
              <Input
                placeholder={searchPlaceholder}
                prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
                style={{ width: 240 }}
              />
            )}
            {onRefresh && (
              <Button
                icon={<ReloadOutlined />}
                onClick={onRefresh}
                loading={loading}
              >
                Refresh
              </Button>
            )}
            {extra}
          </Space>
        </div>
      )}

      <Table<T>
        columns={antColumns}
        dataSource={filteredData}
        loading={loading}
        rowKey={(record) => record.id ?? record.key ?? JSON.stringify(record)}
        rowSelection={rowSelection}
        pagination={pagination}
        scroll={scroll}
        size={size}
        sticky={sticky}
        locale={{ emptyText }}
        onRow={onRowClick ? (record) => ({
          onClick: () => onRowClick(record),
          style: { cursor: 'pointer' },
        }) : undefined}
        style={{
          borderRadius: tokens.radius.lg,
        }}
      />
    </div>
  );
}

export default DataTable;
