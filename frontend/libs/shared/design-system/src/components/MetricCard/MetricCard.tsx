import React from 'react';
import { Card, Statistic, Tag, Tooltip, Space, Spin } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { tokens } from '../../theme';

export interface MetricCardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: string;
  precision?: number;
  trend?: {
    value: number;
    label?: string;
    isPositiveGood?: boolean; // Default: true (increase = green)
  };
  status?: 'success' | 'warning' | 'error' | 'default';
  loading?: boolean;
  tooltip?: string;
  size?: 'small' | 'default' | 'large';
  className?: string;
  style?: React.CSSProperties;
}

const statusColors = {
  success: tokens.colorSuccess,
  warning: tokens.colorWarning,
  error: tokens.colorError,
  default: tokens.colorText,
};

/**
 * MetricCard - Compact metric display widget
 * 
 * Features:
 * - Trend indicator with percentage change
 * - Status-based coloring
 * - Tooltip for additional context
 * - Loading state
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  prefix,
  suffix,
  precision,
  trend,
  status = 'default',
  loading = false,
  tooltip,
  size = 'default',
  className,
  style,
}) => {
  const valueColor = statusColors[status];
  
  const valueFontSize = size === 'small' ? 20 : size === 'large' ? 32 : 24;
  const titleFontSize = size === 'small' ? 11 : 12;

  const renderTrend = () => {
    if (!trend) return null;
    
    const isPositive = trend.value >= 0;
    const isGood = trend.isPositiveGood !== false ? isPositive : !isPositive;

    return (
      <Tag
        color={isGood ? 'success' : 'error'}
        style={{
          marginLeft: 8,
          fontSize: 11,
          padding: '0 6px',
          lineHeight: '18px',
        }}
        icon={isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
      >
        {Math.abs(trend.value).toFixed(1)}%{trend.label ? ` ${trend.label}` : ''}
      </Tag>
    );
  };

  const cardContent = (
    <Card
      size="small"
      className={className}
      style={{
        ...style,
        borderRadius: 4,
      }}
      styles={{
        body: {
          padding: size === 'small' ? 12 : 16,
        },
      }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <Spin size="small" />
        </div>
      ) : (
        <>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: 8,
              color: tokens.colorTextSecondary,
              fontSize: titleFontSize,
            }}
          >
            <span>{title}</span>
            {tooltip && (
              <Tooltip title={tooltip}>
                <InfoCircleOutlined
                  style={{
                    marginLeft: 4,
                    fontSize: 12,
                    cursor: 'help',
                  }}
                />
              </Tooltip>
            )}
          </div>
          <Space align="baseline">
            <Statistic
              value={value}
              prefix={prefix}
              suffix={suffix}
              precision={precision}
              valueStyle={{
                color: valueColor,
                fontSize: valueFontSize,
                fontWeight: 600,
                lineHeight: 1,
              }}
            />
            {renderTrend()}
          </Space>
        </>
      )}
    </Card>
  );

  return cardContent;
};

export default MetricCard;
