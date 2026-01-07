/**
 * ProjectDetailPage - Detail view for a single project
 *
 * Shows project info, data sources, analysis options, and upload options.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 */

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Space, Typography, Popconfirm, Row, Col, message, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import {
  UploadOutlined,
  DatabaseOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
  PlayCircleOutlined,
  BranchesOutlined,
  LineChartOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { tokens, logAction } from '@/src/shared/design-system';
import { devLog } from '../../../../shared/ui/DevConsole';
import { FeaturePage } from '../../../../shared/core';
import { useProjectDetail, useDeleteProject } from '../hooks';
import { DataSourcesList } from '../components/DataSourcesList';
import { SimpleUploadModal } from '../components/SimpleUploadModal';
import { AnalyzeModal } from '../components/AnalyzeModal';
import { toDataSources } from '../types';
import type { DataSourceInfo } from '../types';

const { Text, Title } = Typography;

// Analysis type definitions
const ANALYSIS_TYPES = [
  {
    key: 'discovery',
    label: 'Process Discovery',
    description: 'Discover process model from event logs',
    icon: <BranchesOutlined />,
  },
  {
    key: 'conformance',
    label: 'Conformance Check',
    description: 'Check conformance against a reference model',
    icon: <CheckCircleOutlined />,
  },
  {
    key: 'variants',
    label: 'Variant Analysis',
    description: 'Analyze process variants and deviations',
    icon: <ExperimentOutlined />,
  },
  {
    key: 'performance',
    label: 'Performance Analysis',
    description: 'Identify bottlenecks and delays',
    icon: <LineChartOutlined />,
  },
];

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [_selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);

  // Modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [analyzeDataset, setAnalyzeDataset] = useState<DataSourceInfo | null>(null);

  const { data: project, isLoading, error, refetch } = useProjectDetail(projectId || '');
  const deleteProject = useDeleteProject();

  // Reset modal state when navigating between projects (BUG-010)
  React.useEffect(() => {
    setUploadModalOpen(false);
    setAnalyzeDataset(null);
    setSelectedAnalysis(null);
  }, [projectId]);

  // Navigate to full-page upload wizard (Celonis-style)
  const handleUpload = () => {
    logAction('ProjectDetailPage', 'upload_clicked', { projectId });
    devLog.action('ProjectDetailPage', 'Navigating to upload wizard', { projectId });
    navigate(`/workspace/${projectId}/upload`);
  };

  // Analyze or resume wizard based on dataset status
  const handleAnalyze = (dataset: DataSourceInfo) => {
    logAction('ProjectDetailPage', 'analyze_clicked', { projectId, datasetId: dataset.id, status: dataset.status });
    devLog.info('ProjectDetailPage', `Analyze clicked: ${dataset.name}`, { status: dataset.status });

    // Route based on dataset status
    const status = dataset.status?.toLowerCase();

    if (status === 'unstructured' || status === 'awaiting_mapping') {
      // Not yet mapped - open wizard at the right step
      devLog.action('ProjectDetailPage', 'Routing to wizard (unmapped dataset)', { datasetId: dataset.id });
      navigate(`/workspace/${projectId}/upload?datasetId=${dataset.id}`);
    } else if (status === 'ingesting' || status === 'analyzing') {
      // Processing in progress - show progress in wizard
      devLog.action('ProjectDetailPage', 'Routing to wizard (processing)', { datasetId: dataset.id });
      navigate(`/workspace/${projectId}/upload?datasetId=${dataset.id}`);
    } else if (status === 'ready') {
      // Ready - go to questions page
      devLog.action('ProjectDetailPage', 'Routing to questions (ready dataset)', { datasetId: dataset.id });
      navigate(`/workspace/${projectId}/data/${dataset.id}/questions`);
    } else if (status === 'error') {
      // Error - open wizard to retry
      devLog.action('ProjectDetailPage', 'Routing to wizard (error retry)', { datasetId: dataset.id });
      navigate(`/workspace/${projectId}/upload?datasetId=${dataset.id}`);
    } else {
      // Fallback: open analyze modal for legacy datasets
      setAnalyzeDataset(dataset);
    }
  };

  const handleConnectDatabase = () => {
    logAction('ProjectDetailPage', 'add_database_clicked', { projectId });
    message.info('Database connection coming soon');
  };

  const handleDeleteProject = async () => {
    if (!projectId) return;
    logAction('ProjectDetailPage', 'delete_project_clicked', { projectId });
    await deleteProject.mutateAsync(projectId);
    logAction('ProjectDetailPage', 'project_deleted', { projectId });
    navigate('/workspace');
  };

  const handleRunAnalysis = (analysisType: string) => {
    const dataSources = project?.datasets ? toDataSources(project.datasets) : [];

    if (dataSources.length === 0) {
      logAction('ProjectDetailPage', 'analysis_blocked_no_data', { projectId, analysisType });
      message.warning('Please upload data before running analysis');
      return;
    }

    // Navigate to appropriate analysis page (project-scoped)
    const datasetId = dataSources[0].id;  // Use first data source
    logAction('ProjectDetailPage', 'run_analysis_clicked', { projectId, analysisType, datasetId });

    switch (analysisType) {
      case 'discovery':
        navigate(`/workspace/${projectId}/data/${datasetId}/explorer`);
        break;
      case 'conformance':
        navigate(`/workspace/${projectId}/analytics/conformance?datasetId=${datasetId}`);
        break;
      case 'variants':
        navigate(`/workspace/${projectId}/data/${datasetId}/explorer?tab=variants`);
        break;
      case 'performance':
        navigate(`/workspace/${projectId}/analytics/performance?datasetId=${datasetId}`);
        break;
      default:
        navigate(`/workspace/${projectId}/data/${datasetId}/explorer`);
    }
  };

  const analysisMenuItems: MenuProps['items'] = ANALYSIS_TYPES.map((analysis) => ({
    key: analysis.key,
    label: (
      <div style={{ padding: '4px 0' }}>
        <Space>
          {analysis.icon}
          <div>
            <div style={{ fontWeight: 500 }}>{analysis.label}</div>
            <div style={{ fontSize: 12, color: tokens.colors.neutral[500] }}>
              {analysis.description}
            </div>
          </div>
        </Space>
      </div>
    ),
    onClick: () => handleRunAnalysis(analysis.key),
  }));

  const dataSources = project?.datasets ? toDataSources(project.datasets) : [];
  const hasData = dataSources.length > 0;

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
      onRetry={() => { refetch(); }}
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
          {hasData && (
            <Dropdown menu={{ items: analysisMenuItems }} placement="bottomRight">
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                style={{
                  background: `linear-gradient(135deg, ${tokens.colors.primary[500]}, ${tokens.colors.primary[600]})`,
                }}
              >
                Run Analysis
              </Button>
            </Dropdown>
          )}
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
      {/* Quick Stats */}
      {hasData && (
        <Row gutter={16} style={{ marginTop: tokens.spacing[4] }}>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text type="secondary">Data Sources</Text>
              <Title level={3} style={{ margin: '8px 0 0' }}>{dataSources.length}</Title>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text type="secondary">Total Analyses</Text>
              <Title level={3} style={{ margin: '8px 0 0' }}>{project?.totalAnalyses || 0}</Title>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" style={{ textAlign: 'center' }}>
              <Text type="secondary">Created</Text>
              <Title level={5} style={{ margin: '8px 0 0' }}>
                {project?.createdAt ? new Date(project.createdAt).toLocaleDateString() : '-'}
              </Title>
            </Card>
          </Col>
        </Row>
      )}

      {/* Data Sources */}
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
                  onClick={handleConnectDatabase}
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
                    <Text strong>Add Database</Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                      SQL, Snowflake, or SAP
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
            <DataSourcesList
              sources={dataSources}
              onUploadClick={handleUpload}
              onAnalyzeClick={handleAnalyze}
            />
          </>
        )}
      </Card>

      {/* Analysis Quick Actions - only show when data exists */}
      {hasData && (
        <Card
          title="Quick Analysis"
          style={{ marginTop: tokens.spacing[6] }}
          extra={<Text type="secondary">Choose an analysis type</Text>}
        >
          <Row gutter={[16, 16]}>
            {ANALYSIS_TYPES.map((analysis) => (
              <Col xs={24} sm={12} md={6} key={analysis.key}>
                <Card
                  hoverable
                  onClick={() => handleRunAnalysis(analysis.key)}
                  style={{
                    textAlign: 'center',
                    height: '100%',
                    transition: 'all 0.3s ease',
                  }}
                  styles={{ body: { padding: tokens.spacing[4] } }}
                >
                  <div style={{ fontSize: 28, color: tokens.colors.primary[500], marginBottom: 8 }}>
                    {analysis.icon}
                  </div>
                  <Text strong style={{ display: 'block' }}>{analysis.label}</Text>
                  <Text
                    type="secondary"
                    style={{ fontSize: tokens.fontSize.sm, display: 'block', marginTop: 4 }}
                  >
                    {analysis.description}
                  </Text>
                </Card>
              </Col>
            ))}
          </Row>
        </Card>
      )}

      {/* Upload Modal */}
      <SimpleUploadModal
        open={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        projectId={projectId || ''}
        onSuccess={refetch}
      />

      {/* Analyze Modal */}
      {analyzeDataset && (
        <AnalyzeModal
          open={!!analyzeDataset}
          onClose={() => setAnalyzeDataset(null)}
          datasetId={analyzeDataset.id}
          datasetName={analyzeDataset.name}
          projectId={projectId || ''}
          onSuccess={refetch}
        />
      )}
    </FeaturePage>
  );
}

export default ProjectDetailPage;
