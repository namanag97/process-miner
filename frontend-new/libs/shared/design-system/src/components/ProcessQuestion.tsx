import React from 'react';
import { Card, Typography } from 'antd';
import { tokens } from '../theme';

const { Title, Text } = Typography;

export interface ProcessQuestionProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick?: () => void;
  disabled?: boolean;
}

/**
 * ProcessQuestion - Clickable card for process analysis questions
 * Used on the Process Questions page to guide users to insights
 */
export function ProcessQuestion({
  icon,
  title,
  description,
  onClick,
  disabled = false,
}: ProcessQuestionProps) {
  return (
    <Card
      hoverable={!disabled}
      onClick={disabled ? undefined : onClick}
      style={{
        height: '100%',
        borderRadius: tokens.radius.lg,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.6 : 1,
        transition: `all ${tokens.duration.moderate}ms ${tokens.easing.out}`,
        border: `1px solid ${tokens.colors.neutral[200]}`,
      }}
      onMouseEnter={(e) => {
        if (!disabled) {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = tokens.shadow.lg;
          e.currentTarget.style.borderColor = tokens.colors.primary[400];
        }
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '';
        e.currentTarget.style.borderColor = tokens.colors.neutral[200];
      }}
      bodyStyle={{
        padding: tokens.spacing[6],
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      <div
        style={{
          fontSize: 32,
          color: tokens.colors.primary[500],
          marginBottom: tokens.spacing[4],
        }}
      >
        {icon}
      </div>

      <Title
        level={5}
        style={{
          marginBottom: tokens.spacing[2],
          color: tokens.colors.neutral[800],
          fontWeight: tokens.fontWeight.semibold,
        }}
      >
        {title}
      </Title>

      <Text
        style={{
          color: tokens.colors.neutral[500],
          fontSize: tokens.fontSize.sm,
          lineHeight: 1.5,
          flex: 1,
        }}
      >
        {description}
      </Text>
    </Card>
  );
}

export default ProcessQuestion;
