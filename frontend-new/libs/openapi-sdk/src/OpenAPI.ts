/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { AxiosHttpRequest } from './core/AxiosHttpRequest';
import { AiService } from './services/AiService';
import { AlgorithmsService } from './services/AlgorithmsService';
import { AnalysesService } from './services/AnalysesService';
import { AnalyticsService } from './services/AnalyticsService';
import { AuditService } from './services/AuditService';
import { AuthService } from './services/AuthService';
import { BusinessUseCasesService } from './services/BusinessUseCasesService';
import { ConformanceService } from './services/ConformanceService';
import { DatasetsService } from './services/DatasetsService';
import { DevDataService } from './services/DevDataService';
import { DevelopmentService } from './services/DevelopmentService';
import { DevLogsService } from './services/DevLogsService';
import { DiscoveryService } from './services/DiscoveryService';
import { FilteringService } from './services/FilteringService';
import { HealthService } from './services/HealthService';
import { JobsService } from './services/JobsService';
import { ObjectCentricProcessMiningService } from './services/ObjectCentricProcessMiningService';
import { OperationsService } from './services/OperationsService';
import { OrganizationalMiningService } from './services/OrganizationalMiningService';
import { OrganizationsService } from './services/OrganizationsService';
import { ProjectsService } from './services/ProjectsService';
import { QualityMetricsService } from './services/QualityMetricsService';
import { SimulationService } from './services/SimulationService';
import { VisualizationService } from './services/VisualizationService';
import { WorkflowsService } from './services/WorkflowsService';
import { WorkspacesService } from './services/WorkspacesService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class OpenAPI {
    public readonly ai: AiService;
    public readonly algorithms: AlgorithmsService;
    public readonly analyses: AnalysesService;
    public readonly analytics: AnalyticsService;
    public readonly audit: AuditService;
    public readonly auth: AuthService;
    public readonly businessUseCases: BusinessUseCasesService;
    public readonly conformance: ConformanceService;
    public readonly datasets: DatasetsService;
    public readonly devData: DevDataService;
    public readonly development: DevelopmentService;
    public readonly devLogs: DevLogsService;
    public readonly discovery: DiscoveryService;
    public readonly filtering: FilteringService;
    public readonly health: HealthService;
    public readonly jobs: JobsService;
    public readonly objectCentricProcessMining: ObjectCentricProcessMiningService;
    public readonly operations: OperationsService;
    public readonly organizationalMining: OrganizationalMiningService;
    public readonly organizations: OrganizationsService;
    public readonly projects: ProjectsService;
    public readonly qualityMetrics: QualityMetricsService;
    public readonly simulation: SimulationService;
    public readonly visualization: VisualizationService;
    public readonly workflows: WorkflowsService;
    public readonly workspaces: WorkspacesService;
    public readonly request: BaseHttpRequest;
    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = AxiosHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '1.0.0',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });
        this.ai = new AiService(this.request);
        this.algorithms = new AlgorithmsService(this.request);
        this.analyses = new AnalysesService(this.request);
        this.analytics = new AnalyticsService(this.request);
        this.audit = new AuditService(this.request);
        this.auth = new AuthService(this.request);
        this.businessUseCases = new BusinessUseCasesService(this.request);
        this.conformance = new ConformanceService(this.request);
        this.datasets = new DatasetsService(this.request);
        this.devData = new DevDataService(this.request);
        this.development = new DevelopmentService(this.request);
        this.devLogs = new DevLogsService(this.request);
        this.discovery = new DiscoveryService(this.request);
        this.filtering = new FilteringService(this.request);
        this.health = new HealthService(this.request);
        this.jobs = new JobsService(this.request);
        this.objectCentricProcessMining = new ObjectCentricProcessMiningService(this.request);
        this.operations = new OperationsService(this.request);
        this.organizationalMining = new OrganizationalMiningService(this.request);
        this.organizations = new OrganizationsService(this.request);
        this.projects = new ProjectsService(this.request);
        this.qualityMetrics = new QualityMetricsService(this.request);
        this.simulation = new SimulationService(this.request);
        this.visualization = new VisualizationService(this.request);
        this.workflows = new WorkflowsService(this.request);
        this.workspaces = new WorkspacesService(this.request);
    }
}

