/**
 * BottleneckTable Component
 * 
 * Ranking table for bottleneck activities with impact scores.
 */

import { Table, Progress, Typography, Tag } from 'antd';
import { WarningOutlined } from '@ant-design/icons';
import type { BottleneckData } from '../../data/sampleAnalysisResults';

const { Text } = Typography;

interface BottleneckTableProps {
    data: BottleneckData[];
}

function formatDuration(seconds: number): string {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
}

export function BottleneckTable({ data }: BottleneckTableProps) {
    const columns = [
        {
            title: 'Rank',
            key: 'rank',
            width: 60,
            render: (_: unknown, __: unknown, idx: number) => (
                <Text
                    strong
                    style={{
                        color: idx < 3 ? '#ff4d4f' : '#666',
                        fontSize: 16,
                    }}
                >
                    #{idx + 1}
                </Text>
            ),
        },
        {
            title: 'Activity',
            dataIndex: 'activity',
            key: 'activity',
            render: (activity: string, _: unknown, idx: number) => (
                <span>
                    {idx < 3 && <WarningOutlined style={{ color: '#ff4d4f', marginRight: 8 }} />}
                    <Text strong>{activity}</Text>
                </span>
            ),
        },
        {
            title: 'Avg Wait Time',
            dataIndex: 'avgWaitTime',
            key: 'avgWaitTime',
            width: 120,
            render: (seconds: number) => (
                <Tag color="orange">{formatDuration(seconds)}</Tag>
            ),
        },
        {
            title: 'Frequency',
            dataIndex: 'frequency',
            key: 'frequency',
            width: 100,
            align: 'right' as const,
            render: (freq: number) => <Text>{freq.toLocaleString()}</Text>,
        },
        {
            title: 'Impact Score',
            dataIndex: 'impactScore',
            key: 'impactScore',
            width: 150,
            render: (score: number) => (
                <Progress
                    percent={Math.round(score * 100)}
                    size="small"
                    strokeColor={
                        score > 0.7 ? '#ff4d4f' :
                            score > 0.4 ? '#faad14' :
                                '#52c41a'
                    }
                    format={(p) => `${p}%`}
                />
            ),
        },
    ];

    return (
        <Table
            dataSource={data}
            columns={columns}
            rowKey="activity"
            pagination={false}
            size="middle"
        />
    );
}

export default BottleneckTable;
