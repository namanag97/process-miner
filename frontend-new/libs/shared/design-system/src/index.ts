// Theme
export { luminaTheme, luminaDarkTheme, tokens } from './theme';
export type { LuminaTokens } from './theme';

// Components
export {
  AppShell,
  MetricCard,
  EmptyState,
  PageHeader,
  SkeletonCard,
  ErrorBoundary,
  useErrorBoundary,
  QueryError,
  getErrorMessage,
  isNetworkError,
  LoadingState,
  MetricsLoadingState,
  TableLoadingState,
  PageLoadingState,
  DetailLoadingState,
  ProcessQuestion,
  DataTable,
  DataSourceCard,
} from './components';
export type {
  AppShellProps,
  NavItem,
  MetricCardProps,
  EmptyStateProps,
  PageHeaderProps,
  SkeletonCardProps,
  ErrorBoundaryProps,
  QueryErrorProps,
  QueryErrorVariant,
  LoadingStateProps,
  LoadingStateType,
  ProcessQuestionProps,
  DataTableProps,
  DataTableColumn,
  DataSourceCardProps,
  DataSourceInfo,
} from './components';

// Utils
export {
  toast,
  notify,
  formatDuration,
  formatDurationFromSeconds,
  formatCompactNumber,
  formatPercentage,
} from './utils';
export {
  devLog,
  logAction,
  logRequest,
  logResponse,
  logError,
  flushDevLogs,
} from './utils/devLogger';

// Context
export { SDKProvider, useSDK, queryClient } from './context/SDKContext';

// API Client
export { APIError, API_ERRORS, validateApiResponse } from './api/client';
export type { ApiClientConfig, RequestOptions } from './api/client';

// Query Keys
export { queryKeys, invalidationKeys, getInvalidationKey } from './api/queryKeys';
export type {
  QueryKeys,
  QueryKeyOf,
  QueryKeyPrefix,
  ListProcessesOptions,
  DFGOptions,
  VariantOptions,
  AuditFilters,
} from './api/queryKeys';

// Zod Schemas (selective exports for common use cases)
export { validateResponse, safeValidateResponse } from './api/schemas';
export type { PaginatedResponse, DateRange, Severity, Status } from './api/schemas';

// API Types and Transformers
export * from './api/transformers';
export type { ColumnDetectionResponse } from './api/types';
export type { ProcessSummaryData, PatternResponse } from './api/modules/analytics';

// Query Hooks
export {
  // Projects
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  useAddFileToProject,
  useRemoveFileFromProject,
  // Processes
  useProcesses,
  useProcess,
  useProjectProcesses,
  useUploadProcess,
  useDeleteProcess,
  useDetectColumns,
  useProcessStatistics,
  // Discovery
  useDFG,
  useVariants,
  useActivities,
  useDiscoverProcess,
  useExplorerData,
  // Analytics
  usePerformance,
  useRework,
  useBottlenecks,
  useCycleTime,
  useThroughput,
  usePatterns,
  useProcessSummary,
  useDeadlines,
  useAutomation,
  useKPIData,
  // Audit
  useAuditLogs,
  useLogAuditEvent,
} from './hooks';
export type { AuditLogEntry } from './hooks';

