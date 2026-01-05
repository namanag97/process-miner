/**
 * AnalysisCard Component
 * 
 * Collapsible card for displaying individual process mining analysis results.
 */

import { useState, ReactNode } from 'react';
import { Card, Typography, Tag, Space, Button } from 'antd';
import {
    DownOutlined,
    RightOutlined,
    InfoCircleOutlined,
} from '@ant-design/icons';

const { Text, Paragraph } = Typography;

interface AnalysisCardProps {
    title: string;
    description: string;
    category: string;
    categoryIcon?: string;
    children: ReactNode;
    defaultExpanded?: boolean;
}

const CATEGORY_COLORS: Record<string, string> = {
    Discovery: 'blue',
    Variants: 'purple',
    Statistics: 'cyan',
    Performance: 'orange',
    Organizational: 'green',
    Conformance: 'gold',
    Declarative: 'magenta',
};

export function AnalysisCard({
    title,
    description,
    category,
    categoryIcon,
    children,
    defaultExpanded = false,
}: AnalysisCardProps) {
    const [expanded, setExpanded] = useState(defaultExpanded);

    return (
        <Card
            style={{ marginBottom: 16 }}
            bodyStyle={{ padding: expanded ? 16 : 0 }}
            headStyle={{
                cursor: 'pointer',
                background: expanded ? '#fafafa' : 'transparent',
            }}
            title={
                <div
                    onClick={() => setExpanded(!expanded)}
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}
                >
                    <Space>
                        <Button
                            type="text"
                            size="small"
                            icon={expanded ? <DownOutlined /> : <RightOutlined />}
                            style={{ marginRight: 4 }}
                        />
                        <Text strong style={{ fontSize: 15 }}>
                            {categoryIcon} {title}
                        </Text>
                        <Tag color={CATEGORY_COLORS[category] || 'default'}>{category}</Tag>
                    </Space>
                    <Button
                        type="text"
                        size="small"
                        icon={<InfoCircleOutlined />}
                        onClick={(e) => {
                            e.stopPropagation();
                            // Could show a tooltip or modal with more info
                        }}
                    />
                </div>
            }
        >
            {expanded && (
                <>
                    <Paragraph type="secondary" style={{ marginBottom: 16, fontSize: 13 }}>
                        {description}
                    </Paragraph>
                    {children}
                </>
            )}
        </Card>
    );
}

export default AnalysisCard;
