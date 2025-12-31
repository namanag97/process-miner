/**
 * Enhanced VariantPanel - Process Variant Explorer
 *
 * Features:
 * - Search/filter variants by activity
 * - Sort by frequency, duration, complexity
 * - Variant comparison mode
 * - Mini process map preview
 * - Conformance indicator
 * - Happy path highlighting
 */

import React, { useState, useMemo, useCallback } from 'react';
import {
  List,
  Typography,
  Tag,
  Progress,
  Space,
  Button,
  Tooltip,
  Input,
  Select,
  Segmented,
  Badge,
  Empty,
} from 'antd';
import {
  FilterOutlined,
  CheckCircleFilled,
  SearchOutlined,
  SortAscendingOutlined,
  SwapOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  BranchesOutlined,
  ExclamationCircleFilled,
  EyeOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';
import { formatDuration, formatNumber, COLORS } from '../utils/colorScales';
import type { ProcessedVariant } from '../types';

const log = createLogger('VariantPanel');
const { Text, Title } = Typography;

// =============================================================================
// TYPES
// =============================================================================

// Using ProcessedVariant from types, aliased as Variant for component compatibility
export type Variant = ProcessedVariant;

export type SortOption = 'frequency' | 'duration' | 'complexity' | 'activities';

export interface VariantPanelProps {
  variants: ProcessedVariant[];
  selectedVariantKey?: string | null;
  onSelectVariant?: (variantKey: string | null) => void;
  onFilterToVariant?: (variantKey: string) => void;
  onCompareVariants?: (variantKeys: string[]) => void;
  loading?: boolean;
}

// =============================================================================
// MINI PROCESS PATH COMPONENT
// =============================================================================

interface MiniProcessPathProps {
  activities: string[];
  maxVisible?: number;
  highlighted?: boolean;
}

function MiniProcessPath({ activities, maxVisible = 4, highlighted }: MiniProcessPathProps) {
  const visibleActivities = activities.slice(0, maxVisible);
  const remaining = activities.length - maxVisible;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        flexWrap: 'nowrap',
        overflow: 'hidden',
      }}
    >
      {visibleActivities.map((activity, index) => (
        <React.Fragment key={index}>
          <div
            style={{
              padding: '2px 6px',
              backgroundColor: highlighted ? tokens.colors.primary[50] : tokens.colors.neutral[100],
              borderRadius: 4,
              fontSize: 10,
              color: tokens.colors.neutral[700],
              whiteSpace: 'nowrap',
              maxWidth: 60,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
            title={activity}
          >
            {activity}
          </div>
          {index < visibleActivities.length - 1 && (
            <span style={{ color: tokens.colors.neutral[400], fontSize: 10 }}>→</span>
          )}
        </React.Fragment>
      ))}
      {remaining > 0 && (
        <Tooltip title={activities.slice(maxVisible).join(' → ')}>
          <span
            style={{
              fontSize: 10,
              color: tokens.colors.neutral[500],
              whiteSpace: 'nowrap',
            }}
          >
            +{remaining} more
          </span>
        </Tooltip>
      )}
    </div>
  );
}

// =============================================================================
// VARIANT CARD COMPONENT
// =============================================================================

interface VariantCardProps {
  variant: Variant;
  index: number;
  isSelected: boolean;
  isCompareMode: boolean;
  isComparing: boolean;
  onSelect: () => void;
  onFilter: () => void;
  onToggleCompare: () => void;
}

function VariantCard({
  variant,
  index,
  isSelected,
  isCompareMode,
  isComparing,
  onSelect,
  onFilter,
  onToggleCompare,
}: VariantCardProps) {
  return (
    <List.Item
      onClick={isCompareMode ? onToggleCompare : onSelect}
      style={{
        padding: tokens.spacing[3],
        cursor: 'pointer',
        backgroundColor: isSelected
          ? tokens.colors.primary[50]
          : isComparing
          ? tokens.colors.warning[50]
          : undefined,
        borderLeft: isSelected
          ? `3px solid ${tokens.colors.primary[500]}`
          : isComparing
          ? `3px solid ${tokens.colors.warning[500]}`
          : '3px solid transparent',
        transition: 'all 150ms ease',
      }}
    >
      <Space direction="vertical" size={8} style={{ width: '100%' }}>
        {/* Header Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space size={6}>
            {/* Rank Badge */}
            <Badge
              count={index + 1}
              style={{
                backgroundColor:
                  index === 0
                    ? tokens.colors.warning[500]
                    : index < 3
                    ? tokens.colors.neutral[400]
                    : tokens.colors.neutral[300],
              }}
            />

            {/* Happy Path */}
            {variant.isHappyPath && (
              <Tooltip title="Happy Path - Most common variant">
                <CheckCircleFilled style={{ color: COLORS.performance.good, fontSize: 14 }} />
              </Tooltip>
            )}

            {/* Rework Warning */}
            {variant.hasRework && (
              <Tooltip title="Contains rework loops">
                <ExclamationCircleFilled
                  style={{ color: COLORS.performance.moderate, fontSize: 14 }}
                />
              </Tooltip>
            )}

            {/* Case Count */}
            <Text strong style={{ fontSize: 13 }}>
              {formatNumber(variant.caseCount)} cases
            </Text>
          </Space>

          {/* Frequency Tag */}
          <Tag
            color={variant.frequencyPercent > 50 ? 'blue' : variant.frequencyPercent > 10 ? 'default' : 'default'}
            style={{ marginRight: 0 }}
          >
            {variant.frequencyPercent.toFixed(1)}%
          </Tag>
        </div>

        {/* Frequency Bar */}
        <Progress
          percent={variant.frequencyPercent}
          showInfo={false}
          size="small"
          strokeColor={
            variant.isHappyPath
              ? COLORS.performance.good
              : isSelected
              ? tokens.colors.primary[500]
              : tokens.colors.neutral[400]
          }
          trailColor={tokens.colors.neutral[200]}
        />

        {/* Mini Process Path */}
        <MiniProcessPath activities={variant.activities} highlighted={isSelected} />

        {/* Metrics Row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Space size={12}>
            {/* Duration */}
            <Tooltip title="Average duration">
              <Space size={4} style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>
                <ClockCircleOutlined />
                <span>{formatDuration(variant.avgDurationSeconds)}</span>
              </Space>
            </Tooltip>

            {/* Activity Count */}
            <Tooltip title="Number of activities">
              <Space size={4} style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>
                <BranchesOutlined />
                <span>{variant.activities.length}</span>
              </Space>
            </Tooltip>

            {/* Complexity Score */}
            {variant.complexityScore !== undefined && (
              <Tooltip title="Complexity score">
                <Space size={4} style={{ fontSize: 11, color: tokens.colors.neutral[500] }}>
                  <ThunderboltOutlined />
                  <span>{variant.complexityScore.toFixed(1)}</span>
                </Space>
              </Tooltip>
            )}
          </Space>

          {/* Actions */}
          {isSelected && !isCompareMode && (
            <Button
              type="link"
              size="small"
              icon={<FilterOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onFilter();
              }}
              style={{ padding: 0, height: 'auto', fontSize: 11 }}
            >
              Filter
            </Button>
          )}

          {isCompareMode && (
            <Button
              type={isComparing ? 'primary' : 'default'}
              size="small"
              icon={<EyeOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                onToggleCompare();
              }}
              style={{ fontSize: 10 }}
            >
              {isComparing ? 'Selected' : 'Compare'}
            </Button>
          )}
        </div>
      </Space>
    </List.Item>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function VariantPanel({
  variants,
  selectedVariantKey,
  onSelectVariant,
  onFilterToVariant,
  onCompareVariants,
  loading = false,
}: VariantPanelProps) {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('frequency');
  const [compareMode, setCompareMode] = useState(false);
  const [compareKeys, setCompareKeys] = useState<string[]>([]);

  log.debug('Rendering VariantPanel', {
    variantCount: variants.length,
    selected: selectedVariantKey,
    compareMode,
  });

  // Filter and sort variants
  const filteredVariants = useMemo(() => {
    let result = [...variants];

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter((v) =>
        v.activities.some((a) => a.toLowerCase().includes(query))
      );
    }

    // Sort
    result.sort((a, b) => {
      switch (sortBy) {
        case 'frequency':
          return b.caseCount - a.caseCount;
        case 'duration':
          return b.avgDurationSeconds - a.avgDurationSeconds;
        case 'complexity':
          return (b.complexityScore ?? 0) - (a.complexityScore ?? 0);
        case 'activities':
          return b.activities.length - a.activities.length;
        default:
          return 0;
      }
    });

    return result;
  }, [variants, searchQuery, sortBy]);

  // Handlers
  const handleSelectVariant = useCallback(
    (key: string) => {
      onSelectVariant?.(selectedVariantKey === key ? null : key);
    },
    [selectedVariantKey, onSelectVariant]
  );

  const handleFilterToVariant = useCallback(
    (key: string) => {
      onFilterToVariant?.(key);
      log.info('Filter to variant', { variantKey: key });
    },
    [onFilterToVariant]
  );

  const handleToggleCompare = useCallback((key: string) => {
    setCompareKeys((prev) => {
      if (prev.includes(key)) {
        return prev.filter((k) => k !== key);
      }
      if (prev.length >= 3) {
        // Max 3 variants for comparison
        return [...prev.slice(1), key];
      }
      return [...prev, key];
    });
  }, []);

  const handleCompare = useCallback(() => {
    if (compareKeys.length >= 2) {
      onCompareVariants?.(compareKeys);
    }
    setCompareMode(false);
    setCompareKeys([]);
  }, [compareKeys, onCompareVariants]);

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div
        style={{
          padding: tokens.spacing[4],
          borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <Title level={5} style={{ margin: 0 }}>
            Variants
          </Title>
          <Space size={4}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {filteredVariants.length} of {variants.length}
            </Text>
            <Tooltip title="Compare variants">
              <Button
                type={compareMode ? 'primary' : 'text'}
                size="small"
                icon={<SwapOutlined />}
                onClick={() => {
                  setCompareMode(!compareMode);
                  setCompareKeys([]);
                }}
              />
            </Tooltip>
          </Space>
        </div>

        {/* Search */}
        <Input
          placeholder="Search by activity..."
          prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          size="small"
          allowClear
          style={{ marginBottom: 8 }}
        />

        {/* Sort */}
        <Select
          value={sortBy}
          onChange={setSortBy}
          size="small"
          style={{ width: '100%' }}
          options={[
            { label: 'Sort by Frequency', value: 'frequency' },
            { label: 'Sort by Duration', value: 'duration' },
            { label: 'Sort by Complexity', value: 'complexity' },
            { label: 'Sort by Activities', value: 'activities' },
          ]}
          suffixIcon={<SortAscendingOutlined />}
        />
      </div>

      {/* Compare Mode Banner */}
      {compareMode && (
        <div
          style={{
            padding: `${tokens.spacing[2]} ${tokens.spacing[4]}`,
            backgroundColor: tokens.colors.warning[50],
            borderBottom: `1px solid ${tokens.colors.warning[500]}40`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Text style={{ fontSize: 12 }}>
            Select 2-3 variants to compare ({compareKeys.length} selected)
          </Text>
          <Space>
            <Button size="small" onClick={() => { setCompareMode(false); setCompareKeys([]); }}>
              Cancel
            </Button>
            <Button
              type="primary"
              size="small"
              disabled={compareKeys.length < 2}
              onClick={handleCompare}
            >
              Compare
            </Button>
          </Space>
        </div>
      )}

      {/* Variant List */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {filteredVariants.length === 0 ? (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={searchQuery ? 'No variants match your search' : 'No variants available'}
            style={{ marginTop: 48 }}
          />
        ) : (
          <List
            dataSource={filteredVariants}
            size="small"
            loading={loading}
            renderItem={(variant, index) => (
              <VariantCard
                key={variant.key}
                variant={variant}
                index={index}
                isSelected={variant.key === selectedVariantKey}
                isCompareMode={compareMode}
                isComparing={compareKeys.includes(variant.key)}
                onSelect={() => handleSelectVariant(variant.key)}
                onFilter={() => handleFilterToVariant(variant.key)}
                onToggleCompare={() => handleToggleCompare(variant.key)}
              />
            )}
          />
        )}
      </div>
    </div>
  );
}

export default VariantPanel;
