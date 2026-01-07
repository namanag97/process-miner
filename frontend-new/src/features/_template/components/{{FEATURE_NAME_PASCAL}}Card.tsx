/**
 * {{FEATURE_NAME_PASCAL}}Card - Card component for displaying a {{FEATURE_NAME_PASCAL}} summary
 *
 * Reusable card component for list views and previews.
 */

import React from 'react';
import { Card, Tag, Typography, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import { tokens } from '@lumina/design-system';
import type { {{FEATURE_NAME_PASCAL}} } from '../types';

const { Text, Paragraph } = Typography;

interface {{FEATURE_NAME_PASCAL}}CardProps {
  item: {{FEATURE_NAME_PASCAL}};
  onClick?: () => void;
}

export function {{FEATURE_NAME_PASCAL}}Card({ item, onClick }: {{FEATURE_NAME_PASCAL}}CardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/{{FEATURE_NAME}}/${item.id}`);
    }
  };

  const statusColors: Record<string, string> = {
    draft: 'default',
    active: 'success',
    archived: 'warning',
  };

  return (
    <Card
      hoverable
      onClick={handleClick}
      style={{ marginBottom: tokens.spacing[4] }}
    >
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Text strong style={{ fontSize: tokens.fontSize.lg }}>
            {item.name}
          </Text>
          <Tag color={statusColors[item.status]}>{item.status}</Tag>
        </div>

        {item.description && (
          <Paragraph
            type="secondary"
            ellipsis={{ rows: 2 }}
            style={{ marginBottom: 0 }}
          >
            {item.description}
          </Paragraph>
        )}

        <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
          Created {new Date(item.createdAt).toLocaleDateString()}
        </Text>
      </Space>
    </Card>
  );
}

export default {{FEATURE_NAME_PASCAL}}Card;
