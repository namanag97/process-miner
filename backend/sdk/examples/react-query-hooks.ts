/**
 * React Query Hooks for Process Mining SDK
 *
 * This file provides complete React Query hooks for all SDK services.
 * Copy this file to your project and customize as needed.
 *
 * Install dependencies:
 *   npm install @process-mining-saas/sdk @tanstack/react-query
 *
 * Setup:
 *   import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
 *   import { OpenAPI } from '@process-mining-saas/sdk';
 *
 *   OpenAPI.BASE = 'http://localhost:8001';
 *   const queryClient = new QueryClient();
 *
 *   // Wrap your app
 *   <QueryClientProvider client={queryClient}>
 *     <App />
 *   </QueryClientProvider>
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  UseQueryOptions,
  UseMutationOptions,
  useInfiniteQuery,
} from '@tanstack/react-query';

import {
  // Services
  ProcessesService,
  DiscoveryService,
  VisualizationService,
  ConformanceService,
  OcpmService,
  WorkflowsService,
  // Types
  ProcessResponse,
  ProcessListResponse,
  ProcessDetailResponse,
  StatisticsResponse,
  VariantResponse,
  CaseListResponse,
  ColumnDetectionResponse,
  MinerInfo,
  ModelResponse,
  ModelListResponse,
  DiscoverRequest,
  DFGResponse,
  PetriNetResponse,
  ConformanceResponse,
  ConformanceCheckRequest,
  DiagnosticsResponse,
  OCELLogResponse,
  OCELLogListResponse,
  OCELStatisticsResponse,
  OCPetriNetResponse,
  WorkflowTemplate,
  WorkflowResponse,
  WorkflowCreateRequest,
  WorkflowRunResponse,
  ApiError,
} from '@process-mining-saas/sdk';

// =============================================================================
// Query Keys
// =============================================================================

export const queryKeys = {
  processes: {
    all: ['processes'] as const,
    lists: () => [...queryKeys.processes.all, 'list'] as const,
    list: (filters: { page?: number; pageSize?: number; sourceFormat?: string }) =>
      [...queryKeys.processes.lists(), filters] as const,
    details: () => [...queryKeys.processes.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.processes.details(), id] as const,
    statistics: (id: string) => [...queryKeys.processes.detail(id), 'statistics'] as const,
    variants: (id: string) => [...queryKeys.processes.detail(id), 'variants'] as const,
    cases: (id: string) => [...queryKeys.processes.detail(id), 'cases'] as const,
  },
  discovery: {
    all: ['discovery'] as const,
    miners: () => [...queryKeys.discovery.all, 'miners'] as const,
    models: {
      all: () => [...queryKeys.discovery.all, 'models'] as const,
      list: (logId?: string) => [...queryKeys.discovery.models.all(), { logId }] as const,
      detail: (id: string) => [...queryKeys.discovery.models.all(), id] as const,
    },
  },
  visualization: {
    dfg: (logId: string) => ['visualization', 'dfg', logId] as const,
    petriNet: (modelId: string) => ['visualization', 'petri-net', modelId] as const,
  },
  conformance: {
    all: ['conformance'] as const,
    results: () => [...queryKeys.conformance.all, 'results'] as const,
    result: (id: string) => [...queryKeys.conformance.results(), id] as const,
    diagnostics: (id: string) => [...queryKeys.conformance.result(id), 'diagnostics'] as const,
    deviations: (id: string) => [...queryKeys.conformance.result(id), 'deviations'] as const,
  },
  ocel: {
    all: ['ocel'] as const,
    logs: () => [...queryKeys.ocel.all, 'logs'] as const,
    log: (id: string) => [...queryKeys.ocel.logs(), id] as const,
    statistics: (id: string) => [...queryKeys.ocel.log(id), 'statistics'] as const,
  },
  workflows: {
    all: ['workflows'] as const,
    templates: () => [...queryKeys.workflows.all, 'templates'] as const,
    list: () => [...queryKeys.workflows.all, 'list'] as const,
    detail: (id: string) => [...queryKeys.workflows.list(), id] as const,
    runs: (workflowId: string) => [...queryKeys.workflows.detail(workflowId), 'runs'] as const,
  },
} as const;

// =============================================================================
// PROCESSES HOOKS
// =============================================================================

/**
 * Fetch paginated list of processes
 */
export function useProcesses(
  filters: { page?: number; pageSize?: number; sourceFormat?: string } = {},
  options?: Omit<UseQueryOptions<ProcessListResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.processes.list(filters),
    queryFn: () =>
      ProcessesService.listProcesses({
        page: filters.page,
        pageSize: filters.pageSize,
        sourceFormat: filters.sourceFormat,
      }),
    ...options,
  });
}

/**
 * Fetch single process details
 */
export function useProcess(
  processId: string,
  options?: Omit<UseQueryOptions<ProcessDetailResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.processes.detail(processId),
    queryFn: () => ProcessesService.getProcess({ processId }),
    enabled: !!processId,
    ...options,
  });
}

/**
 * Fetch process statistics
 */
export function useProcessStatistics(
  processId: string,
  options?: Omit<UseQueryOptions<StatisticsResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.processes.statistics(processId),
    queryFn: () => ProcessesService.getStatistics({ processId }),
    enabled: !!processId,
    ...options,
  });
}

/**
 * Fetch process variants
 */
export function useProcessVariants(
  processId: string,
  topN: number = 20,
  options?: Omit<UseQueryOptions<VariantResponse[], ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.processes.variants(processId),
    queryFn: () => ProcessesService.getVariants({ processId, topN }),
    enabled: !!processId,
    ...options,
  });
}

/**
 * Fetch process cases with infinite scroll
 */
export function useProcessCasesInfinite(processId: string, pageSize: number = 50) {
  return useInfiniteQuery({
    queryKey: queryKeys.processes.cases(processId),
    queryFn: ({ pageParam = 1 }) =>
      ProcessesService.listCases({
        processId,
        page: pageParam,
        pageSize,
      }),
    initialPageParam: 1,
    getNextPageParam: (lastPage: CaseListResponse) => {
      if (lastPage.page < lastPage.pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    enabled: !!processId,
  });
}

/**
 * Upload process mutation
 */
export function useUploadProcess(
  options?: UseMutationOptions<
    ProcessResponse,
    ApiError,
    {
      file: File;
      name?: string;
      caseIdColumn?: string;
      activityColumn?: string;
      timestampColumn?: string;
      resourceColumn?: string;
    }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ file, name, caseIdColumn, activityColumn, timestampColumn, resourceColumn }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (name) formData.append('name', name);
      if (caseIdColumn) formData.append('case_id_column', caseIdColumn);
      if (activityColumn) formData.append('activity_column', activityColumn);
      if (timestampColumn) formData.append('timestamp_column', timestampColumn);
      if (resourceColumn) formData.append('resource_column', resourceColumn);

      return ProcessesService.uploadProcess({ formData });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.lists() });
    },
    ...options,
  });
}

/**
 * Detect columns mutation (for CSV files)
 */
export function useDetectColumns(
  options?: UseMutationOptions<ColumnDetectionResponse, ApiError, File>
) {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return ProcessesService.detectColumns({ formData });
    },
    ...options,
  });
}

/**
 * Delete process mutation
 */
export function useDeleteProcess(
  options?: UseMutationOptions<{ status: string; id: string }, ApiError, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (processId: string) => ProcessesService.deleteProcess({ processId }),
    onSuccess: (_, processId) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.processes.lists() });
      queryClient.removeQueries({ queryKey: queryKeys.processes.detail(processId) });
    },
    ...options,
  });
}

// =============================================================================
// DISCOVERY HOOKS
// =============================================================================

/**
 * Fetch available miners
 */
export function useMiners(
  options?: Omit<UseQueryOptions<MinerInfo[], ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.discovery.miners(),
    queryFn: () => DiscoveryService.listMiners(),
    staleTime: Infinity, // Miners don't change
    ...options,
  });
}

/**
 * Fetch models list
 */
export function useModels(
  logId?: string,
  options?: Omit<UseQueryOptions<ModelListResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.discovery.models.list(logId),
    queryFn: () => DiscoveryService.listModels({ logId }),
    ...options,
  });
}

/**
 * Fetch single model
 */
export function useModel(
  modelId: string,
  options?: Omit<UseQueryOptions<ModelResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.discovery.models.detail(modelId),
    queryFn: () => DiscoveryService.getModel({ modelId }),
    enabled: !!modelId,
    ...options,
  });
}

/**
 * Discover model mutation
 */
export function useDiscoverModel(
  options?: UseMutationOptions<ModelResponse, ApiError, DiscoverRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: DiscoverRequest) =>
      DiscoveryService.discoverModel({ requestBody: request }),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.discovery.models.list(variables.log_id),
      });
    },
    ...options,
  });
}

/**
 * Delete model mutation
 */
export function useDeleteModel(
  options?: UseMutationOptions<{ status: string; id: string }, ApiError, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (modelId: string) => DiscoveryService.deleteModel({ modelId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.discovery.models.all() });
    },
    ...options,
  });
}

// =============================================================================
// VISUALIZATION HOOKS
// =============================================================================

/**
 * Fetch DFG data
 */
export function useDFG(
  logId: string,
  options?: Omit<UseQueryOptions<DFGResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.visualization.dfg(logId),
    queryFn: () => VisualizationService.generateDfg({ logId }),
    enabled: !!logId,
    ...options,
  });
}

/**
 * Fetch Petri net structure
 */
export function usePetriNet(
  modelId: string,
  options?: Omit<UseQueryOptions<PetriNetResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.visualization.petriNet(modelId),
    queryFn: () => VisualizationService.getPetriNet({ modelId }),
    enabled: !!modelId,
    ...options,
  });
}

// =============================================================================
// CONFORMANCE HOOKS
// =============================================================================

/**
 * Fetch conformance result
 */
export function useConformanceResult(
  resultId: string,
  options?: Omit<UseQueryOptions<ConformanceResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.conformance.result(resultId),
    queryFn: () => ConformanceService.getResult({ resultId }),
    enabled: !!resultId,
    ...options,
  });
}

/**
 * Fetch conformance diagnostics
 */
export function useConformanceDiagnostics(
  resultId: string,
  options?: Omit<UseQueryOptions<DiagnosticsResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.conformance.diagnostics(resultId),
    queryFn: () => ConformanceService.getDiagnostics({ resultId }),
    enabled: !!resultId,
    ...options,
  });
}

/**
 * Check conformance mutation
 */
export function useCheckConformance(
  options?: UseMutationOptions<ConformanceResponse, ApiError, ConformanceCheckRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ConformanceCheckRequest) =>
      ConformanceService.checkConformance({ requestBody: request }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.conformance.results() });
    },
    ...options,
  });
}

// =============================================================================
// OCEL (Object-Centric) HOOKS
// =============================================================================

/**
 * Fetch OCEL logs list
 */
export function useOCELLogs(
  options?: Omit<UseQueryOptions<OCELLogListResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.ocel.logs(),
    queryFn: () => OcpmService.listOcelLogs(),
    ...options,
  });
}

/**
 * Fetch single OCEL log
 */
export function useOCELLog(
  logId: string,
  options?: Omit<UseQueryOptions<OCELLogResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.ocel.log(logId),
    queryFn: () => OcpmService.getOcelLog({ logId }),
    enabled: !!logId,
    ...options,
  });
}

/**
 * Fetch OCEL statistics
 */
export function useOCELStatistics(
  logId: string,
  options?: Omit<UseQueryOptions<OCELStatisticsResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.ocel.statistics(logId),
    queryFn: () => OcpmService.getOcelStatistics({ logId }),
    enabled: !!logId,
    ...options,
  });
}

/**
 * Upload OCEL file mutation
 */
export function useUploadOCEL(
  options?: UseMutationOptions<OCELLogResponse, ApiError, { file: File; name?: string }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ file, name }) => {
      const formData = new FormData();
      formData.append('file', file);
      if (name) formData.append('name', name);
      return OcpmService.uploadOcel({ formData });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ocel.logs() });
    },
    ...options,
  });
}

/**
 * Discover OC-Petri Net mutation
 */
export function useDiscoverOCPN(
  options?: UseMutationOptions<OCPetriNetResponse, ApiError, { logId: string; modelName?: string }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ logId, modelName }) =>
      OcpmService.discoverOcpn({
        requestBody: { log_id: logId, model_name: modelName },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.ocel.all });
    },
    ...options,
  });
}

// =============================================================================
// WORKFLOW HOOKS
// =============================================================================

/**
 * Fetch workflow templates
 */
export function useWorkflowTemplates(
  options?: Omit<UseQueryOptions<WorkflowTemplate[], ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.workflows.templates(),
    queryFn: () => WorkflowsService.listTemplates(),
    staleTime: Infinity, // Templates don't change
    ...options,
  });
}

/**
 * Fetch workflows list
 */
export function useWorkflows(
  options?: Omit<UseQueryOptions<WorkflowResponse[], ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.workflows.list(),
    queryFn: () => WorkflowsService.listWorkflows(),
    ...options,
  });
}

/**
 * Fetch single workflow
 */
export function useWorkflow(
  workflowId: string,
  options?: Omit<UseQueryOptions<WorkflowResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: queryKeys.workflows.detail(workflowId),
    queryFn: () => WorkflowsService.getWorkflow({ workflowId }),
    enabled: !!workflowId,
    ...options,
  });
}

/**
 * Create workflow mutation
 */
export function useCreateWorkflow(
  options?: UseMutationOptions<WorkflowResponse, ApiError, WorkflowCreateRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: WorkflowCreateRequest) =>
      WorkflowsService.createWorkflow({ requestBody: request }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.list() });
    },
    ...options,
  });
}

/**
 * Run workflow mutation
 */
export function useRunWorkflow(
  options?: UseMutationOptions<
    WorkflowRunResponse,
    ApiError,
    { workflowId: string; logId?: string; params?: Record<string, unknown> }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ workflowId, logId, params }) =>
      WorkflowsService.runWorkflow({
        workflowId,
        requestBody: { log_id: logId, params: params || {} },
      }),
    onSuccess: (_, { workflowId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.workflows.runs(workflowId) });
    },
    ...options,
  });
}

/**
 * Fetch workflow run with polling
 */
export function useWorkflowRun(
  runId: string,
  options?: Omit<UseQueryOptions<WorkflowRunResponse, ApiError>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: ['workflow-runs', runId],
    queryFn: () => WorkflowsService.getWorkflowRun({ runId }),
    enabled: !!runId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Poll every 2 seconds while running
      if (status === 'running' || status === 'pending') {
        return 2000;
      }
      return false;
    },
    ...options,
  });
}

// =============================================================================
// UTILITY HOOKS
// =============================================================================

/**
 * Prefetch process details on hover
 */
export function usePrefetchProcess() {
  const queryClient = useQueryClient();

  return (processId: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.processes.detail(processId),
      queryFn: () => ProcessesService.getProcess({ processId }),
      staleTime: 60 * 1000, // 1 minute
    });
  };
}

/**
 * Invalidate all process-related queries
 */
export function useInvalidateProcesses() {
  const queryClient = useQueryClient();

  return () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.processes.all });
  };
}
