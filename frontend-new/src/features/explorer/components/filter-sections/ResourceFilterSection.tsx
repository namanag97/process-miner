/**
 * Resource Filter Section
 *
 * Filter cases by resource/user involvement
 */

import { useState, useCallback } from 'react';
import { Select, Button, Space, Empty } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { createLogger } from '../../../../shared/lib/logger';
import type { AppliedFilter } from '../../types';
import { FILTER_COLORS, type ResourceFilterSectionProps } from './types';

const log = createLogger('ResourceFilterSection');

export function ResourceFilterSection({ resources, onApply }: ResourceFilterSectionProps) {
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
