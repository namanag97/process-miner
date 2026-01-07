/**
 * SDK Bridge - Connects Design System to OpenAPI-generated SDK
 * 
 * This module initializes the OpenAPI SDK with configuration from the SDKProvider.
 * All design system modules should use this bridge for API calls.
 */

import { OpenAPI } from '@frontend-new/openapi-sdk';

// Re-export all services from OpenAPI SDK for use in modules
export {
    DatasetsService,
    DiscoveryService,
    ProjectsService,
    AnalyticsService,
    ConformanceService,
    VisualizationService,
    PredictionsService,
    OrganizationalMiningService,
    JobsService,
    FilteringService,
    AuthService,
    HealthService,
    WorkspacesService,
    ObjectCentricProcessMiningService,
    SimulationService,
    AnalysesService,
    BusinessUseCasesService,
} from '@frontend-new/openapi-sdk';

// Re-export types
export type {
    DatasetResponse,
    DatasetListResponse,
    DatasetDetailResponse,
    ProjectResponse,
    ProjectListResponse,
    DFGResponse,
    DFGNode,
    DFGEdge,
    StatisticsResponse,
    VariantResponse,
    ActivityDetailResponse,
    ColumnDetectionResponse,
    ConformanceResponse,
    ModelResponse,
    JobStatusResponse,
} from '@frontend-new/openapi-sdk';

/**
 * Configure the OpenAPI SDK with base URL and auth token.
 * Called by SDKProvider on mount.
 */
export function configureOpenAPISDK(options: {
    baseUrl: string;
    getAuthToken?: () => string | null;
}): void {
    OpenAPI.BASE = options.baseUrl;

    if (options.getAuthToken) {
        OpenAPI.TOKEN = async () => {
            const token = options.getAuthToken?.();
            return token ?? '';
        };
    }
}

/**
 * Get the current OpenAPI configuration (for debugging)
 */
export function getOpenAPIConfig() {
    return {
        BASE: OpenAPI.BASE,
        VERSION: OpenAPI.VERSION,
    };
}
