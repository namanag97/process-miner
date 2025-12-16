/**
 * API Queries Index
 * 
 * Central export for all React Query hooks.
 */

// Organizations
export {
    useOrganizations,
    useOrganization,
    useCreateOrganization,
    useDeleteOrganization,
    type Organization,
    type OrganizationCreate,
} from './useOrganizations';

// Processes
export {
    useProcesses,
    useProcess,
    useCreateProcess,
    useUpdateProcess,
    useDeleteProcess,
    useProcessInsights,
    type Process,
    type ProcessWithStats,
    type ProcessCreate,
    type ProcessUpdate,
} from './useProcesses';

// Insights
export {
    useInsights,
    useInsightSummary,
    useDatasetInsights,
    useAcknowledgeInsight,
    useCriticalInsights,
    useUnacknowledgedInsights,
    type Insight,
    type InsightSummary,
} from './useInsights';

// Uploads
export {
    useUploadFile,
    useUpload,
    useDeleteUpload,
    uploadKeys,
} from './useUploads';

// Mapping & Processing
export {
    useCreateMapping,
    useMapping,
    useValidateMapping,
    useStartProcessing,
    useJobStatus,
    useProcessingFlow,
    mappingKeys,
    jobKeys,
} from './useMappingProcessing';

// Analysis
export {
    useDatasetDFG,
    useDatasetVariants,
    useDatasetSummary,
    useFullAnalysis,
    useDeviations,
    analysisKeys,
} from './useAnalysis';
