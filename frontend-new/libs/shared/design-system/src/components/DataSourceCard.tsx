import React from 'react';
import { Card, Typography, Space, Button, Tag, Tooltip } from 'antd';
import {
  FileTextOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  EyeOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Text, Title } = Typography;

export interface DataSourceInfo {
  id: string;
  name: string;
  type: 'csv' | 'xes' | 'database' | 'api';
  caseCount?: number;
  eventCount?: number;
  uploadedAt?: string;
  status?: 'ready' | 'processing' | 'error';
}

export interface DataSourceCardProps {
  source: DataSourceInfo;
  onExplore?: () => void;
  onDelete?: () => void;
  loading?: boolean;
}

const typeIcons = {
  csv: <FileTextOutlined />,
  xes: <FileTextOutlined />,
  database: <DatabaseOutlined />,
  api: <DatabaseOutlined />,
};

const typeColors = {
  csv: 'blue',
  xes: 'purple',
  database: 'green',
  api: 'orange',
};

const statusColors = {
  ready: 'success',
  processing: 'processing',
  error: 'error',
};

/**
 * DataSourceCard - Display card for uploaded data sources
 * Shows file info, case/event counts, and action buttons
 */
export function DataSourceCard({
  source,
  onExplore,
  onDelete,
  loading = false,
}: DataSourceCardProps) {
  const formatNumber = (num?: number) => {
    if (num === undefined) return '-';
    return num.toLocaleString();
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  return (
    <Card
      loading={loading}
      style={{
        borderRadius: tokens.radius.lg,
        border: `1px solid ${tokens.colors.neutral[200]}`,
        transition: `all ${tokens.duration.moderate}ms ${tokens.easing.out}`,
      }}
      bodyStyle={{ padding: tokens.spacing[4] }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Space direction="vertical" size={8} style={{ flex: 1 }}>
          <Space size={12} align="center">
            <span style={{ fontSize: 20, color: tokens.colors.primary[500] }}>
              {typeIcons[source.type]}
            </span>
            <div>
              <Title level={5} style={{ margin: 0, fontSize: tokens.fontSize.base }}>
                {source.name}
              </Title>
              <Space size={8} style={{ marginTop: 4 }}>
                <Tag color={typeColors[source.type]}>{source.type.toUpperCase()}</Tag>
                {source.status && (
                  <Tag color={statusColors[source.status]}>
                    {source.status.charAt(0).toUpperCase() + source.status.slice(1)}
                  </Tag>
                )}
              </Space>
            </div>
          </Space>

          <Space size={16} style={{ marginTop: tokens.spacing[2] }}>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
              <strong>{formatNumber(source.caseCount)}</strong> cases
            </Text>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
              <strong>{formatNumber(source.eventCount)}</strong> events
            </Text>
            {source.uploadedAt && (
              <Tooltip title="Uploaded">
                <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                  <CalendarOutlined style={{ marginRight: 4 }} />
                  {formatDate(source.uploadedAt)}
                </Text>
              </Tooltip>
            )}
          </Space>
        </Space>

        <Space>
          {onExplore && source.status === 'ready' && (
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={onExplore}
            >
              Explore
            </Button>
          )}
          {onDelete && (
            <Tooltip title="Delete data source">
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                }}
              />
            </Tooltip>
          )}
        </Space>
      </div>
    </Card>
  );
}

export default DataSourceCard;
