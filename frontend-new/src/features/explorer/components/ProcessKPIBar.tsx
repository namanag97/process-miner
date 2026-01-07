/**
 * ProcessKPIBar - Key Performance Indicators for Process Explorer
 *
 * Displays high-level process metrics in a compact card row:
 * - Total Cases
 * - Unique Variants
 * - Avg Throughput Time
 * - Happy Path %
 * - Automation Rate (if available)
 */

import React from 'react';
import { Card, Tag, Tooltip, Skeleton } from 'antd';
import {
  FileOutlined,
  BranchesOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
} from '@ant-design/icons';
import { tokens } from '@/src/shared/design-system';
import { formatDuration, formatNumber, COLORS } from '../utils/colorScales';
import type { ProcessKPIs } from '../types';

// =============================================================================
// TYPES
// =============================================================================

export interface KPITrend {
  direction: 'up' | 'down' | 'stable';
  percentChange: number;
}

export interface ProcessKPIBarProps {
  kpis: ProcessKPIs;
  trends?: Partial<Record<keyof ProcessKPIs, KPITrend>>;
  loading?: boolean;
  compact?: boolean;
}

// =============================================================================
// HELPER COMPONENTS
// =============================================================================

interface KPICardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  tooltip?: string;
  trend?: KPITrend;
  suffix?: string;
  color?: string;
  compact?: boolean;
}

function KPICard({
  title,
  value,
  icon,
  tooltip,
  trend,
  suffix,
  color,
  compact,
}: KPICardProps) {
  const content = (
    <Card
      size="small"
      style={{
        flex: 1,
        minWidth: compact ? 100 : 140,
        background: `linear-gradient(135deg, ${tokens.colors.neutral[0]} 0%, ${tokens.colors.neutral[50]} 100%)`,
        border: `1px solid ${tokens.colors.neutral[200]}`,
        borderRadius: tokens.radius.lg,
      }}
      styles={{
        body: {
          padding: compact ? '8px 12px' : '12px 16px',
        },
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
        <div
          style={{
            width: compact ? 28 : 36,
            height: compact ? 28 : 36,
            borderRadius: tokens.radius.md,
            backgroundColor: color ? `${color}15` : tokens.colors.primary[50],
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: color || tokens.colors.primary[500],
            fontSize: compact ? 14 : 16,
            flexShrink: 0,
          }}
        >
          {icon}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div
            style={{
              fontSize: 11,
              color: tokens.colors.neutral[500],
              marginBottom: 2,
              whiteSpace: 'nowrap',
            }}
          >
            {title}
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'baseline',
              gap: 4,
              flexWrap: 'wrap',
            }}
          >
            <span
              style={{
                fontSize: compact ? 16 : 20,
                fontWeight: 600,
                color: color || tokens.colors.neutral[900],
                lineHeight: 1.2,
              }}
            >
              {value}
            </span>
            {suffix && (
              <span
                style={{
                  fontSize: 11,
                  color: tokens.colors.neutral[500],
                }}
              >
                {suffix}
              </span>
            )}
            {trend && trend.percentChange !== 0 && (
              <Tag
                color={trend.direction === 'up' ? 'green' : 'red'}
                style={{
                  fontSize: 10,
                  padding: '0 4px',
                  margin: 0,
                  lineHeight: '16px',
                }}
              >
                {trend.direction === 'up' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                {Math.abs(trend.percentChange).toFixed(0)}%
              </Tag>
            )}
          </div>
        </div>
      </div>
    </Card>
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip} placement="bottom">
        {content}
      </Tooltip>
    );
  }

  return content;
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export function ProcessKPIBar({
  kpis,
  trends,
  loading = false,
  compact = false,
}: ProcessKPIBarProps) {
  // Show skeleton loader while loading
  if (loading) {
    return (
      <div
        style={{
          padding: compact ? '8px 16px' : '12px 24px',
          backgroundColor: tokens.colors.neutral[50],
          borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
        }}
      >
        <Skeleton.Input active block style={{ height: compact ? 48 : 64 }} />
      </div>
    );
  }

  // Defensive defaults for all KPI values
  const {
    totalCases = 0,
    uniqueVariants = 0,
    uniqueActivities = 0,
    avgThroughputTime,
    happyPathPercent,
    reworkRate,
  } = kpis;

  return (
    <div
      style={{
        display: 'flex',
        gap: compact ? 8 : 12,
        padding: compact ? '8px 16px' : '12px 24px',
        backgroundColor: tokens.colors.neutral[50],
        borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
        overflowX: 'auto',
        flexWrap: 'nowrap',
      }}
    >
      {/* Total Cases */}
      <KPICard
        title="Total Cases"
        value={formatNumber(totalCases)}
        icon={<FileOutlined />}
        tooltip="Total number of process instances"
        trend={trends?.totalCases}
        color={tokens.colors.primary[500]}
        compact={compact}
      />

      {/* Unique Variants */}
      <KPICard
        title="Variants"
        value={formatNumber(uniqueVariants)}
        icon={<BranchesOutlined />}
        tooltip="Number of unique process paths"
        trend={trends?.uniqueVariants}
        color="#8B5CF6"
        compact={compact}
      />

      {/* Activities */}
      <KPICard
        title="Activities"
        value={uniqueActivities}
        icon={<ThunderboltOutlined />}
        tooltip="Number of unique activities in the process"
        color="#0EA5E9"
        compact={compact}
      />

      {/* Avg Throughput Time */}
      {avgThroughputTime !== undefined && avgThroughputTime > 0 && (
        <KPICard
          title="Avg Duration"
          value={formatDuration(avgThroughputTime)}
          icon={<ClockCircleOutlined />}
          tooltip="Average case throughput time from start to end"
          trend={trends?.avgThroughputTime}
          color="#F59E0B"
          compact={compact}
        />
      )}

      {/* Happy Path % */}
      {happyPathPercent !== undefined && (
        <KPICard
          title="Happy Path"
          value={happyPathPercent.toFixed(0)}
          suffix="%"
          icon={<CheckCircleOutlined />}
          tooltip="Percentage of cases following the most common path"
          trend={trends?.happyPathPercent}
          color={happyPathPercent >= 70 ? COLORS.performance.good : happyPathPercent >= 40 ? COLORS.performance.moderate : COLORS.performance.poor}
          compact={compact}
        />
      )}

      {/* Rework Rate */}
      {reworkRate !== undefined && reworkRate > 0 && (
        <KPICard
          title="Rework Rate"
          value={reworkRate.toFixed(1)}
          suffix="%"
          icon={<ExclamationCircleOutlined />}
          tooltip="Percentage of cases with repeated activities"
          trend={trends?.reworkRate}
          color={reworkRate <= 10 ? COLORS.performance.good : reworkRate <= 25 ? COLORS.performance.moderate : COLORS.performance.poor}
          compact={compact}
        />
      )}
    </div>
  );
}

export default ProcessKPIBar;
