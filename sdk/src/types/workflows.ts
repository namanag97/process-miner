/**
 * Workflows, Notifications, and Integrations Types
 */

import { HypermediaResponse } from './common.js';

// =============================================================================
// WORKFLOWS
// =============================================================================

export interface WorkflowPipeline extends HypermediaResponse {
  name: string;
  description: string;
  steps: string[];
}

export interface WorkflowExecution extends HypermediaResponse {
  id: string;
  pipelineName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt: string;
  completedAt?: string;
  result?: unknown;
  error?: string;
}

export interface StartWorkflowOptions {
  pipelineName: string;
  logId: string;
  parameters?: Record<string, unknown>;
}

// =============================================================================
// NOTIFICATIONS
// =============================================================================

export type NotificationChannel = 'email' | 'webhook' | 'slack';

export interface SendNotificationOptions {
  channel: NotificationChannel;
  recipient: string;
  subject: string;
  body: string;
}

export interface Notification extends HypermediaResponse {
  id: string;
  channel: NotificationChannel;
  recipient: string;
  subject: string;
  status: 'pending' | 'sent' | 'failed';
  createdAt: string;
}

export interface NotificationChannelInfo {
  name: string;
  type: NotificationChannel;
  description: string;
  configured: boolean;
}

// =============================================================================
// INTEGRATIONS
// =============================================================================

export type ConnectorType = 'sap' | 'salesforce' | 'servicenow' | 'database' | 'file';

export interface ConnectorTypeInfo extends HypermediaResponse {
  type: ConnectorType;
  name: string;
  description: string;
  requiredSettings: string[];
}

export interface Connector extends HypermediaResponse {
  id: string;
  name: string;
  connectorType: ConnectorType;
  status: 'connected' | 'disconnected' | 'error';
  settings: Record<string, unknown>;
  createdAt: string;
  lastSyncAt?: string;
}

export interface CreateConnectorOptions {
  name: string;
  connectorType: ConnectorType;
  settings: Record<string, unknown>;
}

export interface SyncResult extends HypermediaResponse {
  connectorId: string;
  status: 'success' | 'failed';
  recordsImported: number;
  syncedAt: string;
  error?: string;
}
