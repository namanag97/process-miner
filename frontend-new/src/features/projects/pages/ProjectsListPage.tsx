/**
 * ProjectsListPage - List view for all projects
 *
 * Shows a searchable, sortable table of projects with create functionality.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Form } from 'antd';
import { PlusOutlined, FolderOutlined } from '@ant-design/icons';
import { DataTable, tokens, type DataTableColumn } from '@lumina/design-system';
import { FeaturePage, PageSection } from '../../../core/components/FeaturePage';
import { useProjectList, useCreateProject } from '../hooks';
import { CreateProjectModal } from '../components/CreateProjectModal';
import type { Project, CreateProjectInput } from '../types';

export function ProjectsListPage() {
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [form] = Form.useForm<CreateProjectInput>();

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
    const newProject = await createProject.mutateAsync(values);
    setIsCreateModalOpen(false);
    form.resetFields();
    navigate(`/workspace/${newProject.id}`);
  };

  const handleRowClick = (project: Project) => {
    navigate(`/workspace/${project.id}`);
  };

  return (
    <FeaturePage
      title="Projects"
      description="Manage your process mining projects"
      breadcrumb={[{ label: 'Projects' }]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={projects.length === 0}
      emptyState={{
        icon: <FolderOutlined style={{ fontSize: 48, color: tokens.colors.neutral[400] }} />,
        title: 'No projects yet',
        description: 'Create your first project to start analyzing your processes',
        actionLabel: 'Create Project',
        onAction: () => setIsCreateModalOpen(true),
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

      <CreateProjectModal
        open={isCreateModalOpen}
        onCancel={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
        loading={createProject.isPending}
        form={form}
      />
    </FeaturePage>
  );
}

export default ProjectsListPage;
