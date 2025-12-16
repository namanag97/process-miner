/**
 * API Module
 * 
 * Re-exports all API functions and types from a single entry point.
 */

// Types (single source of truth)
export type {
    ColumnMetadata,
    UploadResponse,
    MappingCreate,
    MappingResponse,
    ValidationError,
    ValidationWarning,
    ValidationStats,
    ValidationResult,
    JobStatus,
    JobResponse,
    ActivityNodeData,
    DFGNode,
    DFGEdge,
    DFGSummary,
    DFGResponse,
    VariantItem,
    VariantsResponse,
    ProcessStats,
    DatasetSummary,
    Deviation,
    FullAnalysisResponse,
    Organization,
    OrganizationCreate,
    Process,
    ProcessCreate,
    ProcessUpdate,
    InsightType,
    SeverityLevel,
    Insight,
    InsightSummary,
    AuditAction,
    AuditLog,
} from './types';

// API Functions
export {
    ApiError,
    uploadFile,
    getUpload,
    deleteUpload,
    createMapping,
    getMapping,
    validateMapping,
    startProcessing,
    getJobStatus,
    waitForJob,
    getDFG,
    getVariants,
    getSummary,
    getFullAnalysis,
    getDeviations,
    healthCheck,
    createUser,
    getCurrentUser,
} from './client';

// React Query Hooks
export * from './queries';
