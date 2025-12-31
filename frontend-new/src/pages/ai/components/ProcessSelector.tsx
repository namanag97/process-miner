import React from 'react';
import { Select, Space, Typography, Tag, Skeleton } from 'antd';
import { DatabaseOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';

const { Text } = Typography;

export interface ProcessOption {
  id: string;
  name: string;
  totalCases: number;
  totalActivities: number;
  sourceFormat: string;
}

interface ProcessSelectorProps {
  processes: ProcessOption[];
  selectedId: string | null;
  onSelect: (processId: string) => void;
  loading?: boolean;
  disabled?: boolean;
}

export function ProcessSelector({
  processes,
  selectedId,
  onSelect,
  loading = false,
  disabled = false,
}: ProcessSelectorProps) {
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <DatabaseOutlined style={{ color: tokens.colors.neutral[400] }} />
        <Skeleton.Input active style={{ width: 240 }} />
      </div>
    );
  }

  return (
    <Space>
      <DatabaseOutlined style={{ color: tokens.colors.primary[500] }} />
      <Text type="secondary">Process:</Text>
      <Select
        value={selectedId || undefined}
        onChange={onSelect}
        placeholder="Select a process to analyze"
        style={{ minWidth: 280 }}
        disabled={disabled}
        showSearch
        optionFilterProp="label"
        options={processes.map((p) => ({
          value: p.id,
          label: p.name,
          data: p,
        }))}
        optionRender={(option) => {
          const process = option.data?.data as ProcessOption;
          return (
            <Space direction="vertical" size={0} style={{ padding: '4px 0' }}>
              <Text strong>{process?.name}</Text>
              <Space size={8}>
                <Tag color="blue" style={{ margin: 0 }}>
                  {process?.totalCases?.toLocaleString()} cases
                </Tag>
                <Tag color="green" style={{ margin: 0 }}>
                  {process?.totalActivities} activities
                </Tag>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {process?.sourceFormat?.toUpperCase()}
                </Text>
              </Space>
            </Space>
          );
        }}
      />
    </Space>
  );
}

export default ProcessSelector;
