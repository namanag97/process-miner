import React, { useState } from 'react';
import { Typography, Collapse, DatePicker, Select, Slider, Tag, Button, Space, Divider } from 'antd';
import { CloseOutlined, ClearOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';
import { MockFilterOptions } from '../mockExplorerData';

const log = createLogger('FilterPanel');
const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

export interface AppliedFilter {
  id: string;
  type: 'timeRange' | 'activity' | 'topK';
  label: string;
  value: any;
}

export interface FilterPanelProps {
  filterOptions: MockFilterOptions;
  appliedFilters: AppliedFilter[];
  onApplyFilter?: (filter: AppliedFilter) => void;
  onRemoveFilter?: (filterId: string) => void;
  onClearAllFilters?: () => void;
}

export function FilterPanel({
  filterOptions,
  appliedFilters,
  onApplyFilter,
  onRemoveFilter,
  onClearAllFilters,
}: FilterPanelProps) {
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null);
  const [selectedActivities, setSelectedActivities] = useState<string[]>([]);
  const [topK, setTopK] = useState<number>(80);

  log.debug('Rendering FilterPanel', { appliedCount: appliedFilters.length });

  const handleApplyTimeRange = () => {
    if (dateRange && dateRange[0] && dateRange[1]) {
      const filter: AppliedFilter = {
        id: `time-${Date.now()}`,
        type: 'timeRange',
        label: `${dateRange[0].format('MMM D')} – ${dateRange[1].format('MMM D, YYYY')}`,
        value: { start: dateRange[0].toISOString(), end: dateRange[1].toISOString() },
      };
      onApplyFilter?.(filter);
      log.info('Applied time range filter', filter);
      setDateRange(null);
    }
  };

  const handleApplyActivityFilter = () => {
    if (selectedActivities.length > 0) {
      const filter: AppliedFilter = {
        id: `activity-${Date.now()}`,
        type: 'activity',
        label: `Activities: ${selectedActivities.length} selected`,
        value: selectedActivities,
      };
      onApplyFilter?.(filter);
      log.info('Applied activity filter', filter);
      setSelectedActivities([]);
    }
  };

  const handleApplyTopK = () => {
    const filter: AppliedFilter = {
      id: `topk-${Date.now()}`,
      type: 'topK',
      label: `Top ${topK}% variants`,
      value: topK,
    };
    onApplyFilter?.(filter);
    log.info('Applied top-K filter', filter);
  };

  const collapseItems = [
    {
      key: 'time',
      label: 'Time Range',
      children: (
        <Space direction="vertical" style={{ width: '100%' }}>
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
            onClick={handleApplyTimeRange}
          >
            Apply
          </Button>
        </Space>
      ),
    },
    {
      key: 'activity',
      label: 'Activities',
      children: (
        <Space direction="vertical" style={{ width: '100%' }}>
          <Select
            mode="multiple"
            placeholder="Select activities to include"
            value={selectedActivities}
            onChange={setSelectedActivities}
            options={filterOptions.activities.map((a) => ({ label: a, value: a }))}
            style={{ width: '100%' }}
            size="small"
            maxTagCount={2}
          />
          <Button
            type="primary"
            size="small"
            block
            disabled={selectedActivities.length === 0}
            onClick={handleApplyActivityFilter}
          >
            Include selected
          </Button>
        </Space>
      ),
    },
    {
      key: 'variants',
      label: 'Top Variants',
      children: (
        <Space direction="vertical" style={{ width: '100%' }}>
          <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
            Show top {topK}% of variants by frequency
          </Text>
          <Slider
            value={topK}
            onChange={setTopK}
            min={10}
            max={100}
            step={5}
            marks={{ 10: '10%', 50: '50%', 80: '80%', 100: '100%' }}
          />
          <Button
            type="primary"
            size="small"
            block
            onClick={handleApplyTopK}
          >
            Apply
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: tokens.spacing[4], borderBottom: `1px solid ${tokens.colors.neutral[200]}` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
        <div style={{ padding: tokens.spacing[3], borderBottom: `1px solid ${tokens.colors.neutral[200]}` }}>
          <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block', marginBottom: tokens.spacing[2] }}>
            Applied ({appliedFilters.length})
          </Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
            {appliedFilters.map((filter) => (
              <Tag
                key={filter.id}
                closable
                onClose={() => onRemoveFilter?.(filter.id)}
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
          defaultActiveKey={['time', 'activity']}
          ghost
          expandIconPosition="end"
        />
      </div>
    </div>
  );
}

export default FilterPanel;
