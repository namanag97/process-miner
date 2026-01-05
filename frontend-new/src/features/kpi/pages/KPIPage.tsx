/**
 * KPIPage - KPI Dashboard with Multiple Analysis Tabs
 *
 * Provides comprehensive process KPI analysis including:
 * - Performance metrics and bottlenecks
 * - Deadline compliance tracking
 * - Unwanted activities detection
 * - Automation potential assessment
 */

import { useEffect } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Tabs, Button } from 'antd';
import {
  ClockCircleOutlined,
  CalendarOutlined,
  WarningOutlined,
  RobotOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import {
  PageHeader,
  LoadingState,
  QueryError,
  EmptyState,
  tokens,
  useProcess,
  logAction,
} from '@lumina/design-system';
import { PerformanceTab, DeadlinesTab, UnwantedActivitiesTab, AutomationTab } from '../components';
import { useKPIAuditLogger } from '../../../hooks';
import { createLogger } from '../../../utils/logger';

const log = createLogger('KPIPage');

export function KPIPage() {
  const { projectId, datasetId } = useParams<{ projectId: string; datasetId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'performance';
  const kpiAudit = useKPIAuditLogger();

  const { data: process, isLoading, error, refetch } = useProcess(datasetId || '');

  log.debug('Rendering KPIPage', { projectId, datasetId, activeTab });

  // Log KPI page view for audit
  useEffect(() => {
    if (process && datasetId) {
      kpiAudit.logView(datasetId, activeTab, projectId);
    }
  }, [process, datasetId, activeTab, projectId, kpiAudit]);

  const handleTabChange = (key: string) => {
    logAction('KPIPage', 'tab_changed', { from: activeTab, to: key, datasetId });
    setSearchParams({ tab: key });
  };

  if (isLoading) {
    return <LoadingState type="fullPage" text="Loading KPIs..." />;
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

  if (!process || !datasetId) {
    return (
      <EmptyState
        title="Process not found"
        description="The process you're looking for doesn't exist"
        actionLabel="Go Back"
        onAction={() => navigate(`/workspace/${projectId}`)}
      />
    );
  }

  // Dataset status validation - check if ready for analysis
  const status = (process as any).status || 'ready'; // Fallback for older API responses

  const handleGoToProject = () => {
    navigate(`/workspace/${projectId}`);
  };

  // UNSTRUCTURED: Dataset needs column mapping
  if (status === 'unstructured') {
    return (
      <EmptyState
        icon={<CalendarOutlined />}
        title="Column Mapping Required"
        description="Before viewing KPIs, you need to analyze this dataset. Go to your project to map the columns."
        actionLabel="Go to Project to Analyze"
        onAction={handleGoToProject}
      />
    );
  }

  // ANALYZING: Dataset is being processed
  if (status === 'analyzing') {
    return (
      <LoadingState
        type="fullPage"
        text="Your dataset is being analyzed. This may take a few moments..."
      />
    );
  }

  // ERROR: Analysis failed
  if (status === 'error') {
    return (
      <EmptyState
        icon={<WarningOutlined />}
        title="Analysis Failed"
        description="There was an error processing your dataset. Please go back and try again."
        actionLabel="Go to Project to Retry"
        onAction={handleGoToProject}
      />
    );
  }

  // READY: Dataset is ready - show KPIs

  const items = [
    {
      key: 'performance',
      label: (
        <span>
          <ClockCircleOutlined />
          Performance
        </span>
      ),
      children: <PerformanceTab datasetId={datasetId} />,
    },
    {
      key: 'deadlines',
      label: (
        <span>
          <CalendarOutlined />
          Deadlines
        </span>
      ),
      children: <DeadlinesTab datasetId={datasetId} />,
    },
    {
      key: 'unwanted',
      label: (
        <span>
          <WarningOutlined />
          Unwanted Activities
        </span>
      ),
      children: <UnwantedActivitiesTab datasetId={datasetId} />,
    },
    {
      key: 'automation',
      label: (
        <span>
          <RobotOutlined />
          Automation
        </span>
      ),
      children: <AutomationTab datasetId={datasetId} />,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Process KPIs"
        description={`Metrics for: ${process.name}`}
        breadcrumb={[
          { label: 'Workspace', href: '/workspace' },
          { label: 'Project', href: `/workspace/${projectId}` },
          { label: 'Questions', href: `/workspace/${projectId}/data/${datasetId}/questions` },
          { label: 'KPIs' },
        ]}
        actions={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/workspace/${projectId}/data/${datasetId}/questions`)}
          >
            Back to Questions
          </Button>
        }
      />

      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        items={items}
        style={{ marginTop: tokens.spacing[4] }}
        tabBarStyle={{
          marginBottom: 0,
          paddingLeft: tokens.spacing[4],
          backgroundColor: tokens.colors.surface.card,
          borderRadius: `${tokens.radius.lg}px ${tokens.radius.lg}px 0 0`,
        }}
      />
    </div>
  );
}

export default KPIPage;
