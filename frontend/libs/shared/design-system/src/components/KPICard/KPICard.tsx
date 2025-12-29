import React from 'react';
import { Card, Progress, Space, Typography, Tooltip, Spin, Tag } from 'antd';
import {
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { tokens } from '../../theme';

const { Text, Title } = Typography;

export interface KPICardProps {
  title: string;
  value: number | string;
  target?: number;
  unit?: string;
  trend?: {
    value: number;
    label?: string;
    isPositiveGood?: boolean;
  };
  status?: 'success' | 'warning' | 'error' | 'default';
  icon?: React.ReactNode;
  chart?: React.ReactNode; // Sparkline or mini chart
  breakdown?: Array<{
    label: string;
    value: number | string;
    color?: string;
  }>;
  loading?: boolean;
  tooltip?: string;
  onClick?: () => void;
}

const statusColors = {
  success: tokens.colorSuccess,
  warning: tokens.colorWarning,
  error: tokens.colorError,
  default: tokens.colorPrimary,
};

/**
 * KPICard - Full-featured KPI display widget
 * 
 * Features:
 * - Target progress indicator
 * - Trend with percentage change
 * - Mini chart/sparkline slot
 * - Breakdown details
 * - Click handler for drill-down
 */
export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  target,
  unit,
  trend,
  status = 'default',
  icon,
  chart,
  breakdown,
  loading = false,
  tooltip,
  onClick,
}) => {
  const statusColor = statusColors[status];
  
  const progressPercent = target ? (Number(value) / target) * 100 : undefined;
  const progressStatus = progressPercent
    ? progressPercent >= 100
      ? 'success'
      : progressPercent >= 75
        ? 'normal'
        : 'exception'
    : undefined;

  const renderTrend = () => {
    if (!trend) return null;
    
    const isPositive = trend.value >= 0;
    const isGood = trend.isPositiveGood !== false ? isPositive : !isPositive;

    return (
      <Tag
        color={isGood ? 'success' : 'error'}
        style={{ marginLeft: 8, fontSize: 11 }}
        icon={isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
      >
        {Math.abs(trend.value).toFixed(1)}%{trend.label ? ` ${trend.label}` : ''}
      </Tag>
    );
  };

  const renderBreakdown = () => {
    if (!breakdown?.length) return null;

    return (
      <div style={{ marginTop: 12, borderTop: `1px solid ${tokens.colorBorderSecondary}`, paddingTop: 12 }}>
        <Space direction="vertical" size={4} style={{ width: '100%' }}>
          {breakdown.map((item, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Space size={4}>
                {item.color && (
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: 2,
                      background: item.color,
                      display: 'inline-block',
                    }}
                  />
                )}
                <Text style={{ fontSize: 12, color: tokens.colorTextSecondary }}>
                  {item.label}
                </Text>
              </Space>
              <Text strong style={{ fontSize: 12 }}>
                {item.value}
              </Text>
            </div>
          ))}
        </Space>
      </div>
    );
  };

  return (
    <Card
      size="small"
      hoverable={!!onClick}
      onClick={onClick}
      style={{
        borderRadius: 4,
        cursor: onClick ? 'pointer' : 'default',
        height: '100%',
      }}
      styles={{
        body: { padding: 16 },
      }}
    >
      {loading ? (
        <div style={{ textAlign: 'center', padding: '32px 0' }}>
          <Spin />
        </div>
      ) : (
        <>
          {/* Header */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: 12,
            }}
          >
            <Space size={8}>
              {icon && (
                <span style={{ color: statusColor, fontSize: 16 }}>{icon}</span>
              )}
              <Text
                style={{
                  fontSize: 12,
                  color: tokens.colorTextSecondary,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}
              >
                {title}
              </Text>
            </Space>
            {tooltip && (
              <Tooltip title={tooltip}>
                <InfoCircleOutlined
                  style={{ color: tokens.colorTextTertiary, cursor: 'help' }}
                />
              </Tooltip>
            )}
          </div>

          {/* Value */}
          <div style={{ display: 'flex', alignItems: 'baseline', flexWrap: 'wrap' }}>
            <Title
              level={3}
              style={{
                margin: 0,
                color: statusColor,
                fontWeight: 600,
              }}
            >
              {value}
              {unit && (
                <Text
                  style={{
                    fontSize: 14,
                    color: tokens.colorTextSecondary,
                    marginLeft: 4,
                    fontWeight: 400,
                  }}
                >
                  {unit}
                </Text>
              )}
            </Title>
            {renderTrend()}
          </div>

          {/* Target progress */}
          {target !== undefined && (
            <div style={{ marginTop: 12 }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginBottom: 4,
                }}
              >
                <Text style={{ fontSize: 11, color: tokens.colorTextTertiary }}>
                  Target
                </Text>
                <Text style={{ fontSize: 11, color: tokens.colorTextSecondary }}>
                  {target}
                  {unit && ` ${unit}`}
                </Text>
              </div>
              <Progress
                percent={Math.min(progressPercent || 0, 100)}
                status={progressStatus}
                size="small"
                showInfo={false}
              />
            </div>
          )}

          {/* Chart slot */}
          {chart && <div style={{ marginTop: 12 }}>{chart}</div>}

          {/* Breakdown */}
          {renderBreakdown()}
        </>
      )}
    </Card>
  );
};

export default KPICard;
