import React from 'react';
import { List, message, Popconfirm } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import {
  DataSourceCard,
  EmptyState,
  tokens,
  useRemoveFileFromProject,
  type DataSourceInfo,
} from '@lumina/design-system';
import { FolderOpenOutlined } from '@ant-design/icons';

interface DataSourcesListProps {
  sources: DataSourceInfo[];
  loading?: boolean;
  onUploadClick?: () => void;
}

/**
 * DataSourcesList - Display and manage data sources for a project
 * Shows cards for each data source with explore/delete actions
 */
export function DataSourcesList({ sources, loading, onUploadClick }: DataSourcesListProps) {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const removeFile = useRemoveFileFromProject();

  const handleExplore = (source: DataSourceInfo) => {
    navigate(`/projects/${projectId}/data/${source.id}/questions`);
  };

  const handleDelete = async (sourceId: string) => {
    if (!projectId) return;
    try {
      await removeFile.mutateAsync({ projectId, processId: sourceId });
      message.success('Data source removed');
    } catch (err) {
      message.error('Failed to remove data source');
    }
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
      grid={{ gutter: 16, xs: 1, sm: 1, md: 1, lg: 1, xl: 1, xxl: 1 }}
      renderItem={(source) => (
        <List.Item style={{ marginBottom: tokens.spacing[3] }}>
          <DataSourceCard
            source={source}
            onExplore={() => handleExplore(source)}
            onDelete={() => handleDelete(source.id)}
          />
        </List.Item>
      )}
    />
  );
}

export default DataSourcesList;
