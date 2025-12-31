import React from 'react';
import { Tabs } from 'antd';
import { HomeOutlined, AppstoreOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { PageHeader, tokens, useProjects } from '@lumina/design-system';
import { useAuth } from '../../context/AuthContext';
import { OverviewTab } from './OverviewTab';
import { WorkspaceTab } from './WorkspaceTab';

/**
 * HomePage - Main landing page with Overview and Workspace tabs
 * Overview shows metrics, Workspace shows projects table
 */
export function HomePage() {
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'workspace';

  const { data: projectsData } = useProjects();
  const projects = projectsData?.items ?? [];

  const stats = {
    totalProjects: projects.length,
    totalProcesses: projects.reduce((sum, p) => sum + (p.processCount || 0), 0),
    activeAnalyses: projects.filter((p) => p.processCount > 0).length,
  };

  const handleTabChange = (key: string) => {
    setSearchParams({ tab: key });
  };

  const items = [
    {
      key: 'overview',
      label: (
        <span>
          <HomeOutlined />
          Overview
        </span>
      ),
      children: <OverviewTab stats={stats} />,
    },
    {
      key: 'workspace',
      label: (
        <span>
          <AppstoreOutlined />
          Workspace
        </span>
      ),
      children: <WorkspaceTab />,
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name || 'User'}`}
        description="Manage your projects and explore your processes"
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

export default HomePage;
