/**
 * ResourceTable Component
 * 
 * Table visualization for resource utilization data.
 */

import { Table, Tag, Typography, Space, Progress } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import type { ResourceUtilization } from '../../data/sampleAnalysisResults';

const { Text } = Typography;

interface ResourceTableProps {
    data: ResourceUtilization[];
}

export function ResourceTable({ data }: ResourceTableProps) {
    const maxEvents = Math.max(...data.map(r => r.eventCount));

    const columns = [
        {
            title: 'Resource',
            dataIndex: 'resource',
            key: 'resource',
            render: (name: string) => (
                <Space>
                    <UserOutlined style={{ color: '#1890ff' }} />
                    <Text strong>{name}</Text>
                </Space>
            ),
        },
        {
            title: 'Cases',
            dataIndex: 'caseCount',
            key: 'caseCount',
            width: 80,
            align: 'right' as const,
            render: (count: number) => <Text>{count}</Text>,
        },
        {
            title: 'Events',
            dataIndex: 'eventCount',
            key: 'eventCount',
            width: 150,
            render: (count: number) => (
                <Space direction="vertical" size={0} style={{ width: '100%' }}>
                    <Progress
                        percent={Math.round((count / maxEvents) * 100)}
                        size="small"
                        showInfo={false}
                        strokeColor="#1890ff"
                    />
                    <Text type="secondary" style={{ fontSize: 11 }}>{count} events</Text>
                </Space>
            ),
        },
        {
            title: 'Avg Events/Case',
            dataIndex: 'avgEventsPerCase',
            key: 'avgEventsPerCase',
            width: 120,
            align: 'right' as const,
            render: (avg: number) => (
                <Tag color="blue">{avg.toFixed(2)}</Tag>
            ),
        },
        {
            title: 'Activities',
            dataIndex: 'activities',
            key: 'activities',
            render: (activities: string[]) => (
                <Space wrap size={4}>
                    {activities.map((activity, idx) => (
                        <Tag key={idx} color="default" style={{ margin: 2 }}>
                            {activity}
                        </Tag>
                    ))}
                </Space>
            ),
        },
    ];

    return (
        <Table
            dataSource={data}
            columns={columns}
            rowKey="resource"
            pagination={false}
            size="middle"
        />
    );
}

export default ResourceTable;
