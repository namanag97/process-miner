/**
 * Event Log Types for Process Mining SDK
 * Business-focused types following CodeOpinion guidance
 */

import { HypermediaResponse, PaginatedResponse, DateRange } from "./common.js";

// =============================================================================
// CORE ENTITIES
// =============================================================================

/**
 * Event log summary with available operations
 */
export interface EventLog extends HypermediaResponse {
  id: string;
  name: string;
  sourceFile?: string;
  totalCases: number;
  totalEvents: number;
  createdAt: string;
}

/**
 * Detailed event log with full metadata
 */
export interface EventLogDetails extends EventLog {
  uniqueActivities: number;
  uniqueResources: number;
  variantCount: number;
  dateRange?: DateRange;
  description?: string;
}

// =============================================================================
// BUSINESS OPERATION INPUTS
// =============================================================================

/**
 * Options when ingesting a new event log
 */
export interface IngestLogOptions {
  name?: string;
  caseIdColumn?: string;
  activityColumn?: string;
  timestampColumn?: string;
  resourceColumn?: string;
}

/**
 * Options when updating event log metadata
 */
export interface UpdateLogMetadata {
  name?: string;
  description?: string;
}

// =============================================================================
// BUSINESS OPERATION OUTPUTS
// =============================================================================

/**
 * Result of log ingestion operation
 */
export interface IngestionResult extends HypermediaResponse {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  validation: {
    isValid: boolean;
    errors: string[];
    warnings: string[];
  };
}

/**
 * Column detection result for CSV files
 */
export interface ColumnDetection extends HypermediaResponse {
  columns: string[];
  suggestions: {
    caseId?: string;
    activity?: string;
    timestamp?: string;
    resource?: string;
  };
  sampleRows: Record<string, unknown>[];
}

/**
 * File preview before ingestion
 */
export interface FilePreview extends HypermediaResponse {
  filename: string;
  fileFormat: string;
  columns: string[];
  columnTypes: Record<string, string>;
  suggestions: {
    caseId?: string;
    activity?: string;
    timestamp?: string;
    resource?: string;
  };
  sampleRows: Record<string, unknown>[];
  rowCount: number;
  estimatedCaseCount: number;
  estimatedEventCount: number;
}

/**
 * Log statistics analysis result
 */
export interface LogStatistics extends HypermediaResponse {
  logId: string;
  eventCount: number;
  caseCount: number;
  activityCount: number;
  variantCount: number;
  resourceCount: number;
  dateRange?: DateRange;
  avgCaseDurationSeconds?: number;
  medianCaseDurationSeconds?: number;
  minCaseDurationSeconds?: number;
  maxCaseDurationSeconds?: number;
  activities: string[];
  startActivities: Record<string, number>;
  endActivities: Record<string, number>;
}

/**
 * Quality issue found in log
 */
export interface QualityIssue {
  issueType: string;
  message: string;
  severity: "error" | "warning" | "info";
  affectedRows: number;
  column?: string;
}

/**
 * Log quality assessment result
 */
export interface QualityReport extends HypermediaResponse {
  logId: string;
  completenessScore: number;
  validityScore: number;
  overallScore: number;
  isValid: boolean;
  issues: QualityIssue[];
}

/**
 * Process variant with frequency and performance
 */
export interface ProcessVariant {
  key: string;
  activities: string[];
  caseCount: number;
  length: number;
  frequencyPercent?: number;
  avgDurationSeconds?: number;
  isHappyPath?: boolean;
}

// =============================================================================
// PAGINATED RESPONSES
// =============================================================================

export type PaginatedLogs = PaginatedResponse<EventLog>;
