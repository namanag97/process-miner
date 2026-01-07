/**
 * Advanced FilterPanel - Celonis-style Process Filtering
 *
 * Features:
 * - Activity occurrence filters (with/without)
 * - Activity sequence filters (directly follows)
 * - Performance/duration filters
 * - Time range filters
 * - Attribute filters (resources)
 * - Saved filter presets
 * - Removable filter chips
 *
 * Note: Filter section components have been extracted to
 * ./filter-sections/ for better maintainability and testing.
 */

import { useMemo, useCallback } from 'react';
import { Typography, Collapse, Tag, Button, Space } from 'antd';
import {
  ClearOutlined,
  FilterOutlined,
  ClockCircleOutlined,
  UserOutlined,
  BranchesOutlined,
  ThunderboltOutlined,
  NodeIndexOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../shared/lib/logger';
import type { AppliedFilter, FilterOptions, FilterType } from '../types';

// Import extracted filter section components
import {
  ActivityFilterSection,
  SequenceFilterSection,
  PerformanceFilterSection,
  TimeRangeFilterSection,
  ResourceFilterSection,
  ReworkFilterSection,
  FILTER_COLORS,
} from './filter-sections';

const log = createLogger('FilterPanel');
const { Title, Text } = Typography;

// =============================================================================
// TYPES
// =============================================================================

export interface FilterPanelProps {
  filterOptions: FilterOptions;
  appliedFilters: AppliedFilter[];
  onApplyFilter?: (filter: AppliedFilter) => void;
  onRemoveFilter?: (filterId: string) => void;
  onClearAllFilters?: () => void;
  loading?: boolean;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function FilterPanel({
  filterOptions,
  appliedFilters,
  onApplyFilter,
  onRemoveFilter,
  onClearAllFilters,
}: FilterPanelProps) {
  log.debug('Rendering FilterPanel', { appliedCount: appliedFilters.length });

  const handleApplyFilter = useCallback(
    (filter: AppliedFilter) => {
      onApplyFilter?.(filter);
    },
    [onApplyFilter]
  );

  // Collapse items configuration
  const collapseItems = useMemo(
    () => [
      {
        key: 'activity',
        label: (
          <Space>
            <ThunderboltOutlined style={{ color: tokens.colors.success[500] }} />
            <span>Activity Occurrence</span>
          </Space>
        ),
        children: (
          <ActivityFilterSection
            activities={filterOptions.activities}
            onApply={handleApplyFilter}
          />
        ),
      },
      {
        key: 'sequence',
        label: (
          <Space>
            <BranchesOutlined style={{ color: '#8B5CF6' }} />
            <span>Activity Sequence</span>
          </Space>
        ),
        children: (
          <SequenceFilterSection
            activities={filterOptions.activities}
            onApply={handleApplyFilter}
          />
        ),
      },
      {
        key: 'performance',
        label: (
          <Space>
            <ClockCircleOutlined style={{ color: tokens.colors.warning[500] }} />
            <span>Duration</span>
          </Space>
        ),
        children: (
          <PerformanceFilterSection
            caseDuration={filterOptions.caseDuration}
            onApply={handleApplyFilter}
          />
        ),
      },
      {
        key: 'time',
        label: (
          <Space>
            <FilterOutlined style={{ color: tokens.colors.primary[500] }} />
            <span>Time Range</span>
          </Space>
        ),
        children: (
          <TimeRangeFilterSection
            timeRange={filterOptions.timeRange}
            onApply={handleApplyFilter}
          />
        ),
      },
      {
        key: 'resource',
        label: (
          <Space>
            <UserOutlined style={{ color: '#0EA5E9' }} />
            <span>Resource</span>
          </Space>
        ),
        children: (
          <ResourceFilterSection
            resources={filterOptions.resources}
            onApply={handleApplyFilter}
          />
        ),
      },
      {
        key: 'rework',
        label: (
          <Space>
            <NodeIndexOutlined style={{ color: tokens.colors.error[500] }} />
            <span>Rework / Loops</span>
          </Space>
        ),
        children: (
          <ReworkFilterSection
            activities={filterOptions.activities}
            onApply={handleApplyFilter}
          />
        ),
      },
    ],
    [filterOptions, handleApplyFilter]
  );

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div
        style={{
          padding: tokens.spacing[4],
          borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Title level={5} style={{ margin: 0 }}>
            Filters
          </Title>
          {appliedFilters.length > 0 && (
            <Button
              type="link"
              size="small"
              icon={<ClearOutlined />}
              onClick={() => {
                onClearAllFilters?.();
                log.info('Cleared all filters');
              }}
              style={{ padding: 0 }}
            >
              Clear all
            </Button>
          )}
        </div>
      </div>

      {/* Applied Filters */}
      {appliedFilters.length > 0 && (
        <div
          style={{
            padding: tokens.spacing[3],
            borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
            backgroundColor: tokens.colors.neutral[50],
          }}
        >
          <Text
            type="secondary"
            style={{
              fontSize: tokens.fontSize.xs,
              display: 'block',
              marginBottom: tokens.spacing[2],
            }}
          >
            Applied ({appliedFilters.length})
          </Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {appliedFilters.map((filter) => (
              <Tag
                key={filter.id}
                closable
                onClose={() => onRemoveFilter?.(filter.id)}
                color={filter.color || FILTER_COLORS[filter.type as FilterType]}
                style={{ marginRight: 0 }}
              >
                {filter.label}
              </Tag>
            ))}
          </div>
        </div>
      )}

      {/* Filter Controls */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Collapse
          items={collapseItems}
          defaultActiveKey={['activity']}
          ghost
          expandIconPosition="end"
          style={{ backgroundColor: 'transparent' }}
        />
      </div>
    </div>
  );
}

export default FilterPanel;
