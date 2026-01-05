/**
 * {{FEATURE_NAME_PASCAL}}ListPage - List view for {{FEATURE_NAME_PASCAL}}s
 *
 * Shows a paginated list of {{FEATURE_NAME_PASCAL}}s with search and filtering.
 * Uses FeaturePage wrapper for consistent loading/error/empty states.
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Space, Table } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { FeaturePage, PageSection } from '../../../shared/core';
import { use{{FEATURE_NAME_PASCAL}}List } from '../hooks';
import type { {{FEATURE_NAME_PASCAL}}, {{FEATURE_NAME_PASCAL}}ListOptions } from '../types';

export function {{FEATURE_NAME_PASCAL}}ListPage() {
  const navigate = useNavigate();
  const [options, setOptions] = useState<{{FEATURE_NAME_PASCAL}}ListOptions>({
    page: 1,
    pageSize: 10,
  });

  const { data, isLoading, error, refetch } = use{{FEATURE_NAME_PASCAL}}List(options);

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: {{FEATURE_NAME_PASCAL}}) => (
        <a onClick={() => navigate(`/{{FEATURE_NAME}}/${record.id}`)}>{name}</a>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
  ];

  return (
    <FeaturePage
      title="{{FEATURE_NAME_PASCAL}}s"
      description="Manage your {{FEATURE_NAME_PASCAL}}s"
      breadcrumb={[{ label: '{{FEATURE_NAME_PASCAL}}s' }]}
      isLoading={isLoading}
      error={error}
      onRetry={refetch}
      isEmpty={!data?.items.length}
      emptyState={{
        title: 'No {{FEATURE_NAME_PASCAL}}s yet',
        description: 'Create your first {{FEATURE_NAME_PASCAL}} to get started',
        actionLabel: 'Create {{FEATURE_NAME_PASCAL}}',
        onAction: () => navigate('/{{FEATURE_NAME}}/new'),
      }}
      auditCategory="{{FEATURE_NAME}}"
      actions={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/{{FEATURE_NAME}}/new')}
        >
          Create {{FEATURE_NAME_PASCAL}}
        </Button>
      }
    >
      <PageSection>
        <Space style={{ marginBottom: 16 }}>
          <Input
            placeholder="Search..."
            prefix={<SearchOutlined />}
            value={options.search}
            onChange={(e) => setOptions({ ...options, search: e.target.value, page: 1 })}
            style={{ width: 250 }}
          />
        </Space>

        <Table
          dataSource={data?.items}
          columns={columns}
          rowKey="id"
          pagination={{
            current: data?.page,
            pageSize: data?.pageSize,
            total: data?.total,
            onChange: (page, pageSize) => setOptions({ ...options, page, pageSize }),
          }}
        />
      </PageSection>
    </FeaturePage>
  );
}

export default {{FEATURE_NAME_PASCAL}}ListPage;
