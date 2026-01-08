/**
 * ProjectsListPage - List view for all projects
 *
 * Shows a searchable, sortable table of projects with create functionality.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 * Filters projects by current workspace context.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Form } from 'antd';
import { PlusOutlined, FolderOutlined } from '@ant-design/icons';
import { DataTable, tokens, type DataTableColumn, logAction } from '@lumina/design-system';
import { FeaturePage, PageSection } from '../../../../shared/core';
import { useProjectList, useCreateProject } from '../hooks';
import { CreateProjectModal } from '../components/CreateProjectModal';
import { useWorkspace } from '../../../../shared/context/UserContext';
import type { Project, CreateProjectInput } from '../types';

export function ProjectsListPage() {
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [form] = Form.useForm<CreateProjectInput>();

  // Get current workspace context
  const { workspace } = useWorkspace();

  // Pass workspace_id to filter projects (MVP: pass undefined for now to show all)
  const { data, isLoading, error, refetch } = useProjectList(undefined);
  const createProject = useCreateProject();

  const projects = data?.items ?? [];

  const columns: DataTableColumn<Project>[] = [
    {
      key: 'name',
      title: 'Project Name',
      dataIndex: 'name',
      sorter: (a, b) => a.name.localeCompare(b.name),
    },
    {
      key: 'description',
      title: 'Description',
      dataIndex: 'description',
      render: (value: unknown) => (value as string) || '-',
      ellipsis: true,
    },
    {
      key: 'totalFiles',
      title: 'Data Sources',
      dataIndex: 'totalFiles',
      width: 120,
      align: 'center',
      sorter: (a, b) => a.totalFiles - b.totalFiles,
    },
    {
      key: 'updatedAt',
      title: 'Last Updated',
      dataIndex: 'updatedAt',
      width: 150,
      render: (value: unknown) =>
        value
          ? new Date(value as string).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
          })
          : '-',
      sorter: (a, b) => {
        const dateA = a.updatedAt ? new Date(a.updatedAt).getTime() : 0;
        const dateB = b.updatedAt ? new Date(b.updatedAt).getTime() : 0;
        return dateA - dateB;
      },
    },
  ];

  const handleCreateProject = async (values: CreateProjectInput) => {
    const workspaceId = workspace?.id;
    logAction('ProjectsListPage', 'create_project_clicked', {
      name: values.name,
      workspaceId: workspaceId || 'none'
    });
    console.debug('[ProjectsListPage] Creating project:', { ...values, workspaceId });

    try {
      const newProject = await createProject.mutateAsync({
        ...values,
        workspaceId,
      });
      logAction('ProjectsListPage', 'project_created', { projectId: newProject.id, name: newProject.name });
      setIsCreateModalOpen(false);
      form.resetFields();
      navigate(`/workspace/${newProject.id}`);
    } catch (error) {
      logAction('ProjectsListPage', 'create_project_failed', { error: String(error), workspaceId: workspaceId || 'none' });
      console.error('Failed to create project:', error);
    }
  };

  const handleRowClick = (project: Project) => {
    logAction('ProjectsListPage', 'project_row_clicked', { projectId: project.id, projectName: project.name });
    navigate(`/workspace/${project.id}`);
  };

  // Description with workspace context
  const description = workspace
    ? `Manage your process mining projects in ${workspace.name}`
    : 'Manage your process mining projects';

  return (
    <>
      <FeaturePage
        title="Projects"
        description={description}
        breadcrumb={[{ label: 'Projects' }]}
        isLoading={isLoading}
        error={error}
        onRetry={() => { refetch(); }}
        isEmpty={projects.length === 0}
        emptyState={{
          icon: <FolderOutlined style={{ fontSize: 48, color: tokens.colors.primary[400] }} />,
          title: 'Welcome to Process Miner',
          description: 'Projects help you organize your process mining analyses. Each project can contain multiple datasets and analyses.',
          actionLabel: 'Create Your First Project',
          onAction: () => setIsCreateModalOpen(true),
          secondaryAction: {
            label: 'Watch Quick Start Guide',
            onClick: () => window.open('https://docs.processminer.io/quickstart', '_blank'),
          },
          tips: [
            'Upload CSV or XES event log files',
            'Discover process flows automatically',
            'Identify bottlenecks and inefficiencies',
          ],
        }}
        auditCategory="projects"
        actions={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            New Project
          </Button>
        }
      >
        <PageSection noPadding>
          <div style={{ padding: tokens.spacing[4] }}>
            <DataTable<Project>
              columns={columns}
              data={projects}
              loading={isLoading}
              searchable
              searchPlaceholder="Search projects..."
              onRowClick={handleRowClick}
              onRefresh={() => refetch()}
            />
          </div>
        </PageSection>
      </FeaturePage>

      <CreateProjectModal
        open={isCreateModalOpen}
        onCancel={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
        loading={createProject.isPending}
        form={form}
      />
    </>
  );
}

export default ProjectsListPage;
