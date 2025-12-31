import React, { useEffect } from 'react';
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
} from '@lumina/design-system';
import { PerformanceTab, DeadlinesTab, UnwantedActivitiesTab, AutomationTab } from './tabs';
import { useKPIAuditLogger } from '../../hooks';

/**
 * KPIPage - KPI dashboard with multiple analysis tabs
 * Each tab corresponds to a process question from the questions page
 */
export function KPIPage() {
  const { projectId, logId } = useParams<{ projectId: string; logId: string }>();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'performance';
  const kpiAudit = useKPIAuditLogger();

  const { data: process, isLoading, error, refetch } = useProcess(logId || '');

  // Log KPI page view for audit
  useEffect(() => {
    if (process && logId) {
      kpiAudit.logView(logId, activeTab, projectId);
    }
  }, [process, logId, activeTab, projectId, kpiAudit]);

  const handleTabChange = (key: string) => {
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

  if (!process || !logId) {
    return (
      <EmptyState
        title="Process not found"
        description="The process you're looking for doesn't exist"
        actionLabel="Go Back"
        onAction={() => navigate(`/projects/${projectId}`)}
      />
    );
  }

  const items = [
    {
      key: 'performance',
      label: (
        <span>
          <ClockCircleOutlined />
          Performance
        </span>
      ),
      children: <PerformanceTab logId={logId} />,
    },
    {
      key: 'deadlines',
      label: (
        <span>
          <CalendarOutlined />
          Deadlines
        </span>
      ),
      children: <DeadlinesTab logId={logId} />,
    },
    {
      key: 'unwanted',
      label: (
        <span>
          <WarningOutlined />
          Unwanted Activities
        </span>
      ),
      children: <UnwantedActivitiesTab logId={logId} />,
    },
    {
      key: 'automation',
      label: (
        <span>
          <RobotOutlined />
          Automation
        </span>
      ),
      children: <AutomationTab logId={logId} />,
    },
  ];

  return (
    <div>
      <PageHeader
        title="Process KPIs"
        description={`Metrics for: ${process.name}`}
        breadcrumb={[
          { label: 'Home', href: '/home' },
          { label: 'Project', href: `/projects/${projectId}` },
          { label: 'Questions', href: `/projects/${projectId}/data/${logId}/questions` },
          { label: 'KPIs' },
        ]}
        actions={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate(`/projects/${projectId}/data/${logId}/questions`)}
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
