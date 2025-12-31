/**
 * ProjectDetailPage - Detail view for a single project
 *
 * Shows project info, data sources, and upload options.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Space, Typography, Popconfirm, Row, Col, message } from 'antd';
import {
  UploadOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { FeaturePage, PageSection } from '../../../core/components/FeaturePage';
import { useProjectDetail, useDeleteProject } from '../hooks';
import { DataSourcesList } from '../components/DataSourcesList';
import { toDataSources } from '../types';

const { Text } = Typography;

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading, error, refetch } = useProjectDetail(projectId || '');
  const deleteProject = useDeleteProject();

  const handleUpload = () => {
    navigate(`/workspace/${projectId}/upload`);
  };

  const handleConnectDepot = () => {
    message.info('Data depot connection coming soon');
  };

  const handleDeleteProject = async () => {
    if (!projectId) return;
    await deleteProject.mutateAsync(projectId);
    navigate('/workspace');
  };

  const dataSources = project?.eventLogs ? toDataSources(project.eventLogs) : [];

  return (
    <FeaturePage
      title={project?.name ?? 'Project Details'}
      description={project?.description || 'No description'}
      breadcrumb={[
        { label: 'Projects', href: '/workspace' },
        { label: project?.name ?? 'Project' },
      ]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={!project}
      emptyState={{
        title: 'Project not found',
        description: "The project you're looking for doesn't exist",
        actionLabel: 'Go Back',
        onAction: () => navigate('/workspace'),
      }}
      auditCategory="projects"
      actions={
        <Space>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/workspace')}
          >
            Back
          </Button>
          <Popconfirm
            title="Delete Project"
            description="Are you sure? This action cannot be undone."
            onConfirm={handleDeleteProject}
            okText="Delete"
            okButtonProps={{ danger: true, loading: deleteProject.isPending }}
          >
            <Button danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      }
    >
      <Card
        title="Data Sources"
        style={{ marginTop: tokens.spacing[6] }}
        extra={
          <Text type="secondary">
            {dataSources.length} source{dataSources.length !== 1 ? 's' : ''}
          </Text>
        }
      >
        {dataSources.length === 0 ? (
          <div style={{ padding: tokens.spacing[6] }}>
            <Text
              type="secondary"
              style={{ display: 'block', textAlign: 'center', marginBottom: tokens.spacing[6] }}
            >
              Add data to start analyzing your process
            </Text>
            <Row gutter={16} justify="center">
              <Col>
                <Card
                  hoverable
                  onClick={handleConnectDepot}
                  style={{
                    width: 200,
                    textAlign: 'center',
                    border: `2px dashed ${tokens.colors.neutral[300]}`,
                  }}
                  styles={{ body: { padding: tokens.spacing[6] } }}
                >
                  <DatabaseOutlined
                    style={{ fontSize: 32, color: tokens.colors.primary[500], marginBottom: 12 }}
                  />
                  <div>
                    <Text strong>Connect Depot</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                      Data source connection
                    </Text>
                  </div>
                </Card>
              </Col>
              <Col>
                <Card
                  hoverable
                  onClick={handleUpload}
                  style={{
                    width: 200,
                    textAlign: 'center',
                    border: `2px dashed ${tokens.colors.primary[400]}`,
                    backgroundColor: tokens.colors.primary[50],
                  }}
                  styles={{ body: { padding: tokens.spacing[6] } }}
                >
                  <UploadOutlined
                    style={{ fontSize: 32, color: tokens.colors.primary[500], marginBottom: 12 }}
                  />
                  <div>
                    <Text strong>Upload File</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                      CSV or XES format
                    </Text>
                  </div>
                </Card>
              </Col>
            </Row>
          </div>
        ) : (
          <>
            <div style={{ marginBottom: tokens.spacing[4] }}>
              <Button type="primary" icon={<UploadOutlined />} onClick={handleUpload}>
                Upload More Data
              </Button>
            </div>
            <DataSourcesList sources={dataSources} onUploadClick={handleUpload} />
          </>
        )}
      </Card>
    </FeaturePage>
  );
}

export default ProjectDetailPage;
