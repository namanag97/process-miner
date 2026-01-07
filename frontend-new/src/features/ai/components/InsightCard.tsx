import React from 'react';
import { Card, Space, Typography, Tag } from 'antd';
import {
  ThunderboltOutlined,
  NodeIndexOutlined,
  WarningOutlined,
  BulbOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import { tokens } from '@/src/shared/design-system';
import type { ProcessInsight } from '../types';

const { Text, Paragraph } = Typography;

interface InsightCardProps {
  insight: ProcessInsight;
  compact?: boolean;
}

const iconMap: Record<string, React.ReactNode> = {
  bottleneck: <ThunderboltOutlined />,
  pattern: <NodeIndexOutlined />,
  anomaly: <WarningOutlined />,
  recommendation: <BulbOutlined />,
  metric: <BarChartOutlined />,
};

const severityColors: Record<string, string> = {
  high: tokens.colors.error[500],
  medium: tokens.colors.warning[500],
  low: tokens.colors.success[500],
  info: tokens.colors.primary[500],
};

const severityBgColors: Record<string, string> = {
  high: tokens.colors.error[50],
  medium: tokens.colors.warning[50],
  low: tokens.colors.success[50],
  info: tokens.colors.primary[50],
};

export function InsightCard({ insight, compact = false }: InsightCardProps) {
  const icon = iconMap[insight.type] || <BulbOutlined />;
  const color = severityColors[insight.severity || 'info'];
  const bgColor = severityBgColors[insight.severity || 'info'];

  if (compact) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '8px 12px',
          borderRadius: 8,
          backgroundColor: bgColor,
          border: `1px solid ${color}20`,
        }}
      >
        <span style={{ color, fontSize: 16 }}>{icon}</span>
        <Text strong style={{ flex: 1 }}>
          {insight.title}
        </Text>
        {insight.severity && (
          <Tag
            color={
              insight.severity === 'high'
                ? 'error'
                : insight.severity === 'medium'
                ? 'warning'
                : insight.severity === 'low'
                ? 'success'
                : 'blue'
            }
            style={{ margin: 0 }}
          >
            {insight.severity}
          </Tag>
        )}
      </div>
    );
  }

  return (
    <Card
      size="small"
      style={{
        marginBottom: 12,
        borderLeft: `4px solid ${color}`,
        background: `linear-gradient(135deg, ${bgColor}, white)`,
        borderRadius: 12,
        overflow: 'hidden',
        transition: 'transform 0.2s, box-shadow 0.2s',
      }}
      hoverable
    >
      <Space direction="vertical" size={8} style={{ width: '100%' }}>
        <Space>
          <span
            style={{
              color,
              fontSize: 18,
              width: 32,
              height: 32,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 8,
              backgroundColor: `${color}15`,
            }}
          >
            {icon}
          </span>
          <div>
            <Text strong>{insight.title}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: 12 }}>
              {insight.type.charAt(0).toUpperCase() + insight.type.slice(1)}
            </Text>
          </div>
          {insight.severity && (
            <Tag
              color={
                insight.severity === 'high'
                  ? 'error'
                  : insight.severity === 'medium'
                  ? 'warning'
                  : insight.severity === 'low'
                  ? 'success'
                  : 'blue'
              }
            >
              {insight.severity}
            </Tag>
          )}
        </Space>
        <Paragraph
          style={{ margin: 0, color: tokens.colors.neutral[600] }}
          ellipsis={{ rows: 2, expandable: true }}
        >
          {insight.description}
        </Paragraph>
      </Space>
    </Card>
  );
}

export default InsightCard;
