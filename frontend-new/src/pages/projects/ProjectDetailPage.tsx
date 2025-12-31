import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Space, Typography, Popconfirm, message, Row, Col } from 'antd';
import {
  UploadOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import {
  PageHeader,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useProject,
  useDeleteProject,
  type DataSourceInfo,
} from '@lumina/design-system';
import { DataSourcesList } from './components/DataSourcesList';

const { Text } = Typography;

/**
 * ProjectDetailPage - View and manage a single project
 * Shows project info, data sources, and upload options
 */
export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const { data: project, isLoading, error, refetch } = useProject(projectId || '');
  const deleteProject = useDeleteProject();

  const handleUpload = () => {
    navigate(`/projects/${projectId}/upload`);
  };

  const handleConnectDepot = () => {
    message.info('Data depot connection coming soon');
  };

  const handleDeleteProject = async () => {
    if (!projectId) return;
    try {
      await deleteProject.mutateAsync(projectId);
      message.success('Project deleted');
      navigate('/home?tab=workspace');
    } catch (err) {
      message.error('Failed to delete project');
    }
  };

  if (isLoading) {
    return <LoadingState type="fullPage" tip="Loading project..." />;
  }

  if (error) {
    return (
      <QueryError
        error={error}
        onRetry={() => refetch()}
        variant="fullPage"
      />
    );
  }

  if (!project) {
    return (
      <EmptyState
        title="Project not found"
        description="The project you're looking for doesn't exist"
        actionLabel="Go Back"
        onAction={() => navigate('/home?tab=workspace')}
      />
    );
  }

  // Transform processes to DataSourceInfo format
  const dataSources: DataSourceInfo[] = (project.processes || []).map((p) => ({
    id: p.id,
    name: p.name,
    type: p.name.endsWith('.xes') ? 'xes' : 'csv',
    caseCount: p.totalCases,
    eventCount: p.totalEvents,
    uploadedAt: p.createdAt,
    status: 'ready' as const,
  }));

  return (
    <div>
      <PageHeader
        title={project.name}
        description={project.description || 'No description'}
        breadcrumb={[
          { label: 'Home', href: '/home' },
          { label: 'Workspace', href: '/home?tab=workspace' },
          { label: project.name },
        ]}
        extra={
          <Space>
            <Button
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/home?tab=workspace')}
            >
              Back
            </Button>
            <Popconfirm
              title="Delete Project"
              description="Are you sure you want to delete this project? This action cannot be undone."
              onConfirm={handleDeleteProject}
              okText="Delete"
              okButtonProps={{ danger: true }}
            >
              <Button danger icon={<DeleteOutlined />}>
                Delete
              </Button>
            </Popconfirm>
          </Space>
        }
      />

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
                  bodyStyle={{ padding: tokens.spacing[6] }}
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
                  bodyStyle={{ padding: tokens.spacing[6] }}
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
            <DataSourcesList sources={dataSources} />
          </>
        )}
      </Card>
    </div>
  );
}

export default ProjectDetailPage;
