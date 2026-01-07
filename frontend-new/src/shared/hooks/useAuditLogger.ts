/**
 * useAuditLogger - Hook for logging user actions to audit trail
 * Provides a simple interface for tracking important user events
 */

import { useCallback } from 'react';
import { useLogAuditEvent } from '@lumina/design-system';

export type AuditEventType =
  | 'project.created'
  | 'project.deleted'
  | 'project.updated'
  | 'process.uploaded'
  | 'process.deleted'
  | 'explorer.viewed'
  | 'kpi.viewed'
  | 'filter.applied'
  | 'variant.selected'
  | 'export.generated'
  | 'ai.query'
  | 'prediction.created';

interface AuditEventData {
  projectId?: string;
  processId?: string;
  datasetId?: string;
  fileName?: string;
  filterType?: string;
  filterValue?: unknown;
  tab?: string;
  query?: string;
  [key: string]: unknown;
}

/**
 * Hook for logging audit events
 * 
 * @example
 * ```tsx
 * const auditLog = useAuditLogger();
 * 
 * // Log a project creation
 * auditLog('project.created', { projectId: '123', name: 'My Project' });
 * 
 * // Log explorer view
 * auditLog('explorer.viewed', { projectId: '123', processId: 'abc' });
 * 
 * // Log filter application
 * auditLog('filter.applied', { datasetId: 'abc', filterType: 'frequency', filterValue: 10 });
 * ```
 */
export function useAuditLogger() {
  const { mutate: logEvent } = useLogAuditEvent();

  const log = useCallback(
    (event: AuditEventType, data: AuditEventData = {}) => {
      // Add timestamp and user context
      const enrichedData = {
        ...data,
        url: window.location.pathname,
        userAgent: navigator.userAgent,
      };

      logEvent({
        event,
        data: enrichedData,
      });
    },
    [logEvent]
  );

  return log;
}

/**
 * Convenience hooks for common audit events
 */
export function useProjectAuditLogger() {
  const log = useAuditLogger();

  return {
    logCreate: (projectId: string, name: string) =>
      log('project.created', { projectId, name }),
    logDelete: (projectId: string) =>
      log('project.deleted', { projectId }),
    logUpdate: (projectId: string, changes: Record<string, unknown>) =>
      log('project.updated', { projectId, changes }),
  };
}

export function useProcessAuditLogger() {
  const log = useAuditLogger();

  return {
    logUpload: (processId: string, fileName: string, projectId?: string) =>
      log('process.uploaded', { processId, fileName, projectId }),
    logDelete: (processId: string) =>
      log('process.deleted', { processId }),
  };
}

export function useExplorerAuditLogger() {
  const log = useAuditLogger();

  return {
    logView: (processId: string, projectId?: string) =>
      log('explorer.viewed', { processId, projectId }),
    logFilter: (datasetId: string, filterType: string, filterValue: unknown) =>
      log('filter.applied', { datasetId, filterType, filterValue }),
    logVariantSelect: (datasetId: string, variantKey: string) =>
      log('variant.selected', { datasetId, variantKey }),
    logExport: (datasetId: string, format: string) =>
      log('export.generated', { datasetId, format }),
  };
}

export function useKPIAuditLogger() {
  const log = useAuditLogger();

  return {
    logView: (processId: string, tab: string, projectId?: string) =>
      log('kpi.viewed', { processId, tab, projectId }),
  };
}
