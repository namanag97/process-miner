import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Card, Input, Button, Space, Typography, Row, Col, Tooltip, Divider, Empty } from 'antd';
import {
  SendOutlined,
  ThunderboltOutlined,
  SyncOutlined,
  NodeIndexOutlined,
  RocketOutlined,
  WarningOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader, EmptyState, tokens } from '@lumina/design-system';
import { FeaturePage } from '../../../shared/core';
import { ProcessSelector, type ProcessOption } from '../components/ProcessSelector';
import { ChatMessage } from '../components/ChatMessage';
import { InsightCard } from '../components/InsightCard';
import { ChatMessage as ChatMessageType, DEFAULT_PROMPTS } from '../types';
import { useAIProcesses, useAIProcessSummary, useSendAIMessage } from '../hooks';

const { Text, Title } = Typography;

// Icon mapping for prompt suggestions
const iconComponents: Record<string, React.ReactNode> = {
  ThunderboltOutlined: <ThunderboltOutlined />,
  SyncOutlined: <SyncOutlined />,
  NodeIndexOutlined: <NodeIndexOutlined />,
  RocketOutlined: <RocketOutlined />,
  WarningOutlined: <WarningOutlined />,
  FileTextOutlined: <FileTextOutlined />,
};

function generateId(): string {
  return `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

export function AIAssistantPage() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId?: string }>();
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Data fetching with React Query hooks
  const {
    data: processesData,
    isLoading: processesLoading,
    error: processesError,
    refetch: refetchProcesses,
  } = useAIProcesses({ pageSize: 100 });

  // AI Chat mutation
  const { mutate: sendAIMessage, isPending: isLoading } = useSendAIMessage();

  // Local state
  const [selectedProcessId, setSelectedProcessId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputValue, setInputValue] = useState('');

  // Fetch process summary when selection changes
  const {
    data: processSummary,
    isLoading: summaryLoading,
  } = useAIProcessSummary(selectedProcessId || '');

  // Transform processes data to ProcessOption[]
  const processes = useMemo<ProcessOption[]>(() => {
    if (!processesData?.items) return [];
    return processesData.items.map((p) => ({
      id: p.id,
      name: p.name,
      totalCases: p.totalCases,
      totalActivities: p.totalActivities,
      sourceFormat: p.sourceFormat,
    }));
  }, [processesData]);

  // Add welcome message when summary loads
  useEffect(() => {
    if (processSummary && selectedProcessId) {
      const selectedProcess = processes.find((p) => p.id === selectedProcessId);
      setMessages([
        {
          id: generateId(),
          role: 'assistant',
          content: `I'm ready to help you analyze the **${selectedProcess?.name || 'process'}**. I have access to performance metrics, bottleneck analysis, rework patterns, and more.\n\nAsk me anything about this process, or try one of the suggestions below!`,
          timestamp: new Date(),
        },
      ]);
    }
  }, [processSummary, selectedProcessId, processes]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleProcessSelect = useCallback((processId: string) => {
    setSelectedProcessId(processId);
    setMessages([]);
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!inputValue.trim() || !selectedProcessId || !processSummary) return;

    const userMessageContent = inputValue.trim();

    const userMessage: ChatMessageType = {
      id: generateId(),
      role: 'user',
      content: userMessageContent,
      timestamp: new Date(),
    };

    // Add user message and loading indicator
    setMessages((prev) => [
      ...prev,
      userMessage,
      {
        id: generateId(),
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isLoading: true,
      },
    ]);
    setInputValue('');

    // Build conversation history for context (last 10 messages)
    const conversationHistory = messages.slice(-10).map((msg) => ({
      role: msg.role as 'user' | 'assistant',
      content: msg.content,
      timestamp: msg.timestamp?.toISOString(),
    }));

    // Send message to backend API
    sendAIMessage(
      {
        datasetId: selectedProcessId,
        message: userMessageContent,
        conversationHistory,
      },
      {
        onSuccess: (response) => {
          setMessages((prev) => [
            ...prev.slice(0, -1), // Remove loading message
            {
              id: generateId(),
              role: 'assistant',
              content: response.message,
              timestamp: new Date(),
              insights: response.insights,
            },
          ]);
        },
        onError: (error) => {
          console.error('[AI Chat] Error:', error);
          setMessages((prev) => [
            ...prev.slice(0, -1), // Remove loading message
            {
              id: generateId(),
              role: 'assistant',
              content: 'Sorry, I encountered an error processing your request. Please try again.',
              timestamp: new Date(),
            },
          ]);
        },
      }
    );
  }, [inputValue, selectedProcessId, processSummary, messages, sendAIMessage]);

  const handlePromptClick = useCallback((prompt: string) => {
    setInputValue(prompt);
  }, []);

  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
      }
    },
    [handleSendMessage]
  );

  // Error state
  if (processesError) {
    return (
      <FeaturePage
        title="AI Assistant"
        error={processesError}
        onRetry={() => refetchProcesses()}
      >
        {null}
      </FeaturePage>
    );
  }

  // Build breadcrumbs based on context
  const getBreadcrumbs = () => {
    if (projectId) {
      return [
        { label: 'Workspace', href: '/workspace' },
        { label: 'Project', href: `/workspace/${projectId}` },
        { label: 'AI Assistant' },
      ];
    }
    return [
      { label: 'AI', href: '/ai' },
      { label: 'Assistant' },
    ];
  };

  // Empty state when no processes
  if (!processesLoading && processes.length === 0) {
    return (
      <div>
        <PageHeader
          title="AI Assistant"
          description="Get intelligent insights about your processes"
          breadcrumb={getBreadcrumbs()}
        />
        <EmptyState
          icon={<FileTextOutlined />}
          title="No processes available"
          description="Upload an event log to start analyzing with AI"
          actionLabel="Go to Workspace"
          onAction={() => navigate(projectId ? `/workspace/${projectId}` : '/workspace')}
        />
      </div>
    );
  }

  return (
    <div style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <PageHeader
        title="AI Assistant"
        description="Ask questions about your processes and get data-driven insights"
        breadcrumb={getBreadcrumbs()}
        actions={
          <ProcessSelector
            processes={processes}
            selectedId={selectedProcessId}
            onSelect={handleProcessSelect}
            loading={processesLoading}
          />
        }
      />

      {!selectedProcessId ? (
        // Process selection prompt
        <Card
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: `linear-gradient(135deg, ${tokens.colors.primary[50]}, ${tokens.colors.neutral[50]})`,
            border: 'none',
          }}
        >
          <Empty
            image={<RocketOutlined style={{ fontSize: 64, color: tokens.colors.primary[400] }} />}
            description={
              <Space direction="vertical" size={8}>
                <Title level={4} style={{ margin: 0 }}>
                  Select a Process to Begin
                </Title>
                <Text type="secondary">
                  Choose a process from the dropdown above to start analyzing with AI
                </Text>
              </Space>
            }
          />
        </Card>
      ) : (
        <Row gutter={16} style={{ flex: 1, minHeight: 0 }}>
          {/* Main Chat Area */}
          <Col xs={24} lg={16} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Context Metrics Bar */}
            {processSummary && !summaryLoading && (
              <div
                style={{
                  display: 'flex',
                  gap: 12,
                  marginBottom: 16,
                  padding: '12px 16px',
                  background: `linear-gradient(135deg, ${tokens.colors.neutral[50]}, white)`,
                  borderRadius: 12,
                  border: `1px solid ${tokens.colors.neutral[100]}`,
                  overflowX: 'auto',
                }}
              >
                <Tooltip title="Total Cases">
                  <div style={{ textAlign: 'center', minWidth: 80 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>Cases</Text>
                    <br />
                    <Text strong>{processSummary.throughput.totalCases.toLocaleString()}</Text>
                  </div>
                </Tooltip>
                <Divider type="vertical" style={{ height: 'auto' }} />
                <Tooltip title="Average Cycle Time">
                  <div style={{ textAlign: 'center', minWidth: 80 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>Avg Cycle</Text>
                    <br />
                    <Text strong>{formatDuration(processSummary.cycleTime.avgSeconds)}</Text>
                  </div>
                </Tooltip>
                <Divider type="vertical" style={{ height: 'auto' }} />
                <Tooltip title="Bottlenecks Detected">
                  <div style={{ textAlign: 'center', minWidth: 80 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>Bottlenecks</Text>
                    <br />
                    <Text strong style={{ color: processSummary.bottlenecks.filter(b => b.isBottleneck).length > 0 ? tokens.colors.error[500] : tokens.colors.success[500] }}>
                      {processSummary.bottlenecks.filter(b => b.isBottleneck).length}
                    </Text>
                  </div>
                </Tooltip>
                <Divider type="vertical" style={{ height: 'auto' }} />
                <Tooltip title="Rework Rate">
                  <div style={{ textAlign: 'center', minWidth: 80 }}>
                    <Text type="secondary" style={{ fontSize: 11 }}>Rework</Text>
                    <br />
                    <Text strong style={{ color: processSummary.rework.reworkPercentage > 20 ? tokens.colors.warning[500] : undefined }}>
                      {processSummary.rework.reworkPercentage.toFixed(1)}%
                    </Text>
                  </div>
                </Tooltip>
              </div>
            )}

            {/* Chat Messages */}
            <Card
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                minHeight: 0,
                background: 'linear-gradient(180deg, #fafbfc 0%, #ffffff 100%)',
              }}
              bodyStyle={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                padding: 16,
                minHeight: 0,
              }}
            >
              {/* Messages Container */}
              <div
                ref={chatContainerRef}
                style={{
                  flex: 1,
                  overflowY: 'auto',
                  paddingRight: 8,
                  marginBottom: 16,
                }}
              >
                {summaryLoading ? (
                  <div style={{ textAlign: 'center', padding: 40 }}>
                    <SyncOutlined spin style={{ fontSize: 32, color: tokens.colors.primary[400] }} />
                    <br />
                    <Text type="secondary" style={{ marginTop: 12 }}>
                      Loading process data...
                    </Text>
                  </div>
                ) : (
                  messages.map((msg) => <ChatMessage key={msg.id} message={msg} />)
                )}
              </div>

              {/* Prompt Suggestions */}
              {messages.length <= 1 && !summaryLoading && (
                <div style={{ marginBottom: 16 }}>
                  <Text type="secondary" style={{ fontSize: 12, marginBottom: 8, display: 'block' }}>
                    Quick prompts:
                  </Text>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {DEFAULT_PROMPTS.map((prompt) => (
                      <Button
                        key={prompt.id}
                        size="small"
                        icon={iconComponents[prompt.icon]}
                        onClick={() => handlePromptClick(prompt.prompt)}
                        style={{
                          borderRadius: 16,
                          background: tokens.colors.neutral[50],
                          borderColor: tokens.colors.neutral[200],
                        }}
                      >
                        {prompt.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input Area */}
              <div style={{ display: 'flex', gap: 8 }}>
                <Input.TextArea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask about bottlenecks, patterns, rework, or anything else..."
                  autoSize={{ minRows: 1, maxRows: 4 }}
                  disabled={isLoading || summaryLoading}
                  style={{
                    borderRadius: 20,
                    resize: 'none',
                    paddingRight: 50,
                  }}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  loading={isLoading}
                  disabled={!inputValue.trim() || summaryLoading}
                  style={{
                    borderRadius: 20,
                    width: 48,
                    height: 40,
                  }}
                />
              </div>
            </Card>
          </Col>

          {/* Context Sidebar */}
          <Col xs={0} lg={8} style={{ height: '100%', overflowY: 'auto' }}>
            <Card
              title={
                <Space>
                  <InfoCircleOutlined />
                  <span>Process Context</span>
                </Space>
              }
              size="small"
              style={{ height: '100%' }}
            >
              {summaryLoading ? (
                <div style={{ textAlign: 'center', padding: 20 }}>
                  <SyncOutlined spin />
                </div>
              ) : processSummary ? (
                <Space direction="vertical" size={16} style={{ width: '100%' }}>
                  {/* Top Bottlenecks */}
                  {processSummary.bottlenecks.filter(b => b.isBottleneck).length > 0 && (
                    <div>
                      <Text strong style={{ fontSize: 13 }}>Top Bottlenecks</Text>
                      <div style={{ marginTop: 8 }}>
                        {processSummary.bottlenecks
                          .filter(b => b.isBottleneck)
                          .slice(0, 3)
                          .map((b, i) => (
                            <InsightCard
                              key={i}
                              compact
                              insight={{
                                type: 'bottleneck',
                                title: b.activity,
                                description: `Avg wait: ${formatDuration(b.avgWaitingTimeSeconds)}`,
                                severity: b.severity as 'high' | 'medium' | 'low',
                              }}
                            />
                          ))}
                      </div>
                    </div>
                  )}

                  {/* Rework Activities */}
                  {processSummary.rework.activities.length > 0 && (
                    <div>
                      <Text strong style={{ fontSize: 13 }}>Top Rework</Text>
                      <div style={{ marginTop: 8 }}>
                        {processSummary.rework.activities.slice(0, 3).map((r, i) => (
                          <InsightCard
                            key={i}
                            compact
                            insight={{
                              type: 'pattern',
                              title: r.activity,
                              description: `${r.reworkCount} occurrences (${r.reworkPercentage.toFixed(1)}%)`,
                              severity: r.reworkPercentage > 30 ? 'high' : r.reworkPercentage > 15 ? 'medium' : 'low',
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Patterns */}
                  {processSummary.patterns.length > 0 && (
                    <div>
                      <Text strong style={{ fontSize: 13 }}>Common Patterns</Text>
                      <div style={{ marginTop: 8 }}>
                        {processSummary.patterns.slice(0, 3).map((p, i) => (
                          <div
                            key={i}
                            style={{
                              padding: '8px 12px',
                              background: tokens.colors.neutral[50],
                              borderRadius: 8,
                              marginBottom: 8,
                            }}
                          >
                            <Text style={{ fontSize: 12 }}>
                              {p.pattern.join(' → ')}
                            </Text>
                            <br />
                            <Text type="secondary" style={{ fontSize: 11 }}>
                              Support: {(p.support * 100).toFixed(1)}%
                            </Text>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </Space>
              ) : (
                <Text type="secondary">Select a process to view context</Text>
              )}
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}

export default AIAssistantPage;
