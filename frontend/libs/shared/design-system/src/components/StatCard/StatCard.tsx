import React from 'react';
import { Space, Tooltip, Typography } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
} from '@ant-design/icons';
import { tokens } from '../../theme';

const { Text } = Typography;

export interface StatCardProps {
  label: string;
  value: number | string;
  suffix?: string;
  trend?: number; // Percentage change
  trendLabel?: string;
  icon?: React.ReactNode;
  tooltip?: string;
  inline?: boolean;
  size?: 'small' | 'default';
}

/**
 * StatCard - Compact inline statistic display
 * 
 * Useful for:
 * - Header stats row
 * - Inline metrics in tables
 * - Secondary statistics
 */
export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  suffix,
  trend,
  trendLabel,
  icon,
  tooltip,
  inline = false,
  size = 'default',
}) => {
  const renderTrend = () => {
    if (trend === undefined) return null;
    
    const isPositive = trend > 0;
    const isNeutral = trend === 0;
    const color = isNeutral
      ? tokens.colorTextTertiary
      : isPositive
        ? tokens.colorSuccess
        : tokens.colorError;

    const TrendIcon = isNeutral
      ? MinusOutlined
      : isPositive
        ? ArrowUpOutlined
        : ArrowDownOutlined;

    return (
      <Text
        style={{
          color,
          fontSize: size === 'small' ? 10 : 11,
          fontWeight: 500,
        }}
      >
        <TrendIcon style={{ fontSize: 10 }} />
        {' '}
        {Math.abs(trend).toFixed(1)}%
        {trendLabel && ` ${trendLabel}`}
      </Text>
    );
  };

  const content = (
    <div
      style={{
        display: inline ? 'inline-flex' : 'flex',
        flexDirection: inline ? 'row' : 'column',
        alignItems: inline ? 'center' : 'flex-start',
        gap: inline ? 8 : 4,
        padding: size === 'small' ? '4px 8px' : '8px 12px',
        background: tokens.colorBgSpotlight,
        borderRadius: 4,
        border: `1px solid ${tokens.colorBorderSecondary}`,
      }}
    >
      {icon && (
        <span style={{ color: tokens.colorTextSecondary, fontSize: 14 }}>
          {icon}
        </span>
      )}
      <Space direction={inline ? 'horizontal' : 'vertical'} size={2}>
        <Text
          style={{
            fontSize: size === 'small' ? 10 : 11,
            color: tokens.colorTextTertiary,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
          }}
        >
          {label}
        </Text>
        <Space size={4} align="baseline">
          <Text
            strong
            style={{
              fontSize: size === 'small' ? 14 : 16,
              color: tokens.colorText,
            }}
          >
            {value}
            {suffix && (
              <Text
                style={{
                  fontSize: size === 'small' ? 10 : 11,
                  color: tokens.colorTextSecondary,
                  marginLeft: 2,
                }}
              >
                {suffix}
              </Text>
            )}
          </Text>
          {renderTrend()}
        </Space>
      </Space>
    </div>
  );

  return tooltip ? (
    <Tooltip title={tooltip}>{content}</Tooltip>
  ) : (
    content
  );
};

export default StatCard;
