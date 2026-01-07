/**
 * Audit Hooks - React Query hooks for audit log operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSDK } from '../context/SDKContext';
import { queryKeys } from '../api/queryKeys';
import type { AuditEventType } from '../api/modules/audit';

// Re-export for convenience
export type { AuditEventType };

export interface AuditFilters {
  startDate?: string;
  endDate?: string;
  eventType?: AuditEventType;
  userId?: string;
  page?: number;
  pageSize?: number;
}

export interface AuditLogEntry {
  id: string;
  event: string;
  userId: string;
  userName: string;
  timestamp: string;
  data: Record<string, unknown>;
  ipAddress?: string;
}

/**
 * Get audit logs with optional filters
 * Uses the audit SDK module to fetch real data
 */
export function useAuditLogs(filters?: AuditFilters) {
  const sdk = useSDK();
  
  return useQuery({
    queryKey: queryKeys.audit.logs(filters),
    queryFn: async () => {
      const response = await sdk.audit.list({
        startDate: filters?.startDate,
        endDate: filters?.endDate,
        eventType: filters?.eventType,
        userId: filters?.userId,
        page: filters?.page,
        pageSize: filters?.pageSize,
      });
      
      // Transform to expected format
      return {
        items: response.items.map(item => ({
          id: item.id,
          event: item.event,
          userId: item.userId,
          userName: item.userEmail,
          timestamp: item.timestamp,
          data: item.data,
          ipAddress: item.ipAddress,
        })) as AuditLogEntry[],
        total: response.total,
      };
    },
    staleTime: 1 * 60 * 1000, // 1 minute - audit logs should be relatively fresh
  });
}

/**
 * Log an audit event
 * Uses the audit SDK module to log events
 */
export function useLogAuditEvent() {
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (event: { 
      event: string; 
      data: Record<string, unknown>;
    }): Promise<void> => {
      await sdk.audit.log({
        event: event.event as Parameters<typeof sdk.audit.log>[0]['event'],
        data: event.data,
      });
    },
    onSuccess: () => {
      // Invalidate audit logs to show new entry
      queryClient.invalidateQueries({ queryKey: queryKeys.audit.logs() });
    },
  });
}
