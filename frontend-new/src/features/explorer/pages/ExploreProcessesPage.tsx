/**
 * ExploreProcessesPage - List of analyzed datasets ready for exploration
 *
 * Shows only READY datasets with navigation to process explorer.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Card, Typography, Space, Tag, Button, Input, message } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import {
    SearchOutlined,
    PlayCircleOutlined,
    FolderOpenOutlined,
    CheckCircleOutlined,
} from '@ant-design/icons';
import { tokens, logAction } from '@/src/shared/design-system';
import { FeaturePage } from '../../../shared/core';
import { useEventLogsList } from '../hooks';
import { createLogger } from '../../../shared/lib/logger';

const log = createLogger('ExploreProcessesPage');
const { Text } = Typography;

interface ProcessDataset {
    id: string;
    name: string;
    projectId?: string;
    projectName?: string;
    totalCases: number;
    totalEvents: number;
    createdAt?: string;
    status?: string;
}

export function ExploreProcessesPage() {
    const navigate = useNavigate();
    const [searchText, setSearchText] = React.useState('');

    // Fetch all ready datasets
    const { data, isLoading, error, refetch } = useEventLogsList({
        pageSize: 100,
        // Note: Backend should support status filter, but we'll filter client-side for now
    });

    // Filter to only READY datasets
    const datasets: ProcessDataset[] = React.useMemo(() => {
        if (!data?.items) return [];
        return data.items
            .filter((item: any) => !item.status || item.status === 'ready')
            .filter((item: any) => item.totalCases > 0) // Filter out zombie datasets
            .filter((item: any) =>
                !searchText ||
                item.name.toLowerCase().includes(searchText.toLowerCase())
            );
    }, [data, searchText]);

    const handleExplore = (record: ProcessDataset) => {
        logAction('ExploreProcessesPage', 'explore_clicked', {
            datasetId: record.id,
            name: record.name
        });
        log.info('Exploring dataset', { id: record.id, name: record.name });

        // Navigate to the explorer detail page
        if (record.projectId) {
            navigate(`/workspace/${record.projectId}/data/${record.id}/explorer`);
        } else {
            // Show warning instead of navigating to broken route
            message.warning('Cannot explore: this dataset is not associated with a project');
            log.warn('Dataset has no projectId', { datasetId: record.id });
        }
    };

    const columns: ColumnsType<ProcessDataset> = [
        {
            title: 'Dataset Name',
            dataIndex: 'name',
            key: 'name',
            render: (name: string) => (
                <Space>
                    <PlayCircleOutlined style={{ color: tokens.colors.primary[500] }} />
                    <Text strong>{name}</Text>
                </Space>
            ),
        },
        {
            title: 'Project',
            dataIndex: 'projectName',
            key: 'projectName',
            render: (projectName: string) => (
                <Text type="secondary">{projectName || '-'}</Text>
            ),
        },
        {
            title: 'Cases',
            dataIndex: 'totalCases',
            key: 'totalCases',
            align: 'right',
            render: (count: number) => count.toLocaleString(),
        },
        {
            title: 'Events',
            dataIndex: 'totalEvents',
            key: 'totalEvents',
            align: 'right',
            render: (count: number) => count.toLocaleString(),
        },
        {
            title: 'Status',
            key: 'status',
            render: () => (
                <Tag color="success" icon={<CheckCircleOutlined />}>
                    Ready
                </Tag>
            ),
        },
        {
            title: 'Created',
            dataIndex: 'createdAt',
            key: 'createdAt',
            render: (date: string) => new Date(date).toLocaleDateString(),
        },
        {
            title: '',
            key: 'actions',
            width: 120,
            render: (_, record) => (
                <Button
                    type="primary"
                    size="small"
                    icon={<PlayCircleOutlined />}
                    onClick={() => handleExplore(record)}
                >
                    Explore
                </Button>
            ),
        },
    ];

    return (
        <FeaturePage
            title="Explore Processes"
            description="View and analyze your processed datasets"
            breadcrumb={[
                { label: 'Workspace', href: '/workspace' },
                { label: 'Explore Processes' },
            ]}
            isLoading={isLoading}
            error={error}
            onRetry={() => { refetch(); }}
            isEmpty={!isLoading && datasets.length === 0}
            emptyState={{
                icon: <FolderOpenOutlined />,
                title: 'No analyzed datasets yet',
                description: 'Upload and analyze a dataset first to start exploring your processes',
                actionLabel: 'Go to Workspace',
                onAction: () => navigate('/workspace'),
            }}
        >
            <Card>
                <div style={{ marginBottom: tokens.spacing[4] }}>
                    <Input
                        placeholder="Search datasets..."
                        prefix={<SearchOutlined />}
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        allowClear
                        style={{ maxWidth: 320 }}
                    />
                </div>

                <Table
                    columns={columns}
                    dataSource={datasets}
                    rowKey="id"
                    pagination={{
                        pageSize: 20,
                        showSizeChanger: true,
                        showTotal: (total) => `${total} datasets`,
                    }}
                    onRow={(record) => ({
                        onClick: () => handleExplore(record),
                        style: { cursor: 'pointer' },
                    })}
                />
            </Card>
        </FeaturePage>
    );
}

export default ExploreProcessesPage;
