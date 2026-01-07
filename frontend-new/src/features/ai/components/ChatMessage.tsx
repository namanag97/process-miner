import React from 'react';
import { Typography, Space, Spin } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import { tokens } from '@/src/shared/design-system';
import type { ChatMessage as ChatMessageType } from '../types';

const { Text, Paragraph } = Typography;

interface ChatMessageProps {
  message: ChatMessageType;
}

const userBubbleStyle: React.CSSProperties = {
  background: `linear-gradient(135deg, ${tokens.colors.primary[500]}, ${tokens.colors.primary[600]})`,
  color: 'white',
  padding: '12px 16px',
  borderRadius: '18px 18px 4px 18px',
  maxWidth: '75%',
  marginLeft: 'auto',
  boxShadow: '0 2px 8px rgba(99, 102, 241, 0.25)',
};

const assistantBubbleStyle: React.CSSProperties = {
  background: 'rgba(255, 255, 255, 0.08)',
  backdropFilter: 'blur(10px)',
  border: `1px solid ${tokens.colors.neutral[200]}`,
  padding: '12px 16px',
  borderRadius: '18px 18px 18px 4px',
  maxWidth: '85%',
  boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
};

const avatarStyle = (isUser: boolean): React.CSSProperties => ({
  width: 32,
  height: 32,
  borderRadius: '50%',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: isUser
    ? `linear-gradient(135deg, ${tokens.colors.primary[500]}, ${tokens.colors.primary[600]})`
    : `linear-gradient(135deg, ${tokens.colors.success[500]}, ${tokens.colors.success[600]})`,
  color: 'white',
  fontSize: 14,
  flexShrink: 0,
});

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isLoading = message.isLoading;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        gap: 12,
        marginBottom: 16,
        animation: 'fadeInUp 0.3s ease-out',
      }}
    >
      <div style={avatarStyle(isUser)}>
        {isUser ? <UserOutlined /> : <RobotOutlined />}
      </div>

      <div style={isUser ? userBubbleStyle : assistantBubbleStyle}>
        {isLoading ? (
          <Space>
            <Spin size="small" />
            <Text type="secondary">Thinking...</Text>
          </Space>
        ) : (
          <>
            <Paragraph
              style={{
                margin: 0,
                color: isUser ? 'white' : 'inherit',
                whiteSpace: 'pre-wrap',
              }}
            >
              {message.content}
            </Paragraph>
            <Text
              type="secondary"
              style={{
                fontSize: 11,
                display: 'block',
                marginTop: 8,
                opacity: 0.7,
                color: isUser ? 'rgba(255,255,255,0.7)' : undefined,
              }}
            >
              {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </Text>
          </>
        )}
      </div>
    </div>
  );
}

// Keyframes for animation (inject via style tag or CSS)
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
if (!document.querySelector('[data-chat-animations]')) {
  styleSheet.setAttribute('data-chat-animations', 'true');
  document.head.appendChild(styleSheet);
}

export default ChatMessage;
