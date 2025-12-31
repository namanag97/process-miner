/**
 * IntegrationPanel - Third-party integrations display and management
 *
 * Shows connected integrations, their status, and configuration options.
 * Supports various integration types like Slack, Jira, email, webhooks, etc.
 *
 * @example
 * <IntegrationPanel
 *   integrations={connectedIntegrations}
 *   onConnect={(type) => openConnectionFlow(type)}
 *   onDisconnect={(id) => handleDisconnect(id)}
 * />
 */

import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Space,
  Typography,
  Tag,
  Badge,
  Switch,
  Tooltip,
  Empty,
  Modal,
  Divider,
  List,
} from 'antd';
import {
  ApiOutlined,
  SlackOutlined,
  MailOutlined,
  GithubOutlined,
  LinkOutlined,
  SettingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  PlusOutlined,
  DisconnectOutlined,
  CloudOutlined,
  ToolOutlined,
  BellOutlined,
} from '@ant-design/icons';
import { StatusBadge, type ObjectStatus } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title, Paragraph } = Typography;

// ============================================
// Types
// ============================================

export type IntegrationType =
  | 'slack'
  | 'teams'
  | 'email'
  | 'jira'
  | 'servicenow'
  | 'webhook'
  | 'zapier'
  | 'power_automate'
  | 's3'
  | 'azure_blob'
  | 'custom';

export type IntegrationCategory = 'communication' | 'ticketing' | 'automation' | 'storage';

export interface Integration {
  id: string;
  type: IntegrationType;
  name: string;
  description?: string;
  status: ObjectStatus;
  enabled: boolean;
  lastSyncAt?: Date;
  config?: Record<string, any>;
  errorMessage?: string;
}

export interface IntegrationTypeInfo {
  type: IntegrationType;
  name: string;
  description: string;
  icon: React.ReactNode;
  category: IntegrationCategory;
  docsUrl?: string;
}

export interface IntegrationPanelProps {
  /** Connected integrations */
  integrations: Integration[];
  /** Connect new integration handler */
  onConnect?: (type: IntegrationType) => void;
  /** Disconnect integration handler */
  onDisconnect?: (integrationId: string) => void;
  /** Configure integration handler */
  onConfigure?: (integration: Integration) => void;
  /** Toggle integration enabled state */
  onToggleEnabled?: (integrationId: string, enabled: boolean) => void;
  /** Sync integration handler */
  onSync?: (integrationId: string) => void;
  /** Loading state */
  loading?: boolean;
  /** Show available integrations to connect */
  showAvailable?: boolean;
}

// ============================================
// Configuration
// ============================================

const INTEGRATION_TYPES: IntegrationTypeInfo[] = [
  {
    type: 'slack',
    name: 'Slack',
    description: 'Send alerts and notifications to Slack channels',
    icon: <SlackOutlined />,
    category: 'communication',
  },
  {
    type: 'teams',
    name: 'Microsoft Teams',
    description: 'Send alerts to Microsoft Teams channels',
    icon: <ApiOutlined />,
    category: 'communication',
  },
  {
    type: 'email',
    name: 'Email (SMTP)',
    description: 'Send email notifications via SMTP',
    icon: <MailOutlined />,
    category: 'communication',
  },
  {
    type: 'jira',
    name: 'Jira',
    description: 'Create and manage Jira issues automatically',
    icon: <ToolOutlined />,
    category: 'ticketing',
  },
  {
    type: 'servicenow',
    name: 'ServiceNow',
    description: 'Create incidents and requests in ServiceNow',
    icon: <ToolOutlined />,
    category: 'ticketing',
  },
  {
    type: 'webhook',
    name: 'Webhook',
    description: 'Send data to custom HTTP endpoints',
    icon: <LinkOutlined />,
    category: 'automation',
  },
  {
    type: 'zapier',
    name: 'Zapier',
    description: 'Connect to 5000+ apps via Zapier',
    icon: <ApiOutlined />,
    category: 'automation',
  },
  {
    type: 'power_automate',
    name: 'Power Automate',
    description: 'Trigger Microsoft Power Automate flows',
    icon: <ApiOutlined />,
    category: 'automation',
  },
  {
    type: 's3',
    name: 'Amazon S3',
    description: 'Export data to Amazon S3 buckets',
    icon: <CloudOutlined />,
    category: 'storage',
  },
  {
    type: 'azure_blob',
    name: 'Azure Blob Storage',
    description: 'Export data to Azure Blob Storage',
    icon: <CloudOutlined />,
    category: 'storage',
  },
];

const CATEGORY_LABELS: Record<IntegrationCategory, string> = {
  communication: 'Communication',
  ticketing: 'Ticketing & ITSM',
  automation: 'Automation',
  storage: 'Cloud Storage',
};

const CATEGORY_ICONS: Record<IntegrationCategory, React.ReactNode> = {
  communication: <BellOutlined />,
  ticketing: <ToolOutlined />,
  automation: <ApiOutlined />,
  storage: <CloudOutlined />,
};

// ============================================
// Helpers
// ============================================

function getIntegrationInfo(type: IntegrationType): IntegrationTypeInfo | undefined {
  return INTEGRATION_TYPES.find((t) => t.type === type);
}

function formatLastSync(date: Date | undefined): string {
  if (!date) return 'Never';
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
}

// ============================================
// IntegrationCard Component
// ============================================

interface IntegrationCardProps {
  integration: Integration;
  onConfigure?: () => void;
  onDisconnect?: () => void;
  onToggleEnabled?: (enabled: boolean) => void;
  onSync?: () => void;
}

function IntegrationCard({
  integration,
  onConfigure,
  onDisconnect,
  onToggleEnabled,
  onSync,
}: IntegrationCardProps) {
  const typeInfo = getIntegrationInfo(integration.type);
  const isConnected = integration.status === 'active' || integration.status === 'completed';
  const hasError = integration.status === 'failed';

  return (
    <Card
      className="card-hover-lift"
      style={{
        borderLeft: `4px solid ${
          hasError
            ? tokens.colors.error[500]
            : isConnected
            ? tokens.colors.success[500]
            : tokens.colors.neutral[300]
        }`,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Space>
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: tokens.radius.md,
              backgroundColor: tokens.colors.neutral[100],
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 20,
              color: tokens.colors.neutral[600],
            }}
          >
            {typeInfo?.icon}
          </div>
          <div>
            <Title level={5} style={{ margin: 0 }}>
              {integration.name}
            </Title>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
              {typeInfo?.name}
            </Text>
          </div>
        </Space>
        <Space>
          <StatusBadge status={integration.status} size="small" />
          {onToggleEnabled && (
            <Switch
              size="small"
              checked={integration.enabled}
              onChange={onToggleEnabled}
              disabled={hasError}
            />
          )}
        </Space>
      </div>

      {hasError && integration.errorMessage && (
        <div
          style={{
            marginTop: tokens.spacing[3],
            padding: tokens.spacing[2],
            backgroundColor: tokens.colors.error[50],
            borderRadius: tokens.radius.sm,
          }}
        >
          <Text type="danger" style={{ fontSize: tokens.fontSize.xs }}>
            {integration.errorMessage}
          </Text>
        </div>
      )}

      <Divider style={{ margin: `${tokens.spacing[3]}px 0` }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
          Last sync: {formatLastSync(integration.lastSyncAt)}
        </Text>
        <Space size={4}>
          {onSync && (
            <Tooltip title="Sync now">
              <Button type="text" size="small" icon={<SyncOutlined />} onClick={onSync} />
            </Tooltip>
          )}
          {onConfigure && (
            <Tooltip title="Configure">
              <Button type="text" size="small" icon={<SettingOutlined />} onClick={onConfigure} />
            </Tooltip>
          )}
          {onDisconnect && (
            <Tooltip title="Disconnect">
              <Button
                type="text"
                size="small"
                danger
                icon={<DisconnectOutlined />}
                onClick={onDisconnect}
              />
            </Tooltip>
          )}
        </Space>
      </div>
    </Card>
  );
}

// ============================================
// IntegrationPanel Component
// ============================================

export function IntegrationPanel({
  integrations,
  onConnect,
  onDisconnect,
  onConfigure,
  onToggleEnabled,
  onSync,
  loading = false,
  showAvailable = true,
}: IntegrationPanelProps) {
  const [connectModalOpen, setConnectModalOpen] = useState(false);

  const connectedTypes = new Set(integrations.map((i) => i.type));
  const availableIntegrations = INTEGRATION_TYPES.filter((t) => !connectedTypes.has(t.type));

  const categories: IntegrationCategory[] = ['communication', 'ticketing', 'automation', 'storage'];

  const handleConnect = (type: IntegrationType) => {
    onConnect?.(type);
    setConnectModalOpen(false);
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing[6],
        }}
      >
        <div>
          <Title level={4} style={{ margin: 0 }}>
            <ApiOutlined style={{ marginRight: tokens.spacing[2] }} />
            Integrations
          </Title>
          <Text type="secondary">
            {integrations.length} connected · {availableIntegrations.length} available
          </Text>
        </div>
        {onConnect && showAvailable && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setConnectModalOpen(true)}>
            Add Integration
          </Button>
        )}
      </div>

      {/* Connected Integrations */}
      {integrations.length === 0 ? (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No integrations connected"
          >
            {onConnect && (
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setConnectModalOpen(true)}>
                Connect Your First Integration
              </Button>
            )}
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {integrations.map((integration) => (
            <Col xs={24} sm={12} lg={8} key={integration.id}>
              <IntegrationCard
                integration={integration}
                onConfigure={onConfigure ? () => onConfigure(integration) : undefined}
                onDisconnect={onDisconnect ? () => onDisconnect(integration.id) : undefined}
                onToggleEnabled={
                  onToggleEnabled ? (enabled) => onToggleEnabled(integration.id, enabled) : undefined
                }
                onSync={onSync ? () => onSync(integration.id) : undefined}
              />
            </Col>
          ))}
        </Row>
      )}

      {/* Connect Modal */}
      <Modal
        title="Add Integration"
        open={connectModalOpen}
        onCancel={() => setConnectModalOpen(false)}
        footer={null}
        width={720}
      >
        {categories.map((category) => {
          const categoryIntegrations = availableIntegrations.filter((i) => i.category === category);
          if (categoryIntegrations.length === 0) return null;

          return (
            <div key={category} style={{ marginBottom: tokens.spacing[6] }}>
              <Space style={{ marginBottom: tokens.spacing[3] }}>
                {CATEGORY_ICONS[category]}
                <Text strong>{CATEGORY_LABELS[category]}</Text>
              </Space>
              <Row gutter={[12, 12]}>
                {categoryIntegrations.map((integration) => (
                  <Col xs={12} sm={8} key={integration.type}>
                    <Card
                      hoverable
                      onClick={() => handleConnect(integration.type)}
                      className="card-hover-lift"
                      style={{ textAlign: 'center' }}
                      styles={{ body: { padding: tokens.spacing[4] } }}
                    >
                      <div
                        style={{
                          fontSize: 28,
                          color: tokens.colors.primary[500],
                          marginBottom: tokens.spacing[2],
                        }}
                      >
                        {integration.icon}
                      </div>
                      <Text strong style={{ display: 'block' }}>
                        {integration.name}
                      </Text>
                      <Text
                        type="secondary"
                        style={{ fontSize: tokens.fontSize.xs, display: 'block' }}
                        ellipsis
                      >
                        {integration.description}
                      </Text>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          );
        })}
      </Modal>
    </div>
  );
}

export default IntegrationPanel;
