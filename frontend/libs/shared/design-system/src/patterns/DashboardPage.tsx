import React from 'react';
import { Row, Col, Space, Typography, Breadcrumb, Tabs, DatePicker, Select, Button } from 'antd';
import type { TabsProps } from 'antd';
import {
  CalendarOutlined,
  ReloadOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export interface DashboardSection {
  key: string;
  title?: string;
  span?: number; // Grid span (1-24)
  content: React.ReactNode;
}

export interface DashboardPageProps {
  // Header
  title: string;
  description?: string;
  breadcrumbs?: Array<{ label: string; href?: string; onClick?: () => void }>;
  
  // Time controls
  showDatePicker?: boolean;
  dateRange?: [Date | null, Date | null];
  onDateRangeChange?: (range: [Date | null, Date | null]) => void;
  
  // Refresh
  refreshable?: boolean;
  onRefresh?: () => void;
  lastUpdated?: Date;
  
  // KPI row
  kpis?: React.ReactNode;
  
  // Tabs (optional)
  tabs?: TabsProps['items'];
  activeTab?: string;
  onTabChange?: (key: string) => void;
  
  // Dashboard sections (grid layout)
  sections?: DashboardSection[];
  
  // Actions
  actions?: React.ReactNode;
  
  // Loading
  loading?: boolean;
}

/**
 * DashboardPage - Standard dashboard composition pattern
 * 
 * Provides consistent layout for analytics/dashboard pages with:
 * - Page header with title and time range selector
 * - KPI row (MetricCards/KPICards)
 * - Optional tabs for different views
 * - Grid layout for charts and widgets
 * - Refresh functionality
 */
export const DashboardPage: React.FC<DashboardPageProps> = ({
  title,
  description,
  breadcrumbs,
  showDatePicker = true,
  dateRange,
  onDateRangeChange,
  refreshable = true,
  onRefresh,
  lastUpdated,
  kpis,
  tabs,
  activeTab,
  onTabChange,
  sections,
  actions,
  loading,
}) => {
  return (
    <div className="dashboard-page">
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

        {/* Title row */}
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

          <Space wrap>
            {/* Date range picker */}
            {showDatePicker && (
              <RangePicker
                value={dateRange as [Date, Date] | undefined}
                onChange={(dates) =>
                  onDateRangeChange?.(dates as [Date | null, Date | null])
                }
                style={{ width: 280 }}
              />
            )}

            {/* Refresh */}
            {refreshable && (
              <Space size={4}>
                {lastUpdated && (
                  <Text
                    style={{
                      fontSize: 11,
                      color: tokens.colorTextTertiary,
                    }}
                  >
                    Updated {lastUpdated.toLocaleTimeString()}
                  </Text>
                )}
                <Button
                  icon={<ReloadOutlined />}
                  onClick={onRefresh}
                  loading={loading}
                />
              </Space>
            )}

            {/* Custom actions */}
            {actions}
          </Space>
        </div>
      </div>

      {/* KPI Row */}
      {kpis && <div style={{ marginBottom: 24 }}>{kpis}</div>}

      {/* Tabs (optional) */}
      {tabs && tabs.length > 0 ? (
        <Tabs
          activeKey={activeTab}
          onChange={onTabChange}
          items={tabs}
          style={{ marginBottom: 24 }}
        />
      ) : null}

      {/* Sections Grid */}
      {sections && sections.length > 0 && (
        <Row gutter={[16, 16]}>
          {sections.map((section) => (
            <Col key={section.key} span={section.span || 24}>
              {section.title && (
                <Text
                  strong
                  style={{
                    display: 'block',
                    marginBottom: 12,
                    fontSize: 14,
                  }}
                >
                  {section.title}
                </Text>
              )}
              {section.content}
            </Col>
          ))}
        </Row>
      )}
    </div>
  );
};

export default DashboardPage;
