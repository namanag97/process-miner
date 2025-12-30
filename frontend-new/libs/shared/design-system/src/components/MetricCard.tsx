import React from 'react';
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

/**
 * MetricCard - Compact stat card with trend indicators
 * Used for KPIs and statistics on dashboards
 */
export function MetricCard({
  title,
  value,
  prefix,
  suffix,
  trend,
  status = 'default',
  loading = false,
  onClick,
}: MetricCardProps) {
  return (
    <Card
      loading={loading}
      hoverable={!!onClick}
      onClick={onClick}
      style={{
        borderRadius: tokens.radius.lg,
        cursor: onClick ? 'pointer' : 'default',
      }}
      bodyStyle={{ padding: tokens.spacing[4] }}
    >
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Text
          style={{
            fontSize: tokens.fontSize.sm,
            color: tokens.colors.neutral[500],
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            fontWeight: tokens.fontWeight.medium,
          }}
        >
          {title}
        </Text>
        
        <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
          <span
            style={{
              fontSize: tokens.fontSize['3xl'],
              fontWeight: tokens.fontWeight.bold,
              color: statusColors[status],
              lineHeight: 1.2,
            }}
          >
            {prefix}
            {value}
            {suffix && (
              <span style={{ fontSize: tokens.fontSize.lg, marginLeft: 4 }}>
                {suffix}
              </span>
            )}
          </span>
          
          {trend && (
            <span
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                fontSize: tokens.fontSize.sm,
                color: trend.isPositive ? tokens.colors.success[500] : tokens.colors.error[500],
              }}
            >
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
}

export default MetricCard;
