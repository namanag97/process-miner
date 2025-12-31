/**
 * ObjectDetailPage - Generic template for viewing object details
 *
 * Standardized layout with:
 * - Page header with breadcrumbs and actions
 * - Tabbed navigation for different sections
 * - Consistent loading and error handling
 * - Optional sidebar for quick stats/metrics
 *
 * @example
 * <ObjectDetailPage<EventLog>
 *   title={log.name}
 *   breadcrumb={[{ label: 'Logs', href: '/logs' }, { label: log.name }]}
 *   tabs={[
 *     { key: 'overview', label: 'Overview', content: <LogOverview log={log} /> },
 *     { key: 'analytics', label: 'Analytics', content: <LogAnalytics log={log} /> }
 *   ]}
 * />
 */

import React from 'react';
import { Tabs, Row, Col, Card } from 'antd';
import { PageHeader } from './PageHeader';
import { LoadingState } from './LoadingState';
import { QueryError } from './QueryError';
import { tokens } from '../theme';

// ============================================
// Types
// ============================================

export interface DetailTab {
  key: string;
  label: string;
  content: React.ReactNode;
  icon?: React.ReactNode;
}

export interface ObjectDetailPageProps<T> {
  /** Page title */
  title: string;
  /** Page description */
  description?: string;
  /** Breadcrumb items */
  breadcrumb?: Array<{ label: string; href?: string }>;
  /** Actions in page header */
  actions?: React.ReactNode;
  
  /** Detail tabs */
  tabs: DetailTab[];
  /** Default active tab key */
  defaultTabKey?: string;
  /** Active tab key (controlled) */
  activeTabKey?: string;
  /** Tab change handler */
  onTabChange?: (key: string) => void;
  
  /** Hook for fetching data */
  useDetailHook: (id: string) => {
    data: T | undefined;
    isLoading: boolean;
    error: any;
    refetch: () => void;
  };
  /** Object ID to pass to the hook */
  id: string;
  
  /** Whether to show a sidebar panel */
  showSidebar?: boolean;
  /** Sidebar content */
  sidebarContent?: React.ReactNode;
  /** Sidebar width (relative to grid) */
  sidebarSpan?: number;
}

// ============================================
// ObjectDetailPage Component
// ============================================

export function ObjectDetailPage<T>({
  title,
  description,
  breadcrumb,
  actions,
  tabs,
  defaultTabKey,
  activeTabKey,
  onTabChange,
  useDetailHook,
  id,
  showSidebar = false,
  sidebarContent,
  sidebarSpan = 6,
}: ObjectDetailPageProps<T>) {
  const { data, isLoading, error, refetch } = useDetailHook(id);

  // Loading State
  if (isLoading) {
    return (
      <>
        <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />
        <div style={{ padding: tokens.spacing[6] }}>
          <LoadingState type="fullPage" />
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

  if (!data) {
    return (
      <>
        <PageHeader title={title} description={description} breadcrumb={breadcrumb} actions={actions} />
        <div style={{ padding: tokens.spacing[6] }}>
          <QueryError 
             error={new Error("Object not found")} 
             onRetry={refetch}
          />
        </div>
      </>
    );
  }

  const content = (
    <div style={{ padding: `0 ${tokens.spacing[6]}px` }}>
      <Tabs
        activeKey={activeTabKey}
        defaultActiveKey={defaultTabKey || tabs[0]?.key}
        onChange={onTabChange}
        items={tabs.map((tab) => ({
          key: tab.key,
          label: (
            <span>
              {tab.icon}
              {tab.label}
            </span>
          ),
          children: (
            <div className="animate-fade-in" style={{ paddingTop: tokens.spacing[4] }}>
              {tab.content}
            </div>
          ),
        }))}
      />
    </div>
  );

  return (
    <div className="animate-fade-in">
      <PageHeader 
        title={title} 
        description={description} 
        breadcrumb={breadcrumb} 
        actions={actions} 
      />
      
      {showSidebar ? (
        <div style={{ padding: `0 ${tokens.spacing[6]}px` }}>
          <Row gutter={[24, 24]}>
            <Col xs={24} lg={24 - sidebarSpan}>
              {content}
            </Col>
            <Col xs={24} lg={sidebarSpan}>
              <div style={{ marginTop: tokens.spacing[12] + 4 }}> {/* Align with tab content top */}
                <Card 
                  bordered 
                  style={{ 
                    borderRadius: tokens.radius.lg,
                    background: tokens.colors.surface.card,
                    boxShadow: tokens.shadow.sm
                  }}
                >
                  {sidebarContent}
                </Card>
              </div>
            </Col>
          </Row>
        </div>
      ) : (
        content
      )}
    </div>
  );
}

export default ObjectDetailPage;
