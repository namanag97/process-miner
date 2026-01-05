/**
 * VariantTable Component
 * 
 * Table visualization for process variants with frequency bars.
 */

import { Table, Tag, Progress, Typography, Space } from 'antd';
import type { VariantData } from '../../data/sampleAnalysisResults';

const { Text } = Typography;

interface VariantTableProps {
    data: VariantData[];
}

export function VariantTable({ data }: VariantTableProps) {
    const columns = [
        {
            title: '#',
            dataIndex: 'rank',
            key: 'rank',
            width: 50,
            render: (rank: number) => (
                <Text strong style={{ color: rank <= 3 ? '#1890ff' : '#666' }}>
                    {rank}
                </Text>
            ),
        },
        {
            title: 'Variant Path',
            dataIndex: 'variant',
            key: 'variant',
            render: (activities: string[]) => (
                <Space wrap size={4}>
                    {activities.map((activity, idx) => (
                        <span key={idx}>
                            <Tag
                                color={
                                    activity.includes('Received') || activity.includes('Start') ? 'green' :
                                        activity.includes('Rejected') || activity.includes('Close') ? 'red' :
                                            activity.includes('Approved') ? 'blue' :
                                                'default'
                                }
                                style={{ margin: 2 }}
                            >
                                {activity}
                            </Tag>
                            {idx < activities.length - 1 && (
                                <Text type="secondary" style={{ margin: '0 2px' }}>→</Text>
                            )}
                        </span>
                    ))}
                </Space>
            ),
        },
        {
            title: 'Count',
            dataIndex: 'count',
            key: 'count',
            width: 80,
            align: 'right' as const,
            render: (count: number) => <Text strong>{count}</Text>,
        },
        {
            title: 'Coverage',
            dataIndex: 'percentage',
            key: 'percentage',
            width: 150,
            render: (percentage: number) => (
                <Space direction="vertical" size={0} style={{ width: '100%' }}>
                    <Progress
                        percent={percentage}
                        size="small"
                        showInfo={false}
                        strokeColor={{ from: '#108ee9', to: '#87d068' }}
                    />
                    <Text type="secondary" style={{ fontSize: 12 }}>{percentage.toFixed(1)}%</Text>
                </Space>
            ),
        },
    ];

    return (
        <Table
            dataSource={data}
            columns={columns}
            rowKey="rank"
            pagination={false}
            size="middle"
            scroll={{ x: true }}
        />
    );
}

export default VariantTable;
