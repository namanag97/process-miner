import React from 'react';
import { Card, Space, Button, Dropdown, Input, Tag, Typography, Breadcrumb } from 'antd';
import type { ColumnsType, TableProps } from 'antd';
import {
  PlusOutlined,
  FilterOutlined,
  SearchOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { DataGrid, DataGridColumn } from '../components/DataGrid';
import { tokens } from '../theme';

const { Text, Title } = Typography;

export interface FilterConfig {
  key: string;
  label: string;
  type: 'select' | 'date' | 'dateRange' | 'text';
  options?: Array<{ label: string; value: string }>;
}

export interface ActionConfig {
  key: string;
  label: string;
  icon?: React.ReactNode;
  onClick: () => void;
  danger?: boolean;
}

export interface ResourceListPageProps<T extends object> {
  // Header
  title: string;
  description?: string;
  breadcrumbs?: Array<{ label: string; href?: string; onClick?: () => void }>;
  
  // Data
  columns: DataGridColumn<T>[];
  data: T[];
  loading?: boolean;
  rowKey?: keyof T | ((record: T) => string);
  
  // Actions
  onCreate?: () => void;
  createLabel?: string;
  actions?: ActionConfig[];
  rowActions?: (record: T) => ActionConfig[];
  onRowClick?: (record: T) => void;
  
  // Filtering
  filters?: FilterConfig[];
  activeFilters?: Record<string, unknown>;
  onFilterChange?: (filters: Record<string, unknown>) => void;
  
  // Search
  searchable?: boolean;
  searchPlaceholder?: string;
  
  // Export
  exportable?: boolean;
  onExport?: () => void;
  
  // Pagination
  pagination?: TableProps<T>['pagination'];
  
  // Selection
  selectable?: boolean;
  selectedRowKeys?: React.Key[];
  onSelectionChange?: (keys: React.Key[], rows: T[]) => void;
  bulkActions?: ActionConfig[];
}

/**
 * ResourceListPage - Standard list page composition pattern
 * 
 * Provides consistent layout for resource listing pages with:
 * - Page header with title, breadcrumbs, and actions
 * - Filter bar
 * - Data grid with search, sorting, pagination
 * - Row actions
 * - Bulk actions (when rows selected)
 */
export function ResourceListPage<T extends object>({
  title,
  description,
  breadcrumbs,
  columns,
  data,
  loading,
  rowKey = 'id' as keyof T,
  onCreate,
  createLabel = 'Create',
  actions,
  rowActions,
  onRowClick,
  filters,
  activeFilters,
  onFilterChange,
  searchable = true,
  searchPlaceholder,
  exportable,
  onExport,
  pagination,
  selectable,
  selectedRowKeys,
  onSelectionChange,
  bulkActions,
}: ResourceListPageProps<T>) {
  // Add row actions column if provided
  const columnsWithActions: DataGridColumn<T>[] = rowActions
    ? [
        ...columns,
        {
          key: 'actions',
          title: '',
          width: 48,
          fixed: 'right',
          render: (_: unknown, record: T) => {
            const recordActions = rowActions(record);
            if (!recordActions.length) return null;

            return (
              <Dropdown
                menu={{
                  items: recordActions.map((action) => ({
                    key: action.key,
                    label: action.label,
                    icon: action.icon,
                    danger: action.danger,
                    onClick: () => action.onClick(),
                  })),
                }}
                trigger={['click']}
              >
                <Button
                  type="text"
                  size="small"
                  icon={<MoreOutlined />}
                  onClick={(e) => e.stopPropagation()}
                />
              </Dropdown>
            );
          },
        },
      ]
    : columns;

  // Row selection config
  const rowSelection = selectable
    ? {
        selectedRowKeys,
        onChange: onSelectionChange,
      }
    : undefined;

  return (
    <div className="resource-list-page">
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        {/* Breadcrumbs */}
        {breadcrumbs && breadcrumbs.length > 0 && (
          <Breadcrumb
            style={{ marginBottom: 8 }}
            items={breadcrumbs.map((crumb, index) => ({
              key: index,
              title: crumb.onClick ? (
                <a onClick={crumb.onClick}>{crumb.label}</a>
              ) : (
                crumb.label
              ),
            }))}
          />
        )}

        {/* Title and actions */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            flexWrap: 'wrap',
            gap: 16,
          }}
        >
          <div>
            <Title level={4} style={{ margin: 0 }}>
              {title}
            </Title>
            {description && (
              <Text style={{ color: tokens.colorTextSecondary }}>
                {description}
              </Text>
            )}
          </div>

          <Space>
            {/* Bulk actions (shown when rows selected) */}
            {selectedRowKeys && selectedRowKeys.length > 0 && bulkActions && (
              <>
                <Tag>{selectedRowKeys.length} selected</Tag>
                {bulkActions.map((action) => (
                  <Button
                    key={action.key}
                    icon={action.icon}
                    danger={action.danger}
                    onClick={action.onClick}
                  >
                    {action.label}
                  </Button>
                ))}
              </>
            )}

            {/* Custom actions */}
            {actions?.map((action) => (
              <Button
                key={action.key}
                icon={action.icon}
                onClick={action.onClick}
              >
                {action.label}
              </Button>
            ))}

            {/* Create button */}
            {onCreate && (
              <Button type="primary" icon={<PlusOutlined />} onClick={onCreate}>
                {createLabel}
              </Button>
            )}
          </Space>
        </div>
      </div>

      {/* Data Grid */}
      <Card styles={{ body: { padding: 0 } }}>
        <DataGrid
          columns={columnsWithActions}
          dataSource={data}
          loading={loading}
          rowKey={rowKey as string}
          searchable={searchable}
          searchPlaceholder={searchPlaceholder}
          exportable={exportable}
          onExport={onExport}
          pagination={pagination}
          rowSelection={rowSelection}
          onRow={
            onRowClick
              ? (record) => ({
                  onClick: () => onRowClick(record),
                  style: { cursor: 'pointer' },
                })
              : undefined
          }
        />
      </Card>
    </div>
  );
}

export default ResourceListPage;
