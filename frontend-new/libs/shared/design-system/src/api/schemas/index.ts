/**
 * Zod Schemas - Central export for all API validation schemas
 */

// Common utilities and types
export {
  PaginatedResponseSchema,
  DateRangeSchema,
  APIErrorDetailSchema,
  APIErrorResponseSchema,
  SeveritySchema,
  StatusSchema,
  validateResponse,
  safeValidateResponse,
  type PaginatedResponse,
  type DateRange,
  type APIErrorResponse,
  type Severity,
  type Status,
} from './common';

// Process/Event Log schemas
export {
  ProcessResponseSchema,
  ProcessDetailResponseSchema,
  ColumnSuggestionsSchema,
  ColumnDetectionResponseSchema,
  StatisticsResponseSchema,
  ProcessListResponseSchema,
  UploadResponseSchema,
  type ProcessResponse,
  type ProcessDetailResponse,
  type ColumnSuggestions,
  type ColumnDetectionResponse,
  type StatisticsResponse,
  type ProcessListResponse,
  type UploadResponse,
} from './processes';

// Discovery schemas (DFG, Variants, Activities)
export {
  DFGNodeResponseSchema,
  DFGEdgeResponseSchema,
  DFGResponseSchema,
  VariantResponseSchema,
  VariantListResponseSchema,
  ActivityDetailResponseSchema,
  ActivityListResponseSchema,
  DiscoveryModelResponseSchema,
  type DFGNodeResponse,
  type DFGEdgeResponse,
  type DFGResponse,
  type VariantResponse,
  type VariantListResponse,
  type ActivityDetailResponse,
  type ActivityListResponse,
  type DiscoveryModelResponse,
} from './discovery';

// Analytics schemas
export {
  BottleneckResponseSchema,
  BottleneckListResponseSchema,
  ReworkActivitySchema,
  ReworkResponseSchema,
  CycleTimeResponseSchema,
  ThroughputResponseSchema,
  PerformanceDashboardResponseSchema,
  PatternResponseSchema,
  PatternListResponseSchema,
  ProcessSummaryResponseSchema,
  type BottleneckResponse,
  type BottleneckListResponse,
  type ReworkActivity,
  type ReworkResponse,
  type CycleTimeResponse,
  type ThroughputResponse,
  type PerformanceDashboardResponse,
  type PatternResponse,
  type PatternListResponse,
  type ProcessSummaryResponse,
} from './analytics';

// Organizational schemas
export {
  NetworkNodeSchema,
  NetworkEdgeSchema,
  NetworkMetricsSchema,
  NetworkTypeSchema,
  SocialNetworkResponseSchema,
  ResourceRoleSchema,
  ResourceRoleListResponseSchema,
  ActivityPerformanceSchema,
  ResourceProfileResponseSchema,
  ResourceWorkloadSchema,
  WorkloadDistributionResponseSchema,
  type NetworkNode,
  type NetworkEdge,
  type NetworkMetrics,
  type NetworkType,
  type SocialNetworkResponse,
  type ResourceRole,
  type ResourceRoleListResponse,
  type ActivityPerformance,
  type ResourceProfileResponse,
  type ResourceWorkload,
  type WorkloadDistributionResponse,
} from './organizational';

// Project schemas
export {
  ProjectSchema,
  ProjectDetailSchema,
  CreateProjectSchema,
  UpdateProjectSchema,
  ProjectListResponseSchema,
  AddProcessToProjectSchema,
  type Project,
  type ProjectDetail,
  type CreateProject,
  type UpdateProject,
  type ProjectListResponse,
  type AddProcessToProject,
} from './projects';

// Predictions & Conformance schemas
export {
  PredictorResponseSchema,
  PredictorListResponseSchema,
  PredictionAlternativeSchema,
  PredictionResponseSchema,
  TrainPredictorRequestSchema,
  ConformanceResponseSchema,
  DeviationDetailSchema,
  DiagnosticsResponseSchema,
  InsightSchema,
  InsightsResponseSchema,
  type PredictorResponse,
  type PredictorListResponse,
  type PredictionAlternative,
  type PredictionResponse,
  type TrainPredictorRequest,
  type ConformanceResponse,
  type DeviationDetail,
  type DiagnosticsResponse,
  type Insight,
  type InsightsResponse,
} from './predictions';
