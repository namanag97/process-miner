/**
 * StatisticsPanel Component
 * 
 * Metric cards grid for basic process statistics.
 */

import { Row, Col, Card, Statistic, Typography } from 'antd';
import {
    FileTextOutlined,
    UnorderedListOutlined,
    TeamOutlined,
    BranchesOutlined,
    ClockCircleOutlined,
    NumberOutlined,
} from '@ant-design/icons';
import type { StatisticsData } from '../../data/sampleAnalysisResults';

const { Text } = Typography;

interface StatisticsPanelProps {
    data: StatisticsData;
}

export function StatisticsPanel({ data }: StatisticsPanelProps) {
    const stats = [
        {
            title: 'Total Cases',
            value: data.totalCases,
            icon: <FileTextOutlined />,
            color: '#1890ff',
        },
        {
            title: 'Total Events',
            value: data.totalEvents,
            icon: <UnorderedListOutlined />,
            color: '#52c41a',
        },
        {
            title: 'Activities',
            value: data.uniqueActivities,
            icon: <NumberOutlined />,
            color: '#722ed1',
        },
        {
            title: 'Resources',
            value: data.uniqueResources,
            icon: <TeamOutlined />,
            color: '#13c2c2',
        },
        {
            title: 'Variants',
            value: data.uniqueVariants,
            icon: <BranchesOutlined />,
            color: '#eb2f96',
        },
        {
            title: 'Avg Case Length',
            value: data.avgCaseLength.toFixed(1),
            suffix: 'events',
            icon: <UnorderedListOutlined />,
            color: '#fa8c16',
        },
        {
            title: 'Avg Duration',
            value: data.avgDurationDays.toFixed(1),
            suffix: 'days',
            icon: <ClockCircleOutlined />,
            color: '#1890ff',
        },
        {
            title: 'Median Duration',
            value: data.medianDurationDays.toFixed(1),
            suffix: 'days',
            icon: <ClockCircleOutlined />,
            color: '#52c41a',
        },
    ];

    return (
        <Row gutter={[16, 16]}>
            {stats.map((stat, idx) => (
                <Col xs={12} sm={8} md={6} key={idx}>
                    <Card size="small" hoverable>
                        <Statistic
                            title={
                                <span style={{ color: stat.color }}>
                                    {stat.icon} <Text style={{ marginLeft: 8 }}>{stat.title}</Text>
                                </span>
                            }
                            value={stat.value}
                            suffix={stat.suffix}
                            valueStyle={{ color: stat.color, fontSize: 24 }}
                        />
                    </Card>
                </Col>
            ))}
        </Row>
    );
}

export default StatisticsPanel;
