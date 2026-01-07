/**
 * Rework Filter Section
 *
 * Filter cases by rework/loop patterns
 */

import { useState, useCallback } from 'react';
import { Select, Button, Space, InputNumber, Typography } from 'antd';
import { NodeIndexOutlined } from '@ant-design/icons';
import { createLogger } from '../../../../shared/lib/logger';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type ReworkFilterSectionProps } from './types';

const log = createLogger('ReworkFilterSection');
const { Text } = Typography;

export function ReworkFilterSection({ activities, onApply }: ReworkFilterSectionProps) {
  const [activity, setActivity] = useState<string | null>(null);
  const [minRepetitions, setMinRepetitions] = useState<number>(2);

  const handleApply = useCallback(() => {
    const filter: AppliedFilter = {
      id: `rework-${Date.now()}`,
      type: 'rework',
      label: activity
        ? `Rework: ${activity} \u2265${minRepetitions}x`
        : `Any Rework \u2265${minRepetitions}x`,
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
