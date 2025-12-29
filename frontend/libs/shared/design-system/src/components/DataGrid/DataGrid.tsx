import React, { useState, useMemo } from 'react';
import { Table, Input, Button, Space, Dropdown, Typography, Tooltip } from 'antd';
import type { TableProps, ColumnsType, TablePaginationConfig } from 'antd';
import type { FilterValue, SorterResult } from 'antd/es/table/interface';
import {
  SearchOutlined,
  FilterOutlined,
  DownloadOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { tokens } from '../../theme';

const { Text } = Typography;

export interface DataGridColumn<T> extends Omit<ColumnsType<T>[number], 'key'> {
  key: string;
  searchable?: boolean;
  exportable?: boolean;
}

export interface DataGridProps<T extends object> extends Omit<TableProps<T>, 'columns'> {
  columns: DataGridColumn<T>[];
  searchable?: boolean;
  searchPlaceholder?: string;
  exportable?: boolean;
  onExport?: () => void;
  refreshable?: boolean;
  onRefresh?: () => void;
  density?: 'compact' | 'default' | 'comfortable';
  title?: string;
  subtitle?: string;
  toolbar?: React.ReactNode;
  emptyText?: string;
  stickyHeader?: boolean;
  maxHeight?: number | string;
}

/**
 * DataGrid - High-density enterprise data table
 * 
 * Features:
 * - Global search across searchable columns
 * - Export functionality
 * - Density control (compact/default/comfortable)
 * - Sticky header support
 * - Custom toolbar slot
 */
export function DataGrid<T extends object>({
  columns,
  dataSource,
  searchable = false,
  searchPlaceholder = 'Search...',
  exportable = false,
  onExport,
  refreshable = false,
  onRefresh,
  density = 'compact',
  title,
  subtitle,
  toolbar,
  emptyText = 'No data',
  stickyHeader = false,
  maxHeight,
  loading,
  pagination,
  onChange,
  ...tableProps
}: DataGridProps<T>) {
  const [searchText, setSearchText] = useState('');

  // Filter data based on search
  const filteredData = useMemo(() => {
    if (!searchText || !dataSource) return dataSource;

    const searchLower = searchText.toLowerCase();
    const searchableKeys = columns
      .filter((col) => col.searchable !== false)
      .map((col) => col.dataIndex)
      .filter(Boolean);

    return dataSource.filter((record: T) =>
      searchableKeys.some((key) => {
        const value = (record as Record<string, unknown>)[key as string];
        return String(value).toLowerCase().includes(searchLower);
      })
    );
  }, [dataSource, searchText, columns]);

  // Convert columns to Ant Design format
  const antColumns: ColumnsType<T> = columns.map((col) => ({
    ...col,
    key: col.key,
  }));

  // Determine table size based on density
  const tableSize = density === 'compact' ? 'small' : density === 'comfortable' ? 'large' : 'middle';

  // Default pagination config
  const defaultPagination: TablePaginationConfig = {
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total, range) => (
      <Text style={{ fontSize: 12, color: tokens.colorTextSecondary }}>
        {range[0]}-{range[1]} of {total} items
      </Text>
    ),
    pageSizeOptions: ['10', '20', '50', '100'],
    size: 'small',
    ...(typeof pagination === 'object' ? pagination : {}),
  };

  return (
    <div className="data-grid">
      {/* Header */}
      {(title || searchable || exportable || toolbar) && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: 16,
            flexWrap: 'wrap',
            gap: 12,
          }}
        >
          {/* Title section */}
          {(title || subtitle) && (
            <div>
              {title && (
                <Text strong style={{ fontSize: 16 }}>
                  {title}
                </Text>
              )}
              {subtitle && (
                <Text
                  style={{
                    display: 'block',
                    fontSize: 12,
                    color: tokens.colorTextSecondary,
                  }}
                >
                  {subtitle}
                </Text>
              )}
            </div>
          )}

          {/* Toolbar */}
          <Space size={8} wrap>
            {searchable && (
              <Input
                prefix={<SearchOutlined style={{ color: tokens.colorTextTertiary }} />}
                placeholder={searchPlaceholder}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                allowClear
                style={{ width: 240 }}
              />
            )}
            {toolbar}
            {refreshable && (
              <Tooltip title="Refresh">
                <Button
                  icon={<ReloadOutlined />}
                  onClick={onRefresh}
                  loading={loading as boolean}
                />
              </Tooltip>
            )}
            {exportable && (
              <Tooltip title="Export">
                <Button icon={<DownloadOutlined />} onClick={onExport}>
                  Export
                </Button>
              </Tooltip>
            )}
          </Space>
        </div>
      )}

      {/* Table */}
      <Table<T>
        {...tableProps}
        columns={antColumns}
        dataSource={filteredData}
        loading={loading}
        size={tableSize}
        pagination={pagination === false ? false : defaultPagination}
        onChange={onChange}
        scroll={{
          x: 'max-content',
          y: maxHeight,
        }}
        sticky={stickyHeader}
        locale={{
          emptyText,
        }}
      />
    </div>
  );
}

export default DataGrid;
