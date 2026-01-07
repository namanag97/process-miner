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
 */

import { useState, useMemo, useCallback } from 'react';
import {
  Typography,
  Collapse,
  DatePicker,
  Select,

  Tag,
  Button,
  Space,


  InputNumber,
  Radio,

  Empty,

} from 'antd';
import {
  ClearOutlined,
  FilterOutlined,
  ClockCircleOutlined,
  UserOutlined,
  BranchesOutlined,
  ThunderboltOutlined,
  NodeIndexOutlined,
  SwapRightOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { tokens } from '@/src/shared/design-system';
import { createLogger } from '../../../shared/lib/logger';
import { formatDuration } from '../utils/colorScales';
import type { AppliedFilter, FilterOptions, FilterType } from '../types';

const log = createLogger('FilterPanel');
const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

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
// FILTER TYPE COLORS
// =============================================================================

const FILTER_COLORS: Record<FilterType, string> = {
  timeRange: 'blue',
  activity: 'green',
  activitySequence: 'purple',
  performance: 'orange',
  resource: 'cyan',
  variant: 'magenta',
  rework: 'red',
};

// =============================================================================
// FILTER SECTION COMPONENTS
// =============================================================================

interface ActivityFilterSectionProps {
  activities: string[];
  onApply: (filter: AppliedFilter) => void;
}

function ActivityFilterSection({ activities, onApply }: ActivityFilterSectionProps) {
  const [mode, setMode] = useState<'include' | 'exclude'>('include');
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);

  const handleApply = useCallback(() => {
    if (selectedActivities.length === 0) return;

    const filter: AppliedFilter = {
      id: `activity-${mode}-${Date.now()}`,
      type: 'activity',
      label:
        mode === 'include'
          ? `With: ${selectedActivities.length > 1 ? `${selectedActivities.length} activities` : selectedActivities[0]}`
          : `Without: ${selectedActivities.length > 1 ? `${selectedActivities.length} activities` : selectedActivities[0]}`,
      value: { mode, activities: selectedActivities },
      color: FILTER_COLORS.activity,
    };

    onApply(filter);
    setSelectedActivities([]);
    log.info('Applied activity filter', filter);
  }, [mode, selectedActivities, onApply]);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <Radio.Group value={mode} onChange={(e) => setMode(e.target.value)} size="small">
        <Radio.Button value="include">Cases With</Radio.Button>
        <Radio.Button value="exclude">Cases Without</Radio.Button>
      </Radio.Group>

      <Select
        mode="multiple"
        placeholder="Select activities..."
        value={selectedActivities}
        onChange={setSelectedActivities}
        options={activities.map((a) => ({ label: a, value: a }))}
        style={{ width: '100%' }}
        size="small"
        maxTagCount={2}
        showSearch
        filterOption={(input, option) =>
          (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
        }
      />

      <Button
        type="primary"
        size="small"
        block
        disabled={selectedActivities.length === 0}
        onClick={handleApply}
        icon={<FilterOutlined />}
      >
        Apply Filter
      </Button>
    </Space>
  );
}

interface SequenceFilterSectionProps {
  activities: string[];
  onApply: (filter: AppliedFilter) => void;
}

function SequenceFilterSection({ activities, onApply }: SequenceFilterSectionProps) {
  const [sourceActivity, setSourceActivity] = useState<string | null>(null);
  const [targetActivity, setTargetActivity] = useState<string | null>(null);
  const [mode, setMode] = useState<'direct' | 'eventual'>('direct');

  const handleApply = useCallback(() => {
    if (!sourceActivity || !targetActivity) return;

    const filter: AppliedFilter = {
      id: `sequence-${mode}-${Date.now()}`,
      type: 'activitySequence',
      label: `${sourceActivity} ${mode === 'direct' ? '→' : '⤳'} ${targetActivity}`,
      value: { source: sourceActivity, target: targetActivity, mode },
      color: FILTER_COLORS.activitySequence,
    };

    onApply(filter);
    setSourceActivity(null);
    setTargetActivity(null);
    log.info('Applied sequence filter', filter);
  }, [sourceActivity, targetActivity, mode, onApply]);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <Radio.Group value={mode} onChange={(e) => setMode(e.target.value)} size="small">
        <Radio.Button value="direct">Directly Follows</Radio.Button>
        <Radio.Button value="eventual">Eventually Follows</Radio.Button>
      </Radio.Group>

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Select
          placeholder="From..."
          value={sourceActivity}
          onChange={setSourceActivity}
          options={activities.map((a) => ({ label: a, value: a }))}
          style={{ flex: 1 }}
          size="small"
          showSearch
        />
        <SwapRightOutlined style={{ color: tokens.colors.neutral[400] }} />
        <Select
          placeholder="To..."
          value={targetActivity}
          onChange={setTargetActivity}
          options={activities.map((a) => ({ label: a, value: a }))}
          style={{ flex: 1 }}
          size="small"
          showSearch
        />
      </div>

      <Button
        type="primary"
        size="small"
        block
        disabled={!sourceActivity || !targetActivity}
        onClick={handleApply}
        icon={<FilterOutlined />}
      >
        Apply Filter
      </Button>
    </Space>
  );
}

interface PerformanceFilterSectionProps {
  caseDuration: { min: number; max: number; mean: number; p90?: number };
  onApply: (filter: AppliedFilter) => void;
}

function PerformanceFilterSection({ caseDuration, onApply }: PerformanceFilterSectionProps) {
  const [minDuration, setMinDuration] = useState<number>(0);
  const [maxDuration, setMaxDuration] = useState<number>(caseDuration.max);
  const [unit, setUnit] = useState<'hours' | 'days'>('days');

  const multiplier = unit === 'hours' ? 3600 : 86400;

  const handleApply = useCallback(() => {
    const minSeconds = minDuration * multiplier;
    const maxSeconds = maxDuration * multiplier;

    const filter: AppliedFilter = {
      id: `performance-${Date.now()}`,
      type: 'performance',
      label: `Duration: ${formatDuration(minSeconds)} - ${formatDuration(maxSeconds)}`,
      value: { min: minSeconds, max: maxSeconds },
      color: FILTER_COLORS.performance,
    };

    onApply(filter);
    log.info('Applied performance filter', filter);
  }, [minDuration, maxDuration, multiplier, onApply]);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Text style={{ fontSize: 12 }}>Unit:</Text>
        <Radio.Group value={unit} onChange={(e) => setUnit(e.target.value)} size="small">
          <Radio.Button value="hours">Hours</Radio.Button>
          <Radio.Button value="days">Days</Radio.Button>
        </Radio.Group>
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <div style={{ flex: 1 }}>
          <Text style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>Min</Text>
          <InputNumber
            size="small"
            min={0}
            value={minDuration}
            onChange={(v) => setMinDuration(v ?? 0)}
            style={{ width: '100%' }}
            addonAfter={unit === 'hours' ? 'h' : 'd'}
          />
        </div>
        <div style={{ flex: 1 }}>
          <Text style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>Max</Text>
          <InputNumber
            size="small"
            min={0}
            value={maxDuration}
            onChange={(v) => setMaxDuration(v ?? caseDuration.max / multiplier)}
            style={{ width: '100%' }}
            addonAfter={unit === 'hours' ? 'h' : 'd'}
          />
        </div>
      </div>

      <div style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>
        Avg: {formatDuration(caseDuration.mean)}
        {caseDuration.p90 && ` | P90: ${formatDuration(caseDuration.p90)}`}
      </div>

      <Button
        type="primary"
        size="small"
        block
        onClick={handleApply}
        icon={<ClockCircleOutlined />}
      >
        Apply Duration Filter
      </Button>
    </Space>
  );
}

interface TimeRangeFilterSectionProps {
  timeRange: { start: string; end: string };
  onApply: (filter: AppliedFilter) => void;
}

function TimeRangeFilterSection({ timeRange: _timeRange, onApply }: TimeRangeFilterSectionProps) {
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(
    null
  );
  const [showCustom, setShowCustom] = useState(false);

  const handlePresetClick = useCallback((preset: 'last7' | 'last30' | 'last90' | 'ytd') => {
    const now = dayjs();
    let start: dayjs.Dayjs;
    const end: dayjs.Dayjs = now;

    switch (preset) {
      case 'last7':
        start = now.subtract(7, 'day');
        break;
      case 'last30':
        start = now.subtract(30, 'day');
        break;
      case 'last90':
        start = now.subtract(90, 'day');
        break;
      case 'ytd':
        start = now.startOf('year');
        break;
      default:
        return;
    }

    const filter: AppliedFilter = {
      id: `time-${preset}-${Date.now()}`,
      type: 'timeRange',
      label: preset === 'ytd' ? 'YTD' : `Last ${preset.replace('last', '')} days`,
      value: { start: start.toISOString(), end: end.toISOString() },
      color: FILTER_COLORS.timeRange,
    };

    onApply(filter);
    log.info('Applied time preset filter', { preset });
  }, [onApply]);

  const handleApply = useCallback(() => {
    if (!dateRange || !dateRange[0] || !dateRange[1]) return;

    const filter: AppliedFilter = {
      id: `time-${Date.now()}`,
      type: 'timeRange',
      label: `${dateRange[0].format('MMM D')} – ${dateRange[1].format('MMM D, YYYY')}`,
      value: { start: dateRange[0].toISOString(), end: dateRange[1].toISOString() },
      color: FILTER_COLORS.timeRange,
    };

    onApply(filter);
    setDateRange(null);
    setShowCustom(false);
    log.info('Applied time range filter', filter);
  }, [dateRange, onApply]);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      {/* Quick Presets */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
        <Button size="small" onClick={() => handlePresetClick('last7')}>Last 7d</Button>
        <Button size="small" onClick={() => handlePresetClick('last30')}>Last 30d</Button>
        <Button size="small" onClick={() => handlePresetClick('last90')}>Last 90d</Button>
        <Button size="small" onClick={() => handlePresetClick('ytd')}>YTD</Button>
        <Button
          size="small"
          type={showCustom ? 'primary' : 'default'}
          onClick={() => setShowCustom(!showCustom)}
        >
          Custom
        </Button>
      </div>

      {/* Custom Date Range */}
      {showCustom && (
        <>
          <RangePicker
            value={dateRange}
            onChange={(dates) => setDateRange(dates)}
            style={{ width: '100%' }}
            size="small"
          />

          <Button
            type="primary"
            size="small"
            block
            disabled={!dateRange || !dateRange[0] || !dateRange[1]}
            onClick={handleApply}
            icon={<FilterOutlined />}
          >
            Apply Custom Range
          </Button>
        </>
      )}
    </Space>
  );
}

interface ResourceFilterSectionProps {
  resources: string[];
  onApply: (filter: AppliedFilter) => void;
}

function ResourceFilterSection({ resources, onApply }: ResourceFilterSectionProps) {
  const [selectedResources, setSelectedResources] = useState<string[]>([]);

  const handleApply = useCallback(() => {
    if (selectedResources.length === 0) return;

    const filter: AppliedFilter = {
      id: `resource-${Date.now()}`,
      type: 'resource',
      label: `Resource: ${selectedResources.length > 1 ? `${selectedResources.length} selected` : selectedResources[0]}`,
      value: selectedResources,
      color: FILTER_COLORS.resource,
    };

    onApply(filter);
    setSelectedResources([]);
    log.info('Applied resource filter', filter);
  }, [selectedResources, onApply]);

  if (resources.length === 0) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description="No resources available"
        style={{ margin: '16px 0' }}
      />
    );
  }

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <Select
        mode="multiple"
        placeholder="Select resources..."
        value={selectedResources}
        onChange={setSelectedResources}
        options={resources.map((r) => ({ label: r, value: r }))}
        style={{ width: '100%' }}
        size="small"
        maxTagCount={2}
        showSearch
      />

      <Button
        type="primary"
        size="small"
        block
        disabled={selectedResources.length === 0}
        onClick={handleApply}
        icon={<UserOutlined />}
      >
        Apply Resource Filter
      </Button>
    </Space>
  );
}

interface ReworkFilterSectionProps {
  activities: string[];
  onApply: (filter: AppliedFilter) => void;
}

function ReworkFilterSection({ activities, onApply }: ReworkFilterSectionProps) {
  const [activity, setActivity] = useState<string | null>(null);
  const [minRepetitions, setMinRepetitions] = useState<number>(2);

  const handleApply = useCallback(() => {
    const filter: AppliedFilter = {
      id: `rework-${Date.now()}`,
      type: 'rework',
      label: activity
        ? `Rework: ${activity} ≥${minRepetitions}x`
        : `Any Rework ≥${minRepetitions}x`,
      value: { activity, minRepetitions },
      color: FILTER_COLORS.rework,
    };

    onApply(filter);
    setActivity(null);
    log.info('Applied rework filter', filter);
  }, [activity, minRepetitions, onApply]);

  return (
    <Space direction="vertical" style={{ width: '100%' }} size={12}>
      <Select
        placeholder="Any activity (optional)"
        value={activity}
        onChange={setActivity}
        options={[
          { label: 'Any activity', value: null },
          ...activities.map((a) => ({ label: a, value: a })),
        ]}
        style={{ width: '100%' }}
        size="small"
        allowClear
        showSearch
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <Text style={{ fontSize: 12, whiteSpace: 'nowrap' }}>Min repetitions:</Text>
        <InputNumber
          size="small"
          min={2}
          max={10}
          value={minRepetitions}
          onChange={(v) => setMinRepetitions(v ?? 2)}
          style={{ width: 80 }}
        />
      </div>

      <Button
        type="primary"
        size="small"
        block
        onClick={handleApply}
        icon={<NodeIndexOutlined />}
      >
        Find Rework
      </Button>
    </Space>
  );
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
                color={filter.color || FILTER_COLORS[filter.type]}
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
