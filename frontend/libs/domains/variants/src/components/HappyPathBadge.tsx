import React from 'react';
import { Tag, Tooltip } from 'antd';
import { CheckCircleOutlined, StarOutlined } from '@ant-design/icons';

interface HappyPathBadgeProps {
  isHappyPath?: boolean;
  showTooltip?: boolean;
  size?: 'small' | 'default';
}

export const HappyPathBadge: React.FC<HappyPathBadgeProps> = ({
  isHappyPath,
  showTooltip = true,
  size = 'default',
}) => {
  if (!isHappyPath) return null;

  const badge = (
    <Tag
      icon={size === 'small' ? <StarOutlined /> : <CheckCircleOutlined />}
      color="success"
      style={{
        fontSize: size === 'small' ? 10 : 12,
        padding: size === 'small' ? '0 4px' : '0 8px',
      }}
    >
      {size === 'small' ? 'HP' : 'Happy Path'}
    </Tag>
  );

  if (showTooltip) {
    return (
      <Tooltip title="This variant represents the ideal/expected process flow">
        {badge}
      </Tooltip>
    );
  }

  return badge;
};
