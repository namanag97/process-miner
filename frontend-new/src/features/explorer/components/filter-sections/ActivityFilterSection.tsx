/**
 * Activity Filter Section
 *
 * Filter cases by activity occurrence (with/without specific activities)
 */

import { useState, useCallback } from 'react';
import { Select, Button, Space, Radio } from 'antd';
import { FilterOutlined } from '@ant-design/icons';
import { createLogger } from '../../../../shared/lib/logger';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type ActivityFilterSectionProps } from './types';

const log = createLogger('ActivityFilterSection');

export function ActivityFilterSection({ activities, onApply }: ActivityFilterSectionProps) {
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
