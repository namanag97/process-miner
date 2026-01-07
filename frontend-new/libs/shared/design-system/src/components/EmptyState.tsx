import React from 'react';
import { Button, Typography } from 'antd';
import { tokens } from '../theme';

const { Title, Text } = Typography;

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

/**
 * EmptyState - Placeholder for empty data states
 * Per DESIGN_SYSTEM.md Empty State pattern
 */
export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: tokens.spacing[12],
        textAlign: 'center',
        maxWidth: 400,
        margin: '0 auto',
        animation: `fadeIn ${tokens.duration.slow}ms ${tokens.easing.out}`,
      }}
    >
      {icon && (
        <div
          style={{
            fontSize: 48,
            color: tokens.colors.neutral[400],
            marginBottom: tokens.spacing[4],
            animation: 'float 3s ease-in-out infinite',
          }}
        >
          {icon}
        </div>
      )}
      
      <Title
        level={4}
        style={{
          marginBottom: tokens.spacing[2],
          color: tokens.colors.neutral[800],
        }}
      >
        {title}
      </Title>
      
      {description && (
        <Text
          style={{
            color: tokens.colors.neutral[500],
            marginBottom: tokens.spacing[6],
          }}
        >
          {description}
        </Text>
      )}
      
      {actionLabel && onAction && (
        <Button 
          type="primary" 
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

export default EmptyState;
