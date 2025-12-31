import React, { memo, useMemo } from 'react';
import { Card, Statistic, Space, Typography } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { tokens } from '../theme';

const { Text } = Typography;

export interface MetricCardProps {
  title: string;
  value: string | number;
  prefix?: React.ReactNode;
  suffix?: string;
  trend?: {
    value: number;
    isPositive: boolean;
    label?: string;
  };
  status?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;
  onClick?: () => void;
}

const statusColors = {
  default: tokens.colors.neutral[800],
  success: tokens.colors.success[500],
  warning: tokens.colors.warning[500],
  error: tokens.colors.error[500],
};

// Static styles (extracted to avoid object recreation)
const titleStyle = {
  fontSize: tokens.fontSize.sm,
  color: tokens.colors.neutral[500],
  textTransform: 'uppercase' as const,
  letterSpacing: '0.05em',
  fontWeight: tokens.fontWeight.medium,
};

const valueContainerStyle = { display: 'flex', alignItems: 'baseline', gap: 8 };

const suffixStyle = { fontSize: tokens.fontSize.lg, marginLeft: 4 };

const getCardStyle = (hasOnClick: boolean) => ({
  borderRadius: tokens.radius.lg,
  cursor: hasOnClick ? 'pointer' : 'default',
});

const getValueStyle = (status: keyof typeof statusColors) => ({
  fontSize: tokens.fontSize['3xl'],
  fontWeight: tokens.fontWeight.bold,
  color: statusColors[status],
  lineHeight: 1.2,
});

const getTrendStyle = (isPositive: boolean) => ({
  display: 'flex' as const,
  alignItems: 'center' as const,
  gap: 4,
  fontSize: tokens.fontSize.sm,
  color: isPositive ? tokens.colors.success[500] : tokens.colors.error[500],
});

/**
 * MetricCard - Compact stat card with trend indicators
 * Used for KPIs and statistics on dashboards
 */
export const MetricCard = memo(function MetricCard({
  title,
  value,
  prefix,
  suffix,
  trend,
  status = 'default',
  loading = false,
  onClick,
}: MetricCardProps) {
  // Memoize dynamic styles
  const cardStyle = useMemo(() => getCardStyle(!!onClick), [onClick]);
  const valueStyle = useMemo(() => getValueStyle(status), [status]);
  const trendStyle = useMemo(
    () => trend ? getTrendStyle(trend.isPositive) : null,
    [trend?.isPositive]
  );

  return (
    <Card
      loading={loading}
      hoverable={!!onClick}
      onClick={onClick}
      className={onClick ? 'card-hover-lift' : ''}
      style={cardStyle}
      bodyStyle={{ padding: tokens.spacing[4] }}
    >
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Text style={titleStyle}>
          {title}
        </Text>
        
        <div style={valueContainerStyle}>
          <span style={valueStyle}>
            {prefix}
            {value}
            {suffix && (
              <span style={suffixStyle}>
                {suffix}
              </span>
            )}
          </span>
          
          {trend && trendStyle && (
            <span style={trendStyle}>
              {trend.isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              {Math.abs(trend.value).toFixed(1)}%
              {trend.label && (
                <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                  {trend.label}
                </Text>
              )}
            </span>
          )}
        </div>
      </Space>
    </Card>
  );
});

export default MetricCard;
