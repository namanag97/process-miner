import React from 'react';
import { Button, Typography } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { tokens } from '@lumina/design-system';

const { Title, Text } = Typography;

interface PlaceholderPageProps {
  title: string;
  phase?: number;
}

/**
 * PlaceholderPage - Shown for unimplemented features
 * Per INFORMATION_ARCHITECTURE.md spec
 */
export function PlaceholderPage({ title, phase = 2 }: PlaceholderPageProps) {
  const navigate = useNavigate();

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 200px)',
        textAlign: 'center',
        padding: tokens.spacing[6],
      }}
    >
      <div
        style={{
          fontSize: 64,
          marginBottom: tokens.spacing[4],
        }}
      >
        🚧
      </div>
      
      <Title level={2} style={{ marginBottom: tokens.spacing[2] }}>
        Coming Soon
      </Title>
      
      <Text
        style={{
          color: tokens.colors.neutral[500],
          fontSize: tokens.fontSize.lg,
          marginBottom: tokens.spacing[4],
          maxWidth: 400,
        }}
      >
        {title} is under development.
      </Text>
      
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          color: tokens.colors.neutral[400],
          marginBottom: tokens.spacing[6],
        }}
      >
        <ClockCircleOutlined />
        <Text type="secondary">Expected in Phase {phase}</Text>
      </div>
      
      <Button type="primary" onClick={() => navigate('/home')}>
        Back to Home
      </Button>
    </div>
  );
}

export default PlaceholderPage;
