/**
 * Time Range Filter Section
 *
 * Filter cases by time range with presets and custom date picker
 */

import { useState, useCallback } from 'react';
import { Button, Space, DatePicker } from 'antd';
import { FilterOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import { createLogger } from '../../../../shared/lib/logger';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type TimeRangeFilterSectionProps } from './types';

const log = createLogger('TimeRangeFilterSection');
const { RangePicker } = DatePicker;

type TimePreset = 'last7' | 'last30' | 'last90' | 'ytd';

export function TimeRangeFilterSection({ timeRange: _timeRange, onApply }: TimeRangeFilterSectionProps) {
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null);
  const [showCustom, setShowCustom] = useState(false);

  const handlePresetClick = useCallback((preset: TimePreset) => {
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
      label: `${dateRange[0].format('MMM D')} \u2013 ${dateRange[1].format('MMM D, YYYY')}`,
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
