import React from 'react';
import { Button, Typography, Space } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import { tokens } from '../theme';

const { Title, Text } = Typography;

export interface SecondaryAction {
  label: string;
  onClick: () => void;
}

export interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  /** Secondary action shown as a text link below the primary action */
  secondaryAction?: SecondaryAction;
  /** Quick tips shown as a bulleted list to help users get started */
  tips?: string[];
}

/**
 * EmptyState - Placeholder for empty data states
 * Per DESIGN_SYSTEM.md Empty State pattern
 *
 * Enhanced with:
 * - Secondary action link for documentation/guides
 * - Tips list for onboarding guidance
 */
export function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
  secondaryAction,
  tips,
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
        maxWidth: 480,
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
            marginBottom: tokens.spacing[4],
            maxWidth: 360,
          }}
        >
          {description}
        </Text>
      )}

      {/* Tips list */}
      {tips && tips.length > 0 && (
        <div
          style={{
            marginBottom: tokens.spacing[6],
            textAlign: 'left',
            background: tokens.colors.neutral[50],
            padding: tokens.spacing[4],
            borderRadius: tokens.radius.md,
            width: '100%',
            maxWidth: 320,
          }}
        >
          <Text
            strong
            style={{
              display: 'block',
              marginBottom: tokens.spacing[2],
              color: tokens.colors.neutral[700],
              fontSize: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            What you can do
          </Text>
          {tips.map((tip, index) => (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: tokens.spacing[2],
                marginBottom: index < tips.length - 1 ? tokens.spacing[2] : 0,
              }}
            >
              <CheckCircleOutlined
                style={{
                  color: tokens.colors.success[500],
                  fontSize: 14,
                  marginTop: 3,
                }}
              />
              <Text style={{ color: tokens.colors.neutral[600], fontSize: 13 }}>
                {tip}
              </Text>
            </div>
          ))}
        </div>
      )}

      {/* Action buttons */}
      {(actionLabel && onAction) || secondaryAction ? (
        <Space direction="vertical" size="small" align="center">
          {actionLabel && onAction && (
            <Button
              type="primary"
              size="large"
              onClick={onAction}
            >
              {actionLabel}
            </Button>
          )}
          {secondaryAction && (
            <Button
              type="link"
              onClick={secondaryAction.onClick}
              style={{ color: tokens.colors.neutral[500] }}
            >
              {secondaryAction.label}
            </Button>
          )}
        </Space>
      ) : null}
    </div>
  );
}

export default EmptyState;
