/**
 * {{FEATURE_NAME_PASCAL}}DetailPage - Detail view for a single {{FEATURE_NAME_PASCAL}}
 *
 * Shows detailed information about a {{FEATURE_NAME_PASCAL}} with edit/delete actions.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 */

import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card, Descriptions, Popconfirm, Space, Tag } from 'antd';
import { EditOutlined, DeleteOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { FeaturePage, PageSection } from '../../../shared/core';
import { use{{FEATURE_NAME_PASCAL}}Detail, useDelete{{FEATURE_NAME_PASCAL}} } from '../hooks';

export function {{FEATURE_NAME_PASCAL}}DetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, error, refetch } = use{{FEATURE_NAME_PASCAL}}Detail(id!);
  const deleteMutation = useDelete{{FEATURE_NAME_PASCAL}}();

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(id!);
    navigate('/{{FEATURE_NAME}}');
  };

  const statusColors: Record<string, string> = {
    draft: 'default',
    active: 'success',
    archived: 'warning',
  };

  return (
    <FeaturePage
      title={data?.name ?? '{{FEATURE_NAME_PASCAL}} Details'}
      description={data?.description}
      breadcrumb={[
        { label: '{{FEATURE_NAME_PASCAL}}s', href: '/{{FEATURE_NAME}}' },
        { label: data?.name ?? 'Details' },
      ]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={!data}
      emptyState={{
        title: '{{FEATURE_NAME_PASCAL}} not found',
        description: 'The {{FEATURE_NAME_PASCAL}} you are looking for does not exist.',
        actionLabel: 'Go back',
        onAction: () => navigate('/{{FEATURE_NAME}}'),
      }}
      auditCategory="{{FEATURE_NAME}}"
      actions={
        <Space>
          <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/{{FEATURE_NAME}}')}>
            Back
          </Button>
          <Button icon={<EditOutlined />} onClick={() => navigate(`/{{FEATURE_NAME}}/${id}/edit`)}>
            Edit
          </Button>
          <Popconfirm
            title="Delete this {{FEATURE_NAME_PASCAL}}?"
            description="This action cannot be undone."
            onConfirm={handleDelete}
            okText="Delete"
            okButtonProps={{ danger: true, loading: deleteMutation.isPending }}
          >
            <Button danger icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      }
    >
      <PageSection title="Details">
        <Descriptions column={2}>
          <Descriptions.Item label="ID">{data?.id}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={statusColors[data?.status ?? 'draft']}>{data?.status}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {data?.createdAt ? new Date(data.createdAt).toLocaleString() : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Updated">
            {data?.updatedAt ? new Date(data.updatedAt).toLocaleString() : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="Description" span={2}>
            {data?.description ?? 'No description'}
          </Descriptions.Item>
        </Descriptions>
      </PageSection>

      {/* Add more sections as needed */}
      <PageSection title="Related Data">
        <Card>
          <p>Add related data components here.</p>
        </Card>
      </PageSection>
    </FeaturePage>
  );
}

export default {{FEATURE_NAME_PASCAL}}DetailPage;
