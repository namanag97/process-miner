import React, { useState } from 'react';
import { Button, Modal, Form, Input, message } from 'antd';
import type { FormInstance } from 'antd';
import { PlusOutlined, FolderOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import {
  DataTable,
  EmptyState,
  tokens,
  useProjects,
  useCreateProject,
  useDeleteProject,
  type DataTableColumn,
  type Project,
} from '@lumina/design-system';

/**
 * WorkspaceTab - Projects table with create/manage functionality
 * Primary workspace for project management
 */
export function WorkspaceTab() {
  const navigate = useNavigate();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [form] = Form.useForm();

  const { data: projectsData, isLoading, error, refetch } = useProjects();
  const createProject = useCreateProject();
  const deleteProject = useDeleteProject();

  const projects = projectsData?.items ?? [];

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

  const handleCreateProject = async (values: { name: string; description?: string }) => {
    try {
      const newProject = await createProject.mutateAsync(values);
      message.success('Project created successfully');
      setIsCreateModalOpen(false);
      form.resetFields();
      navigate(`/projects/${newProject.id}`);
    } catch (err) {
      message.error('Failed to create project');
    }
  };

  const handleRowClick = (project: Project) => {
    navigate(`/projects/${project.id}`);
  };

  if (error) {
    return (
      <EmptyState
        icon={<FolderOutlined />}
        title="Failed to load projects"
        description={error.message}
        actionLabel="Retry"
        onAction={() => refetch()}
      />
    );
  }

  if (!isLoading && projects.length === 0) {
    return (
      <div style={{ padding: tokens.spacing[8] }}>
        <EmptyState
          icon={<FolderOutlined />}
          title="No projects yet"
          description="Create your first project to start analyzing your processes"
          actionLabel="Create Project"
          onAction={() => setIsCreateModalOpen(true)}
        />
        <CreateProjectModal
          open={isCreateModalOpen}
          onCancel={() => setIsCreateModalOpen(false)}
          onSubmit={handleCreateProject}
          loading={createProject.isPending}
          form={form}
        />
      </div>
    );
  }

  return (
    <div style={{ padding: tokens.spacing[4] }}>
      <DataTable<Project>
        columns={columns}
        data={projects}
        loading={isLoading}
        searchable
        searchPlaceholder="Search projects..."
        onRowClick={handleRowClick}
        onRefresh={() => refetch()}
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsCreateModalOpen(true)}
          >
            New Project
          </Button>
        }
      />

      <CreateProjectModal
        open={isCreateModalOpen}
        onCancel={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
        loading={createProject.isPending}
        form={form}
      />
    </div>
  );
}

interface CreateProjectModalProps {
  open: boolean;
  onCancel: () => void;
  onSubmit: (values: { name: string; description?: string }) => void;
  loading: boolean;
  form: FormInstance;
}

function CreateProjectModal({ open, onCancel, onSubmit, loading, form }: CreateProjectModalProps) {
  return (
    <Modal
      title="Create New Project"
      open={open}
      onCancel={onCancel}
      footer={null}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={onSubmit}
        style={{ marginTop: tokens.spacing[4] }}
      >
        <Form.Item
          name="name"
          label="Project Name"
          rules={[{ required: true, message: 'Please enter a project name' }]}
        >
          <Input placeholder="e.g., Q4 Process Analysis" autoFocus />
        </Form.Item>

        <Form.Item name="description" label="Description (optional)">
          <Input.TextArea
            rows={3}
            placeholder="Brief description of the project"
          />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Button onClick={onCancel} style={{ marginRight: 8 }}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit" loading={loading}>
            Create Project
          </Button>
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default WorkspaceTab;
