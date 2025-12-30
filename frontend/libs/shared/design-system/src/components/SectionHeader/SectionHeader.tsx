import React from 'react';
import { Typography } from 'antd';

const { Title, Text } = Typography;

export interface SectionHeaderProps {
  /** Main section title */
  title: string;
  /** Optional description text below title */
  description?: string;
  /** Optional action element (button, link) on the right side */
  action?: React.ReactNode;
  /** Margin bottom spacing */
  marginBottom?: number;
}

/**
 * SectionHeader - A reusable section header component
 * 
 * Displays a title with optional description and action button.
 * Used to group content sections in the dashboard and other pages.
 */
export const SectionHeader: React.FC<SectionHeaderProps> = ({
  title,
  description,
  action,
  marginBottom = 16,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom,
      }}
    >
      <div>
        <Title
          level={4}
          style={{
            marginBottom: description ? 4 : 0,
            fontSize: 16,
            fontWeight: 600,
          }}
        >
          {title}
        </Title>
        {description && (
          <Text type="secondary" style={{ fontSize: 14 }}>
            {description}
          </Text>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};

export default SectionHeader;
