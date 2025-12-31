/**
 * Audit Module - SDK methods for audit logging operations
 */

import type { ApiClient } from '../client';

// Audit event types
export type AuditEventType =
  | 'project.created'
  | 'project.updated'
  | 'project.deleted'
  | 'file.uploaded'
  | 'file.deleted'
  | 'process.viewed'
  | 'process.exported'
  | 'analysis.run'
  | 'filter.applied'
  | 'settings.changed'
  | 'user.login'
  | 'user.logout';

export interface AuditLogEntry {
  id: string;
  userId: string;
  userEmail: string;
  event: AuditEventType;
  timestamp: string;
  data: Record<string, unknown>;
  ipAddress?: string;
  userAgent?: string;
}

export interface AuditFilters {
  startDate?: string;
  endDate?: string;
  eventType?: AuditEventType;
  userId?: string;
  page?: number;
  pageSize?: number;
}

export interface AuditLogResponse {
  items: AuditLogEntry[];
  total: number;
  page: number;
  pageSize: number;
  pages: number;
}

export interface CreateAuditLogData {
  event: AuditEventType;
  data: Record<string, unknown>;
}

export interface AuditModule {
  list: (filters?: AuditFilters) => Promise<AuditLogResponse>;
  log: (data: CreateAuditLogData) => Promise<void>;
  getStats: () => Promise<{ totalLogs: number; todayLogs: number; topEvents: { event: string; count: number }[] }>;
}

// API response types
interface AuditLogApiResponse {
  id: string;
  user_id: string;
  user_email: string;
  event: AuditEventType;
  timestamp: string;
  data: Record<string, unknown>;
  ip_address?: string;
  user_agent?: string;
}

interface AuditLogListApiResponse {
  items: AuditLogApiResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

function transformAuditLog(response: AuditLogApiResponse): AuditLogEntry {
  return {
    id: response.id,
    userId: response.user_id,
    userEmail: response.user_email,
    event: response.event,
    timestamp: response.timestamp,
    data: response.data,
    ipAddress: response.ip_address,
    userAgent: response.user_agent,
  };
}

export function createAuditModule(client: ApiClient): AuditModule {
  return {
    async list(filters?: AuditFilters): Promise<AuditLogResponse> {
      try {
        const response = await client.get<AuditLogListApiResponse>('/audit/logs', {
          start_date: filters?.startDate,
          end_date: filters?.endDate,
          event_type: filters?.eventType,
          user_id: filters?.userId,
          page: filters?.page ?? 1,
          page_size: filters?.pageSize ?? 50,
        });

        return {
          items: response.items.map(transformAuditLog),
          total: response.total,
          page: response.page,
          pageSize: response.page_size,
          pages: response.pages,
        };
      } catch (error) {
        // If audit endpoint doesn't exist yet, return empty
        console.warn('Audit logs endpoint not available:', error);
        return {
          items: [],
          total: 0,
          page: 1,
          pageSize: filters?.pageSize ?? 50,
          pages: 0,
        };
      }
    },

    async log(data: CreateAuditLogData): Promise<void> {
      try {
        await client.post('/audit/logs', {
          event: data.event,
          data: data.data,
        });
      } catch (error) {
        // Don't throw - audit logging should be non-blocking
        console.warn('Failed to log audit event:', error);
      }
    },

    async getStats(): Promise<{ totalLogs: number; todayLogs: number; topEvents: { event: string; count: number }[] }> {
      try {
        const response = await client.get<{
          total_logs: number;
          today_logs: number;
          top_events: { event: string; count: number }[];
        }>('/audit/stats');

        return {
          totalLogs: response.total_logs,
          todayLogs: response.today_logs,
          topEvents: response.top_events,
        };
      } catch (error) {
        console.warn('Audit stats endpoint not available:', error);
        return { totalLogs: 0, todayLogs: 0, topEvents: [] };
      }
    },
  };
}
