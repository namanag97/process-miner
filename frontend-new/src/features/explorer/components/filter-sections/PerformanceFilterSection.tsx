/**
 * Performance Filter Section
 *
 * Filter cases by duration/performance metrics
 */

import { useState, useCallback } from 'react';
import { Button, Space, Radio, InputNumber, Typography } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../../shared/lib/logger';
import { formatDuration } from '../../utils/colorScales';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type PerformanceFilterSectionProps } from './types';

const log = createLogger('PerformanceFilterSection');
const { Text } = Typography;

export function PerformanceFilterSection({ caseDuration, onApply }: PerformanceFilterSectionProps) {
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
