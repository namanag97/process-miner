/**
 * ObjectListPage - Generic template for listing domain objects
 *
 * Provides a standardized layout for object lists with:
 * - Page header with breadcrumbs and actions
 * - Filter/Search bar
 * - Layout options (Grid or Table)
 * - Loading, Error, and Empty states
 *
 * @example
 * <ObjectListPage<Workspace>
 *   title="Workspaces"
 *   type="workspace"
 *   useListHook={useWorkspaces}
 *   renderItem={(ws) => <ObjectCard object={ws} />}
 * />
 */

import { useState, useMemo } from 'react';
import { Input, Segmented, Empty } from 'antd';
import { SearchOutlined, AppstoreOutlined, TableOutlined } from '@ant-design/icons';
import { PageHeader } from './PageHeader';
import { LoadingState } from './LoadingState';
import { QueryError } from './QueryError';
import { EmptyState } from './EmptyState';
import { ObjectCardGrid } from './ObjectCard';
import { tokens } from '../theme';

// ============================================
// Types
// ============================================

export interface ObjectListPageProps<T> {
  /** Page title */
  title: string;
  /** Page description */
  description?: string;
  /** Breadcrumb items */
  breadcrumb?: Array<{ label: string; href?: string }>;
  /** Actions to show in page header */
  actions?: React.ReactNode;

  /** Object type (for defaults) */
  type: string;
  /** Hook for fetching data */
  useListHook: (options: any) => {
    data: { items: T[]; total: number } | undefined;
    isLoading: boolean;
    error: any;
    refetch: () => void;
  };
  /** Options to pass to the hook */
  hookOptions?: any;
  /** Property to use for search filtering */
  searchKey?: keyof T;

  /** Custom render function for list items (Grid view) */
  renderItem: (item: T, index: number) => React.ReactNode;
  /** Layout type: 'grid' or 'table' */
  defaultLayout?: 'grid' | 'table';

  /** Empty state overrides */
  emptyState?: {
    title?: string;
    description?: string;
    actionLabel?: string;
    onAction?: () => void;
  };
}

// ============================================
// ObjectListPage Component
// ============================================

export function ObjectListPage<T>({
  title,
  description,
  breadcrumb,
  actions,
  type,
  useListHook,
  hookOptions = {},
  searchKey,
  renderItem,
  defaultLayout = 'grid',
  emptyState,
}: ObjectListPageProps<T>) {
  const [layout, setLayout] = useState<'grid' | 'table'>(defaultLayout);
  const [searchTerm, setSearchTerm] = useState('');

  const { data, isLoading, error, refetch } = useListHook(hookOptions);

  const items = data?.items || [];

  // Client-side filtering if searchKey is provided
  const filteredItems = useMemo(() => {
    if (!searchTerm || !searchKey) return items;
    const lower = searchTerm.toLowerCase();
    return items.filter((item) => {
      const value = item[searchKey];
      return typeof value === 'string' && value.toLowerCase().includes(lower);
    });
  }, [items, searchTerm, searchKey]);

  // Loading State
  if (isLoading) {
    return (
      <>
        <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />
        <div style={{ padding: tokens.spacing[6] }}>
          <LoadingState type="card" />
        </div>
      </>
    );
  }

  // Error State
  if (error) {
    return (
      <>
        <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />
        <div style={{ padding: tokens.spacing[6] }}>
          <QueryError error={error} onRetry={refetch} />
        </div>
      </>
    );
  }

  // Empty State (No Data)
  if (items.length === 0) {
    return (
      <>
        <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />
        <div style={{ padding: tokens.spacing[12] }}>
          <EmptyState
            title={emptyState?.title || `No ${type}s found`}
            description={emptyState?.description || `Get started by creating your first ${type}.`}
            actionLabel={emptyState?.actionLabel}
            onAction={emptyState?.onAction}
          />
        </div>
      </>
    );
  }

  return (
    <div className="animate-fade-in">
      <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />

      <div style={{ padding: `0 ${tokens.spacing[6]}px ${tokens.spacing[6]}px` }}>
        {/* Controls Bar */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: tokens.spacing[6],
          }}
        >
          <Input
            placeholder={`Search ${type}s...`}
            prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ maxWidth: 300 }}
            allowClear
          />

          <Segmented
            options={[
              { value: 'grid', icon: <AppstoreOutlined /> },
              { value: 'table', icon: <TableOutlined /> },
            ]}
            value={layout}
            onChange={(val) => setLayout(val as 'grid' | 'table')}
          />
        </div>

        {/* Content Area */}
        {filteredItems.length > 0 ? (
          layout === 'grid' ? (
            <ObjectCardGrid columns={3}>
              {filteredItems.map((item, index) => renderItem(item, index))}
            </ObjectCardGrid>
          ) : (
            <div style={{ background: tokens.colors.surface.card, borderRadius: tokens.radius.lg, border: `1px solid ${tokens.colors.neutral[200]}`, overflow: 'hidden' }}>
              {/* Table implementation would go here, or pass content from parent */}
              <div style={{ padding: tokens.spacing[12], textAlign: 'center' }}>
                <Empty description="Table view not yet implemented for this template. Use grid view." />
              </div>
            </div>
          )
        ) : (
          <div style={{ padding: tokens.spacing[12] }}>
            <Empty description={`No ${type}s match your search.`} />
          </div>
        )}
      </div>
    </div>
  );
}

export default ObjectListPage;
