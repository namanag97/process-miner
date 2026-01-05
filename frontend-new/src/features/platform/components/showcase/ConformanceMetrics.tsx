/**
 * ConformanceMetrics Component
 * 
 * Visualization for conformance checking results with quality metrics.
 */

import { Row, Col, Card, Progress, Typography, Table, Tag, Space } from 'antd';
import {
    CheckCircleOutlined,
    AimOutlined,
    BulbOutlined,
    ToolOutlined,
} from '@ant-design/icons';
import type { ConformanceData } from '../../data/sampleAnalysisResults';

const { Text, Title } = Typography;

interface ConformanceMetricsProps {
    data: ConformanceData;
}

export function ConformanceMetrics({ data }: ConformanceMetricsProps) {
    const metrics = [
        {
            title: 'Fitness',
            value: data.fitness,
            icon: <CheckCircleOutlined />,
            color: '#52c41a',
            description: 'How well the log fits the model',
        },
        {
            title: 'Precision',
            value: data.precision,
            icon: <AimOutlined />,
            color: '#1890ff',
            description: 'How precise the model is',
        },
        {
            title: 'Generalization',
            value: data.generalization,
            icon: <BulbOutlined />,
            color: '#722ed1',
            description: 'Model can handle unseen traces',
        },
        {
            title: 'Simplicity',
            value: data.simplicity,
            icon: <ToolOutlined />,
            color: '#faad14',
            description: 'Model complexity measure',
        },
    ];

    const deviationColumns = [
        {
            title: 'Trace',
            dataIndex: 'trace',
            key: 'trace',
            render: (trace: string) => <Tag>{trace}</Tag>,
        },
        {
            title: 'Issue',
            dataIndex: 'issue',
            key: 'issue',
            render: (issue: string) => <Text>{issue}</Text>,
        },
        {
            title: 'Count',
            dataIndex: 'count',
            key: 'count',
            width: 80,
            render: (count: number) => (
                <Tag color="error">{count}</Tag>
            ),
        },
    ];

    return (
        <div>
            {/* Quality Metrics */}
            <Row gutter={16} style={{ marginBottom: 24 }}>
                {metrics.map((metric, idx) => (
                    <Col xs={12} sm={6} key={idx}>
                        <Card size="small" hoverable>
                            <Space direction="vertical" align="center" style={{ width: '100%' }}>
                                <Progress
                                    type="circle"
                                    percent={Math.round(metric.value * 100)}
                                    size={80}
                                    strokeColor={metric.color}
                                    format={(p) => `${p}%`}
                                />
                                <Text strong style={{ color: metric.color }}>
                                    {metric.icon} {metric.title}
                                </Text>
                                <Text type="secondary" style={{ fontSize: 11, textAlign: 'center' }}>
                                    {metric.description}
                                </Text>
                            </Space>
                        </Card>
                    </Col>
                ))}
            </Row>

            {/* Alignment Summary */}
            <Card size="small" style={{ marginBottom: 16 }}>
                <Row gutter={24}>
                    <Col span={12}>
                        <Space>
                            <Title level={3} style={{ margin: 0, color: '#52c41a' }}>
                                {data.alignedTraces}
                            </Title>
                            <Text>/ {data.totalTraces} traces aligned</Text>
                        </Space>
                    </Col>
                    <Col span={12}>
                        <Progress
                            percent={Math.round((data.alignedTraces / data.totalTraces) * 100)}
                            strokeColor={{ from: '#52c41a', to: '#1890ff' }}
                        />
                    </Col>
                </Row>
            </Card>

            {/* Deviations Table */}
            {data.deviations.length > 0 && (
                <Card title="Top Deviations" size="small">
                    <Table
                        dataSource={data.deviations}
                        columns={deviationColumns}
                        rowKey="trace"
                        pagination={false}
                        size="small"
                    />
                </Card>
            )}
        </div>
    );
}

export default ConformanceMetrics;
