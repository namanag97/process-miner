/**
 * FilterPresetManager - Reusable filter selection and persistence component
 *
 * Provides a standardized interface for:
 * - Selecting and applying filters
 * - Saving filter presets
 * - Loading saved presets
 * - Resetting to defaults
 *
 * @example
 * <FilterPresetManager
 *   filters={currentFilters}
 *   onChange={setFilters}
 *   presets={savedPresets}
 *   onSavePreset={handleSave}
 * />
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Button,
  Dropdown,
  Space,
  Input,
  Tag,
  Popover,
  Form,
  Divider,
  Typography,
  Empty,
  message,
} from 'antd';
import {
  FilterOutlined,
  SaveOutlined,
  ReloadOutlined,
  DownOutlined,
  DeleteOutlined,
  StarOutlined,
  StarFilled,
  PlusOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export interface FilterValue {
  key: string;
  label: string;
  value: any;
  operator?: 'equals' | 'contains' | 'gt' | 'lt' | 'between' | 'in';
}

export interface FilterPreset {
  id: string;
  name: string;
  filters: FilterValue[];
  isDefault?: boolean;
  createdAt?: Date;
}

export interface FilterPresetManagerProps {
  /** Currently active filters */
  filters: FilterValue[];
  /** Filter change handler */
  onChange: (filters: FilterValue[]) => void;
  /** Available filter presets */
  presets?: FilterPreset[];
  /** Save preset handler */
  onSavePreset?: (preset: Omit<FilterPreset, 'id' | 'createdAt'>) => void;
  /** Delete preset handler */
  onDeletePreset?: (presetId: string) => void;
  /** Set default preset handler */
  onSetDefault?: (presetId: string) => void;
  /** Available filter fields for the dropdown */
  availableFilters?: Array<{
    key: string;
    label: string;
    type: 'text' | 'number' | 'date' | 'select';
    options?: Array<{ label: string; value: any }>;
  }>;
  /** Whether to show the save preset button */
  showSavePreset?: boolean;
  /** Compact mode */
  compact?: boolean;
}

// ============================================
// FilterPresetManager Component
// ============================================

export function FilterPresetManager({
  filters,
  onChange,
  presets = [],
  onSavePreset,
  onDeletePreset,
  onSetDefault,
  availableFilters = [],
  showSavePreset = true,
  compact = false,
}: FilterPresetManagerProps) {
  const [savePopoverOpen, setSavePopoverOpen] = useState(false);
  const [presetName, setPresetName] = useState('');

  const activeFilterCount = filters.length;
  const defaultPreset = presets.find((p) => p.isDefault);

  // Remove a single filter
  const handleRemoveFilter = useCallback(
    (key: string) => {
      onChange(filters.filter((f) => f.key !== key));
    },
    [filters, onChange]
  );

  // Clear all filters
  const handleClearAll = useCallback(() => {
    onChange([]);
  }, [onChange]);

  // Apply a preset
  const handleApplyPreset = useCallback(
    (preset: FilterPreset) => {
      onChange(preset.filters);
      message.success(`Applied preset: ${preset.name}`);
    },
    [onChange]
  );

  // Save current filters as preset
  const handleSavePreset = useCallback(() => {
    if (!presetName.trim()) {
      message.error('Please enter a preset name');
      return;
    }
    if (filters.length === 0) {
      message.error('No filters to save');
      return;
    }
    onSavePreset?.({ name: presetName.trim(), filters });
    setPresetName('');
    setSavePopoverOpen(false);
    message.success(`Preset "${presetName}" saved`);
  }, [presetName, filters, onSavePreset]);

  // Reset to default preset
  const handleResetToDefault = useCallback(() => {
    if (defaultPreset) {
      onChange(defaultPreset.filters);
      message.info('Reset to default filters');
    } else {
      onChange([]);
      message.info('Cleared all filters');
    }
  }, [defaultPreset, onChange]);

  // Preset dropdown menu items - memoized to prevent recreation on every render
  const presetMenuItems = useMemo(() => [
    ...(presets.length > 0
      ? presets.map((preset) => ({
          key: preset.id,
          label: (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', minWidth: 180 }}>
              <span>
                {preset.isDefault && <StarFilled style={{ color: tokens.colors.warning[500], marginRight: 6 }} />}
                {preset.name}
              </span>
              <Space size={4}>
                {onSetDefault && !preset.isDefault && (
                  <Button
                    type="text"
                    size="small"
                    icon={<StarOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      onSetDefault(preset.id);
                    }}
                  />
                )}
                {onDeletePreset && (
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeletePreset(preset.id);
                    }}
                  />
                )}
              </Space>
            </div>
          ),
          onClick: () => handleApplyPreset(preset),
        }))
      : [{ key: 'empty', label: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No saved presets" />, disabled: true }]),
  ], [presets, onSetDefault, onDeletePreset, handleApplyPreset]);

  // Save preset popover content
  const savePopoverContent = (
    <div style={{ width: 240 }}>
      <Form layout="vertical" size="small">
        <Form.Item label="Preset Name" style={{ marginBottom: tokens.spacing[3] }}>
          <Input
            placeholder="e.g., High Priority Cases"
            value={presetName}
            onChange={(e) => setPresetName(e.target.value)}
            onPressEnter={handleSavePreset}
          />
        </Form.Item>
        <Form.Item style={{ marginBottom: 0 }}>
          <Button type="primary" block icon={<SaveOutlined />} onClick={handleSavePreset}>
            Save Preset
          </Button>
        </Form.Item>
      </Form>
    </div>
  );

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: tokens.spacing[3],
        flexWrap: 'wrap',
      }}
    >
      {/* Presets Dropdown */}
      <Dropdown menu={{ items: presetMenuItems }} trigger={['click']}>
        <Button icon={<FilterOutlined />}>
          Presets {presets.length > 0 && `(${presets.length})`} <DownOutlined />
        </Button>
      </Dropdown>

      {/* Active Filter Tags */}
      {filters.length > 0 && (
        <>
          <Divider type="vertical" style={{ height: 24 }} />
          <Space size={[4, 4]} wrap>
            {filters.map((filter) => (
              <Tag
                key={filter.key}
                closable
                onClose={() => handleRemoveFilter(filter.key)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  backgroundColor: tokens.colors.primary[50],
                  borderColor: tokens.colors.primary[200],
                  color: tokens.colors.primary[700],
                }}
              >
                <Text strong style={{ fontSize: tokens.fontSize.xs, marginRight: 4 }}>
                  {filter.label}:
                </Text>
                <Text style={{ fontSize: tokens.fontSize.xs }}>{String(filter.value)}</Text>
              </Tag>
            ))}
          </Space>
        </>
      )}

      {/* Action Buttons */}
      <div style={{ marginLeft: 'auto', display: 'flex', gap: tokens.spacing[2] }}>
        {/* Save Preset */}
        {showSavePreset && onSavePreset && filters.length > 0 && (
          <Popover
            content={savePopoverContent}
            title="Save Filter Preset"
            trigger="click"
            open={savePopoverOpen}
            onOpenChange={setSavePopoverOpen}
            placement="bottomRight"
          >
            <Button icon={<SaveOutlined />} size={compact ? 'small' : 'middle'}>
              Save
            </Button>
          </Popover>
        )}

        {/* Reset */}
        {filters.length > 0 && (
          <Button icon={<ReloadOutlined />} onClick={handleResetToDefault} size={compact ? 'small' : 'middle'}>
            Reset
          </Button>
        )}
      </div>
    </div>
  );
}

export default FilterPresetManager;
