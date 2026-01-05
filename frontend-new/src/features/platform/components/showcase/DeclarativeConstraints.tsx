/**
 * DeclarativeConstraints Component
 * 
 * Visualization for DECLARE and Log Skeleton constraints.
 */

import { Table, Tag, Typography, Progress, Space, Tooltip } from 'antd';
import {
    ArrowRightOutlined,
    StopOutlined,
    CheckCircleOutlined,
    SwapOutlined,
} from '@ant-design/icons';
import type { ConstraintData } from '../../data/sampleAnalysisResults';

const { Text } = Typography;

interface DeclarativeConstraintsProps {
    data: ConstraintData[];
}

const CONSTRAINT_ICONS: Record<string, React.ReactNode> = {
    Response: <ArrowRightOutlined />,
    Precedence: <ArrowRightOutlined style={{ transform: 'rotate(180deg)' }} />,
    Existence: <CheckCircleOutlined />,
    NotCoExistence: <StopOutlined />,
    ChainResponse: <SwapOutlined />,
    AlternateResponse: <SwapOutlined />,
};

const CONSTRAINT_COLORS: Record<string, string> = {
    Response: 'blue',
    Precedence: 'purple',
    Existence: 'green',
    NotCoExistence: 'red',
    ChainResponse: 'cyan',
    AlternateResponse: 'orange',
};

const CONSTRAINT_DESCRIPTIONS: Record<string, string> = {
    Response: 'If A occurs, B must eventually follow',
    Precedence: 'B can only occur if A has occurred before',
    Existence: 'Activity must occur at least once',
    NotCoExistence: 'A and B cannot both occur in the same case',
    ChainResponse: 'B must immediately follow A',
    AlternateResponse: 'Between A and next B, A cannot repeat',
};

export function DeclarativeConstraints({ data }: DeclarativeConstraintsProps) {
    const columns = [
        {
            title: 'Constraint Type',
            dataIndex: 'type',
            key: 'type',
            width: 180,
            render: (type: string) => (
                <Tooltip title={CONSTRAINT_DESCRIPTIONS[type] || ''}>
                    <Tag
                        icon={CONSTRAINT_ICONS[type]}
                        color={CONSTRAINT_COLORS[type] || 'default'}
                        style={{ cursor: 'help' }}
                    >
                        {type}
                    </Tag>
                </Tooltip>
            ),
        },
        {
            title: 'Antecedent (A)',
            dataIndex: 'antecedent',
            key: 'antecedent',
            render: (activity: string) => (
                <Tag color="processing">{activity}</Tag>
            ),
        },
        {
            title: 'Consequent (B)',
            dataIndex: 'consequent',
            key: 'consequent',
            render: (activity?: string) => (
                activity ? <Tag color="warning">{activity}</Tag> : <Text type="secondary">—</Text>
            ),
        },
        {
            title: 'Support',
            dataIndex: 'support',
            key: 'support',
            width: 120,
            render: (support: number) => (
                <Space direction="vertical" size={0}>
                    <Progress
                        percent={Math.round(support * 100)}
                        size="small"
                        showInfo={false}
                        strokeColor="#1890ff"
                    />
                    <Text type="secondary" style={{ fontSize: 11 }}>{(support * 100).toFixed(0)}%</Text>
                </Space>
            ),
        },
        {
            title: 'Confidence',
            dataIndex: 'confidence',
            key: 'confidence',
            width: 120,
            render: (confidence: number) => (
                <Space direction="vertical" size={0}>
                    <Progress
                        percent={Math.round(confidence * 100)}
                        size="small"
                        showInfo={false}
                        strokeColor={confidence > 0.9 ? '#52c41a' : '#faad14'}
                    />
                    <Text type="secondary" style={{ fontSize: 11 }}>{(confidence * 100).toFixed(0)}%</Text>
                </Space>
            ),
        },
    ];

    return (
        <Table
            dataSource={data}
            columns={columns}
            rowKey={(record) => `${record.type}-${record.antecedent}-${record.consequent || ''}`}
            pagination={false}
            size="middle"
        />
    );
}

export default DeclarativeConstraints;
