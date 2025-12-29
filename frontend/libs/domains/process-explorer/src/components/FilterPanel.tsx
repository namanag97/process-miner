import React, { useState, useEffect } from 'react';
import {
  Card,
  Checkbox,
  DatePicker,
  Slider,
  Typography,
  Space,
  Button,
  Collapse,
  Tag,
  Input,
  Spin,
  Empty,
  Alert,
} from 'antd';
import {
  FilterOutlined,
  ClearOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import { useFilterOptions } from '../hooks';

const { Text, Title } = Typography;
const { RangePicker } = DatePicker;
const { Panel } = Collapse;
const { Search } = Input;

export interface FilterState {
  activities: string[];
  timeRange: [Dayjs, Dayjs] | null;
  variants: string[];
  durationRange: [number, number] | null;
}

interface FilterPanelProps {
  logId: string;
  value?: FilterState;
  onChange?: (filters: FilterState) => void;
  onApply?: (filters: FilterState) => void;
  collapsed?: boolean;
}

const initialFilters: FilterState = {
  activities: [],
  timeRange: null,
  variants: [],
  durationRange: null,
};

export const FilterPanel: React.FC<FilterPanelProps> = ({
  logId,
  value,
  onChange,
  onApply,
  collapsed = false,
}) => {
  const { data: options, isLoading, error } = useFilterOptions(logId);
  const [filters, setFilters] = useState<FilterState>(value || initialFilters);
  const [activitySearch, setActivitySearch] = useState('');

  // Sync with external value
  useEffect(() => {
    if (value) {
      setFilters(value);
    }
  }, [value]);

  const updateFilters = (update: Partial<FilterState>) => {
    const newFilters = { ...filters, ...update };
    setFilters(newFilters);
    onChange?.(newFilters);
  };

  const clearFilters = () => {
    const cleared = { ...initialFilters };
    setFilters(cleared);
    onChange?.(cleared);
  };

  const handleApply = () => {
    onApply?.(filters);
  };

  const hasFilters =
    filters.activities.length > 0 ||
    filters.timeRange !== null ||
    filters.variants.length > 0 ||
    filters.durationRange !== null;

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load filter options"
        size="small"
      />
    );
  }

  if (isLoading) {
    return (
      <Card size="small" style={{ width: 280 }}>
        <Spin size="small" />
      </Card>
    );
  }

  if (!options) {
    return (
      <Card size="small" style={{ width: 280 }}>
        <Empty description="No filter options available" />
      </Card>
    );
  }

  const filteredActivities = options.activities.filter((a) =>
    a.toLowerCase().includes(activitySearch.toLowerCase())
  );

  const panelItems = [
    {
      key: 'activities',
      label: (
        <Space>
          <span>Activities</span>
          {filters.activities.length > 0 && (
            <Tag size="small" color="blue">
              {filters.activities.length}
            </Tag>
          )}
        </Space>
      ),
      children: (
        <div>
          <Search
            placeholder="Search activities..."
            size="small"
            value={activitySearch}
            onChange={(e) => setActivitySearch(e.target.value)}
            style={{ marginBottom: 8 }}
            allowClear
          />
          <div style={{ maxHeight: 200, overflowY: 'auto' }}>
            <Checkbox.Group
              value={filters.activities}
              onChange={(checked) =>
                updateFilters({ activities: checked as string[] })
              }
              style={{ display: 'flex', flexDirection: 'column', gap: 4 }}
            >
              {filteredActivities.map((activity) => (
                <Checkbox key={activity} value={activity}>
                  <Text
                    ellipsis
                    style={{ maxWidth: 180 }}
                    title={activity}
                  >
                    {activity}
                  </Text>
                </Checkbox>
              ))}
            </Checkbox.Group>
          </div>
          {filteredActivities.length === 0 && (
            <Text type="secondary" style={{ fontSize: 12 }}>
              No activities match your search
            </Text>
          )}
        </div>
      ),
    },
    {
      key: 'timeRange',
      label: (
        <Space>
          <span>Time Range</span>
          {filters.timeRange && (
            <Tag size="small" color="blue">1</Tag>
          )}
        </Space>
      ),
      children: (
        <div>
          <RangePicker
            size="small"
            style={{ width: '100%' }}
            value={filters.timeRange}
            onChange={(dates) =>
              updateFilters({ timeRange: dates as [Dayjs, Dayjs] | null })
            }
            format="YYYY-MM-DD"
          />
          {options.time_range && (
            <Text type="secondary" style={{ fontSize: 11, display: 'block', marginTop: 4 }}>
              Available: {dayjs(options.time_range.start).format('MMM D, YYYY')} -{' '}
              {dayjs(options.time_range.end).format('MMM D, YYYY')}
            </Text>
          )}
        </div>
      ),
    },
    {
      key: 'variants',
      label: (
        <Space>
          <span>Variants</span>
          {filters.variants.length > 0 && (
            <Tag size="small" color="blue">
              {filters.variants.length}
            </Tag>
          )}
        </Space>
      ),
      children: (
        <div style={{ maxHeight: 150, overflowY: 'auto' }}>
          <Checkbox.Group
            value={filters.variants}
            onChange={(checked) =>
              updateFilters({ variants: checked as string[] })
            }
            style={{ display: 'flex', flexDirection: 'column', gap: 4 }}
          >
            {options.variants.slice(0, 20).map((v, i) => (
              <Checkbox key={v.variant} value={v.variant}>
                <Text
                  ellipsis
                  style={{ maxWidth: 160 }}
                  title={v.variant}
                >
                  Variant {i + 1} ({v.count})
                </Text>
              </Checkbox>
            ))}
          </Checkbox.Group>
          {options.variants.length > 20 && (
            <Text type="secondary" style={{ fontSize: 11 }}>
              +{options.variants.length - 20} more variants
            </Text>
          )}
        </div>
      ),
    },
    {
      key: 'duration',
      label: (
        <Space>
          <span>Case Duration</span>
          {filters.durationRange && (
            <Tag size="small" color="blue">1</Tag>
          )}
        </Space>
      ),
      children: (
        <div>
          <Slider
            range
            min={options.case_duration.min}
            max={options.case_duration.max}
            value={filters.durationRange || [options.case_duration.min, options.case_duration.max]}
            onChange={(value) =>
              updateFilters({ durationRange: value as [number, number] })
            }
            tooltip={{
              formatter: (value) => formatDuration(value || 0),
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {formatDuration(options.case_duration.min)}
            </Text>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {formatDuration(options.case_duration.max)}
            </Text>
          </div>
        </div>
      ),
    },
  ];

  return (
    <Card
      size="small"
      style={{ width: 280 }}
      title={
        <Space>
          <FilterOutlined />
          <span>Filters</span>
        </Space>
      }
      extra={
        hasFilters && (
          <Button
            type="text"
            size="small"
            icon={<ClearOutlined />}
            onClick={clearFilters}
          >
            Clear
          </Button>
        )
      }
    >
      <Collapse
        size="small"
        defaultActiveKey={collapsed ? [] : ['activities']}
        ghost
        items={panelItems}
      />

      {onApply && (
        <Button
          type="primary"
          block
          size="small"
          onClick={handleApply}
          disabled={!hasFilters}
          style={{ marginTop: 16 }}
        >
          Apply Filters
        </Button>
      )}
    </Card>
  );
};

// Helper function to format duration in seconds to human-readable
function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  if (seconds < 86400) return `${Math.round(seconds / 3600)}h`;
  return `${Math.round(seconds / 86400)}d`;
}
