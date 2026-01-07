/**
 * Sequence Filter Section
 *
 * Filter cases by activity sequence (directly/eventually follows)
 */

import { useState, useCallback } from 'react';
import { Select, Button, Space, Radio } from 'antd';
import { FilterOutlined, SwapRightOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../../shared/lib/logger';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type SequenceFilterSectionProps } from './types';

const log = createLogger('SequenceFilterSection');

export function SequenceFilterSection({ activities, onApply }: SequenceFilterSectionProps) {
  const [sourceActivity, setSourceActivity] = useState<string | null>(null);
  const [targetActivity, setTargetActivity] = useState<string | null>(null);
  const [mode, setMode] = useState<'direct' | 'eventual'>('direct');

  const handleApply = useCallback(() => {
    if (!sourceActivity || !targetActivity) return;

    const filter: AppliedFilter = {
      id: `sequence-${mode}-${Date.now()}`,
      type: 'activitySequence',
      label: `${sourceActivity} ${mode === 'direct' ? '\u2192' : '\u2933'} ${targetActivity}`,
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
