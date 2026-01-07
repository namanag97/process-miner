/**
 * DataSourcesList - Display and manage data sources for a project
 * 
 * Shows dataset status and provides Analyze action for UNSTRUCTURED datasets.
 */

import React from 'react';
import { List, Card, Space, Tag, Button, Typography, Tooltip } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { EmptyState, tokens } from '@/src/shared/design-system';
import {
  FolderOpenOutlined,
  FileTextOutlined,
  PlayCircleOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  SettingOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { useRemoveFileFromProject } from '../hooks';
import type { DataSourceInfo, DatasetStatus } from '../types';

const { Text } = Typography;

interface DataSourcesListProps {
  sources: DataSourceInfo[];
  loading?: boolean;
  onUploadClick?: () => void;
  onAnalyzeClick?: (source: DataSourceInfo) => void;
}

const STATUS_CONFIG: Record<DatasetStatus, { color: string; icon: React.ReactNode; label: string }> = {
  unstructured: {
    color: 'orange',
    icon: <SettingOutlined />,
    label: 'Needs Configuration'
  },
  analyzing: {
    color: 'processing',
    icon: <LoadingOutlined spin />,
    label: 'Analyzing...'
  },
  ready: {
    color: 'success',
    icon: <CheckCircleOutlined />,
    label: 'Ready'
  },
  error: {
    color: 'error',
    icon: <ExclamationCircleOutlined />,
    label: 'Error'
  },
};

export function DataSourcesList({
  sources,
  loading,
  onUploadClick,
  onAnalyzeClick,
}: DataSourcesListProps) {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const removeFile = useRemoveFileFromProject();

  const handleExplore = (source: DataSourceInfo) => {
    // Only allow exploration of READY datasets
    if (source.status !== 'ready') {
      return;
    }
    navigate(`/workspace/${projectId}/data/${source.id}/questions`);
  };

  const handleDelete = async (sourceId: string) => {
    if (!projectId) return;
    await removeFile.mutateAsync({ projectId, datasetId: sourceId });
  };

  if (!loading && sources.length === 0) {
    return (
      <EmptyState
        icon={<FolderOpenOutlined />}
        title="No data sources yet"
        description="Upload a CSV or XES file to start analyzing your process"
        actionLabel="Upload File"
        onAction={onUploadClick}
      />
    );
  }

  return (
    <List
      loading={loading}
      dataSource={sources}
      grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 2, xxl: 3 }}
      renderItem={(source) => {
        const status = source.status || 'ready';
        const statusConfig = STATUS_CONFIG[status];

        const isZombie = status === 'ready' && source.caseCount === 0;
        const isReady = status === 'ready' && !isZombie;
        const needsAnalysis = status === 'unstructured' || isZombie;
        const isAnalyzing = status === 'analyzing';

        return (
          <List.Item>
            <Card
              size="small"
              hoverable={isReady}
              onClick={() => isReady && handleExplore(source)}
              style={{
                cursor: isReady ? 'pointer' : 'default',
                opacity: isAnalyzing ? 0.8 : 1,
              }}
              actions={[
                needsAnalysis && onAnalyzeClick && (
                  <Button
                    key="analyze"
                    type="primary"
                    size="small"
                    icon={<PlayCircleOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      onAnalyzeClick(source);
                    }}
                  >
                    Analyze
                  </Button>
                ),
                isReady && (
                  <Button
                    key="explore"
                    type="link"
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExplore(source);
                    }}
                  >
                    Explore
                  </Button>
                ),
                <Tooltip title="Delete dataset" key="delete">
                  <Button
                    type="text"
                    size="small"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(source.id);
                    }}
                  />
                </Tooltip>,
              ].filter(Boolean)}
            >
              <Card.Meta
                avatar={
                  <FileTextOutlined
                    style={{
                      fontSize: 24,
                      color: isReady ? tokens.colors.primary[500] : tokens.colors.neutral[400]
                    }}
                  />
                }
                title={
                  <Space>
                    <Text strong ellipsis style={{ maxWidth: 180 }}>{source.name}</Text>
                    <Tag
                      color={statusConfig.color}
                      icon={statusConfig.icon}
                      style={{ marginLeft: 'auto' }}
                    >
                      {statusConfig.label}
                    </Tag>
                  </Space>
                }
                description={
                  <Space direction="vertical" size={0}>
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                      {source.caseCount.toLocaleString()} cases · {source.eventCount.toLocaleString()} events
                    </Text>
                    {source.errorMessage && (
                      <Text type="danger" style={{ fontSize: tokens.fontSize.sm }}>
                        {source.errorMessage}
                      </Text>
                    )}
                  </Space>
                }
              />
            </Card>
          </List.Item>
        );
      }}
    />
  );
}

export default DataSourcesList;

