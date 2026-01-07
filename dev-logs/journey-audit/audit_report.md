=== User Journey Data Path Audit ===
Generated: Wed Jan  7 07:04:05 IST 2026

# Journey 1: User Onboarding

## Backend Endpoints
```
/Users/namanagarwal/system/backend/src/api/dependencies.py:77:        log_auth_event("login", success=False, reason="Missing token")
/Users/namanagarwal/system/backend/src/api/dependencies.py:85:        log_auth_event("login", success=False, reason=f"Invalid token: {e!s}")
/Users/namanagarwal/system/backend/src/api/dependencies.py:94:        log_auth_event("login", user_id=token_data.sub, success=False, reason="User not found")
/Users/namanagarwal/system/backend/src/api/dependencies.py:112:    log_auth_event("login", user_id=user.id, success=True)
/Users/namanagarwal/system/backend/src/api/dependencies.py:198:        last_login_at=datetime.utcnow(),
/Users/namanagarwal/system/backend/src/api/main.py:314:1.  **Register/Login**: Use `/api/v1/auth/login` to obtain an `access_token` and `refresh_token`.
```

## Error Handling Patterns
```
```

## Frontend Hooks
```
/Users/namanagarwal/system/frontend-new/src/api/generated.ts:3712:export const useRegisterApiV1AuthRegisterPost = <TError = HTTPValidationError, TContext = unknown>(
/Users/namanagarwal/system/frontend-new/src/api/generated.ts:3793:export const useLoginApiV1AuthLoginPost = <TError = HTTPValidationError, TContext = unknown>(
/Users/namanagarwal/system/frontend-new/src/api/generated.ts:7693:export const useCreateProjectApiV1ProjectsPost = <TError = HTTPValidationError, TContext = unknown>(
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useAuth.ts:9:    useLoginApiV1AuthLoginPost,
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useAuth.ts:65:    const loginMutation = useLoginApiV1AuthLoginPost();
/Users/namanagarwal/system/frontend-new/src/features/platform/projects/hooks/index.ts:58:export const useCreateProject = createMutationHook<Project, CreateProjectInput>({
/Users/namanagarwal/system/frontend-new/src/features/platform/projects/pages/ProjectsListPage.tsx:15:import { useProjectList, useCreateProject } from '../hooks';
/Users/namanagarwal/system/frontend-new/src/features/platform/projects/pages/ProjectsListPage.tsx:30:  const createProject = useCreateProject();
/Users/namanagarwal/system/frontend-new/src/features/platform/projects/index.ts:52:  useCreateProject,
```

# Journey 2: Dataset Upload & Processing (CRITICAL)

## Upload Endpoints
```
/Users/namanagarwal/system/backend/src/api/dependencies.py:262:            await container.ingestion.process(...)
/Users/namanagarwal/system/backend/src/api/main.py:245:            "description": "💾 Event log management. Upload, ingest, and manage CSV/XES/OCEL files.",
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:142:        workflow_id: The Temporal workflow ID (e.g., "dataset_ingestion-abc123")
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:52:    ingest_router as datasets_ingest_router,
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:53:    mapping_router as datasets_mapping_router,
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:55:    upload_router as datasets_upload_router,
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:73:    "datasets_upload_router",
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:74:    "datasets_mapping_router",
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:75:    "datasets_ingest_router",
```

## Dataset Service Layer
```
```

## Error Handling in Upload Flow
```
```

## Frontend Upload Components
```
```

# Journey 3: Process Discovery

## Mining Endpoints
```
/Users/namanagarwal/system/backend/src/api/dependencies.py:184:            description="Your default process mining workspace",
/Users/namanagarwal/system/backend/src/api/main.py:29:    discovery_router,
/Users/namanagarwal/system/backend/src/api/main.py:145:                description="Your default process mining workspace",
/Users/namanagarwal/system/backend/src/api/main.py:154:                description="Your default process mining project",
/Users/namanagarwal/system/backend/src/api/main.py:249:            "description": "🔍 Process model discovery. Alpha, Inductive, Heuristics miners.",
/Users/namanagarwal/system/backend/src/api/main.py:284:            "description": "👥 Organizational mining. Social networks and resource analysis.",
/Users/namanagarwal/system/backend/src/api/main.py:299:Welcome to the **Process Mining SaaS API**. This API provides enterprise-grade process mining capabilities, allowing you to discover, analyze, and optimize business processes from event logs.
/Users/namanagarwal/system/backend/src/api/main.py:340:            "url": "https://processmining.io/support",
/Users/namanagarwal/system/backend/src/api/main.py:341:            "email": "support@processmining.io",
/Users/namanagarwal/system/backend/src/api/main.py:345:            "url": "https://processmining.io/license",
/Users/namanagarwal/system/backend/src/api/main.py:347:        terms_of_service="https://processmining.io/terms",
/Users/namanagarwal/system/backend/src/api/main.py:455:            "type": "https://api.processmining.io/errors/ERR_500",
/Users/namanagarwal/system/backend/src/api/main.py:505:    app.include_router(discovery_router, prefix=settings.api_prefix)
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:28:from src.features.process_mining.analyses import router as analyses_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:29:from src.features.process_mining.analytics import router as analytics_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:30:from src.features.process_mining.business_use_cases import router as business_use_cases_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:31:from src.features.process_mining.conformance import router as conformance_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:32:from src.features.process_mining.discovery import router as discovery_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:33:from src.features.process_mining.filtering import router as filtering_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:34:from src.features.process_mining.ocpm import router as ocpm_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:35:from src.features.process_mining.organizational import router as organizational_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:36:from src.features.process_mining.predictions import router as predictions_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:37:from src.features.process_mining.simulation import router as simulation_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:38:from src.features.process_mining.statistics import router as statistics_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:39:from src.features.process_mining.visualization import router as visualization_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:40:from src.features.process_mining.workflows import router as workflows_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:43:from src.features.process_mining.api.algorithms import router as algorithms_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:44:from src.features.process_mining.api.quality import router as quality_metrics_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:47:# Datasets Routers (from features/process_mining/datasets)
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:49:from src.features.process_mining.datasets.api import (
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:81:    "discovery_router",
/Users/namanagarwal/system/backend/src/shared/repositories.py:11:from src.features.process_mining.models import (
/Users/namanagarwal/system/backend/src/shared/pipeline.py:3:Model process mining analyses as a directed acyclic graph (DAG).
/Users/namanagarwal/system/backend/src/shared/pipeline.py:11:        .add_node("discover", DiscoverNode(algorithm="inductive"))
/Users/namanagarwal/system/backend/src/shared/pipeline.py:13:        .connect("filter", "discover")
/Users/namanagarwal/system/backend/src/shared/pipeline.py:80:        from src.features.process_mining.services.loader import load_event_log
/Users/namanagarwal/system/backend/src/shared/pipeline.py:119:        # Run discovery
/Users/namanagarwal/system/backend/src/shared/pipeline.py:120:        from pm4py import discover_petri_net_inductive
/Users/namanagarwal/system/backend/src/shared/pipeline.py:123:            net, im, fm = discover_petri_net_inductive(event_log)
/Users/namanagarwal/system/backend/src/shared/container.py:19:    from src.features.process_mining.analytics.service import AnalyticsService
/Users/namanagarwal/system/backend/src/shared/container.py:20:    from src.features.process_mining.conformance.service import ConformanceService
/Users/namanagarwal/system/backend/src/shared/container.py:21:    from src.features.process_mining.discovery.service import MiningService
/Users/namanagarwal/system/backend/src/shared/container.py:22:    from src.features.process_mining.filtering.service import FilteringService
/Users/namanagarwal/system/backend/src/shared/container.py:23:    from src.features.process_mining.ingestion.service import IngestionService
/Users/namanagarwal/system/backend/src/shared/container.py:24:    from src.features.process_mining.ocpm.service import OCPMService
/Users/namanagarwal/system/backend/src/shared/container.py:25:    from src.features.process_mining.organizational.service import OrganizationalService
/Users/namanagarwal/system/backend/src/shared/container.py:26:    from src.features.process_mining.predictions.service import PredictionService
/Users/namanagarwal/system/backend/src/shared/container.py:27:    from src.features.process_mining.simulation.service import SimulationService
/Users/namanagarwal/system/backend/src/shared/container.py:28:    from src.features.process_mining.visualization.service import VisualizationService
/Users/namanagarwal/system/backend/src/shared/container.py:70:        from src.features.process_mining.ingestion.service import IngestionService
```

## Frontend Discovery Components
```
/Users/namanagarwal/system/frontend-new/src/features/index.ts:18:import './discovery';
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:35:type AnalysisCategory = 'Discovery' | 'Variants' | 'Statistics' | 'Performance' | 'Organizational' | 'Conformance';
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:60:  // Discovery
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:64:    category: 'Discovery',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:68:    apiMethod: 'discovery.buildDFG',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:72:    name: 'Alpha Miner',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:73:    category: 'Discovery',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:74:    description: 'Classic Petri net discovery algorithm',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:77:    apiMethod: 'discovery.discover',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:81:    name: 'Inductive Miner',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:82:    category: 'Discovery',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:83:    description: 'Block-structured process tree discovery',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:86:    apiMethod: 'discovery.discover',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:90:    name: 'Heuristics Miner',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:91:    category: 'Discovery',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:95:    apiMethod: 'discovery.discover',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:106:    apiMethod: 'discovery.getVariants',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:164:const CATEGORY_ORDER: AnalysisCategory[] = ['Discovery', 'Variants', 'Statistics', 'Performance', 'Organizational', 'Conformance'];
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:167:  Discovery: <SearchOutlined />,
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:176:  Discovery: 'blue',
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:347:  const [activeCategory, setActiveCategory] = useState<AnalysisCategory>('Discovery');
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:382:          data = await sdk.discovery.buildDFG(selectedDatasetId);
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:387:          data = await sdk.discovery.getVariants(selectedDatasetId, { topN: 20 });
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:406:          const result = await sdk.discovery.discover({
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/TestBenchPage.tsx:408:            minerType: analysis.id === 'heuristic' ? 'heuristics' : analysis.id,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:9:  DFGData,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:10:  DFGNode,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:11:  DFGEdge,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:17:// DFG Mock Data
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:20:const mockDFGNodes: DFGNode[] = [
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:100:const mockDFGEdges: DFGEdge[] = [
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:216:export const mockOrderToCashDFG: DFGData = {
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:217:  nodes: mockDFGNodes,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:218:  edges: mockDFGEdges,
/Users/namanagarwal/system/frontend-new/src/features/explorer/mocks/orderToCash.ts:226:  totalFrequency: mockDFGEdges.reduce((sum, edge) => sum + edge.frequency, 0),
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/HelpCenterPage.tsx:96:  { key: 'discovery', label: 'Process Discovery', icon: <CompassOutlined />, color: tokens.colors.success[500] },
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/HelpCenterPage.tsx:112:  { title: 'Process Map Visualization', description: 'Understand nodes, edges, and frequency', category: 'discovery', path: '/explorer' },
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/HelpCenterPage.tsx:113:  { title: 'Variant Analysis', description: 'Explore different execution paths', category: 'discovery', path: '/explorer' },
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/HelpCenterPage.tsx:114:  { title: 'Filtering Processes', description: 'Use filters to focus your analysis', category: 'discovery', path: '/explorer' },
/Users/namanagarwal/system/frontend-new/src/features/platform/pages/HelpCenterPage.tsx:150:    category: 'discovery',
```

# Journey 4: Process Analysis

## Analysis Endpoints
```
/Users/namanagarwal/system/backend/src/api/main.py:253:            "description": "✅ Conformance checking. Token replay, alignments, and deviation analysis.",
/Users/namanagarwal/system/backend/src/api/main.py:276:            "description": "🎲 Process simulation and what-if analysis.",
/Users/namanagarwal/system/backend/src/api/main.py:284:            "description": "👥 Organizational mining. Social networks and resource analysis.",
/Users/namanagarwal/system/backend/src/api/main.py:306:*   **Performance Analytics**: Deep dive into bottlenecks, cycle times, and throughput efficiency.
/Users/namanagarwal/system/backend/src/shared/repositories.py:39:        analysis_type: str,
/Users/namanagarwal/system/backend/src/shared/repositories.py:41:        """Get latest analysis of a specific type for a dataset."""
/Users/namanagarwal/system/backend/src/shared/repositories.py:45:            .where(Analysis.type == analysis_type)
/Users/namanagarwal/system/backend/src/shared/repositories.py:238:        "analysis": AnalysisRepository(session),
/Users/namanagarwal/system/backend/src/shared/pipeline.py:8:        Pipeline("my-analysis")
/Users/namanagarwal/system/backend/src/shared/pipeline.py:153:    metrics: list[str] = field(default_factory=lambda: ["variants", "throughput"])
/Users/namanagarwal/system/backend/src/shared/pipeline.py:162:        if "variants" in self.metrics:
/Users/namanagarwal/system/backend/src/shared/pipeline.py:163:            from pm4py.statistics.variants import get
/Users/namanagarwal/system/backend/src/shared/pipeline.py:164:            results["variants"] = get.get_variants(event_log)
/Users/namanagarwal/system/backend/src/shared/events.py:95:ANALYSIS_STARTED = "analysis.started"
/Users/namanagarwal/system/backend/src/shared/events.py:96:ANALYSIS_COMPLETED = "analysis.completed"
/Users/namanagarwal/system/backend/src/shared/events.py:97:ANALYSIS_FAILED = "analysis.failed"
/Users/namanagarwal/system/backend/src/shared/protocols.py:94:        """Run analysis on a dataset."""
/Users/namanagarwal/system/backend/src/shared/base_schemas.py:181:    long-running operations like DAG runs, analysis jobs, etc.
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:35:- `alignment`: More accurate, slower (for detailed analysis)
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:463:async def get_root_cause_analysis(
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:470:    """Get comprehensive root cause analysis for conformance deviations."""
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:473:    logger.info("root_cause_analysis_started", dataset_id=dataset_id, model_id=model_id)
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:481:        analysis = root_cause_analyzer.get_comprehensive_root_cause_analysis(event_log, model, attribute_list)
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:484:        logger.info("root_cause_analysis_completed", duration_ms=round(duration_ms, 2))
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:485:        return analysis
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:487:        logger.error("root_cause_analysis_failed", error=str(e), exc_info=True)
/Users/namanagarwal/system/backend/src/features/process_mining/simulation/router.py:3:What-if analysis and synthetic log generation.
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:97:        variant: str = "basic",
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:107:            variant: PRIPEL variant ("basic" or "advanced")
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:116:                variant=variant,
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:142:            orig_variants = pm4py.get_variants(original_log)
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:143:            anon_variants = pm4py.get_variants(anonymized_log)
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:146:            orig_variant_set = set(orig_variants.keys())
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:147:            anon_variant_set = set(anon_variants.keys())
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:149:            preserved = len(orig_variant_set.intersection(anon_variant_set))
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:150:            total_orig = len(orig_variant_set)
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:162:                "original_variants": total_orig,
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:163:                "anonymized_variants": len(anon_variant_set),
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:164:                "variant_overlap": preserved,
/Users/namanagarwal/system/backend/src/features/process_mining/services/privacy.py:165:                "variant_preservation_ratio": preserved / total_orig if total_orig > 0 else 0,
/Users/namanagarwal/system/backend/src/features/process_mining/engine/loader.py:21:        PM4Py EventLog object ready for analysis.
/Users/namanagarwal/system/backend/src/features/process_mining/engine/loader.py:48:    Useful for statistics and variant analysis where
/Users/namanagarwal/system/backend/src/features/process_mining/simulation/__init__.py:1:"""Simulation Module - Process simulation and what-if analysis.
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:3:Performance analysis endpoints for process mining insights.
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:19:- **Bottlenecks**: `GET /api/v1/analytics/datasets/{id}/bottlenecks`
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:75:@router.get("/datasets/{dataset_id}/bottlenecks", response_model=BottleneckListResponse)
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:76:async def get_bottlenecks(
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:81:    """Detect process bottlenecks based on waiting times."""
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:82:    logger.info("getting_bottlenecks", dataset_id=dataset_id)
/Users/namanagarwal/system/backend/src/features/process_mining/analytics/router.py:85:    cache_key = f"bottlenecks:{dataset_id}"
```

# Journey 5: Conformance Checking

## Conformance Endpoints
```
/Users/namanagarwal/system/backend/src/api/main.py:25:    conformance_router,
/Users/namanagarwal/system/backend/src/api/main.py:506:    app.include_router(conformance_router, prefix=settings.api_prefix)
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:5:- Process Mining: Discovery, conformance, analytics, visualization, datasets, etc.
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:31:from src.features.process_mining.conformance import router as conformance_router
/Users/namanagarwal/system/backend/src/api/routers/__init__.py:82:    "conformance_router",
/Users/namanagarwal/system/backend/src/shared/pipeline.py:131:    """Check conformance between log and model."""
/Users/namanagarwal/system/backend/src/shared/pipeline.py:140:        from pm4py.conformance import conformance_diagnostics_token_based_replay
/Users/namanagarwal/system/backend/src/shared/pipeline.py:142:        diagnostics = conformance_diagnostics_token_based_replay(
/Users/namanagarwal/system/backend/src/shared/pipeline.py:146:        return {"conformance": diagnostics}
/Users/namanagarwal/system/backend/src/shared/container.py:20:    from src.features.process_mining.conformance.service import ConformanceService
/Users/namanagarwal/system/backend/src/shared/container.py:92:    def conformance(self) -> "ConformanceService":
/Users/namanagarwal/system/backend/src/shared/container.py:94:        from src.features.process_mining.conformance.service import ConformanceService
/Users/namanagarwal/system/backend/src/shared/protocols.py:115:    """Protocol for conformance checking services."""
/Users/namanagarwal/system/backend/src/shared/protocols.py:117:    async def check_conformance(
/Users/namanagarwal/system/backend/src/shared/protocols.py:124:        """Check conformance between log and model."""
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:3:Endpoints for checking conformance between event logs and process models.
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:23:   POST /api/v1/conformance/check
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:26:2. **Get Quality Metrics**: `GET /api/v1/conformance/quality/{dataset_id}/{model_id}`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:27:3. **Get Diagnostics**: `GET /api/v1/conformance/diagnostics/{dataset_id}/{model_id}`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:28:4. **Get Deviations**: `GET /api/v1/conformance/deviations/{dataset_id}/{model_id}`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:29:5. **Root Cause Analysis**: `GET /api/v1/conformance/root-cause/{dataset_id}/{model_id}`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:30:6. **List Results**: `GET /api/v1/conformance/results`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:31:7. **Import PNML/BPMN**: `POST /api/v1/conformance/import-model`
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:66:router = APIRouter(prefix="/conformance", tags=["Conformance"])
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:100:async def check_conformance(
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:106:    """Check conformance between an event log and a process model."""
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:108:        "conformance_check_started",
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:126:        result = container.conformance.check_conformance(
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:132:        conformance_record = ConformanceResult(
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:138:            diagnostics_json=json.dumps({
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:143:        db.add(conformance_record)
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:145:        await db.refresh(conformance_record)
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:149:            "conformance_check_completed",
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:150:            result_id=conformance_record.id,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:156:            id=conformance_record.id,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:157:            dataset_id=conformance_record.dataset_id,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:158:            model_id=conformance_record.model_id,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:159:            fitness=conformance_record.fitness,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:160:            precision=conformance_record.precision,
/Users/namanagarwal/system/backend/src/features/process_mining/conformance/router.py:161:            method=conformance_record.method,
```

# Journey 6: Workflow Execution

## Temporal Workflows
```
/Users/namanagarwal/system/backend/src/api/main.py:41:    workflows_api_router,
/Users/namanagarwal/system/backend/src/api/main.py:42:    workflows_router,
/Users/namanagarwal/system/backend/src/api/main.py:226:            "description": "🔀 DAG workflow orchestration. Trigger and monitor multi-step workflows.",
/Users/namanagarwal/system/backend/src/api/main.py:515:    app.include_router(workflows_router, prefix=settings.api_prefix)
/Users/namanagarwal/system/backend/src/api/main.py:523:    app.include_router(workflows_api_router, prefix=settings.api_prefix)  # Temporal workflow status
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:3:Provides endpoints for querying Temporal workflow status and database-backed workflow records.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:12:from src.platform.workflows import (
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:21:router = APIRouter(prefix="/workflows", tags=["Workflows"])
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:30:async def list_workflows(
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:34:    workflow_type: str | None = Query(None, description="Filter by type"),
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:40:    """List workflows for the current user/organization.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:42:    Use entity_type + entity_id to get workflows for a specific dataset/model.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:52:    if workflow_type:
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:53:        query = query.where(Workflow.workflow_type == workflow_type)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:72:    workflows = result.scalars().all()
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:75:        items=[WorkflowResponse.model_validate(w) for w in workflows],
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:82:@router.get("/{workflow_id}", response_model=WorkflowResponse)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:83:async def get_workflow(
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:85:    workflow_id: str,
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:88:    """Get workflow details with task-level progress."""
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:92:        .where(Workflow.id == workflow_id)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:97:    workflow = result.scalar_one_or_none()
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:99:    if not workflow:
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:100:        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:102:    return WorkflowResponse.model_validate(workflow)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:105:@router.get("/{workflow_id}/tasks", response_model=list[WorkflowTaskResponse])
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:106:async def get_workflow_tasks(
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:108:    workflow_id: str,
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:111:    """Get granular task progress for a workflow.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:118:        .where(Workflow.id == workflow_id)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:123:    workflow = result.scalar_one_or_none()
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:125:    if not workflow:
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:126:        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:129:    return [WorkflowTaskResponse.model_validate(t) for t in workflow.tasks]
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:137:@router.get("/{workflow_id}/status")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:138:async def get_workflow_temporal_status(workflow_id: str) -> dict:
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:139:    """Get real-time status from Temporal for a workflow.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:142:        workflow_id: The Temporal workflow ID (e.g., "dataset_ingestion-abc123")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:147:    from src.platform.temporal.compat import get_workflow_status as query_status
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:150:        status = await query_status(workflow_id)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:152:            "workflow_id": workflow_id,
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:161:        logger.error("workflow_status_error", workflow_id=workflow_id, error=str(e))
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:162:        raise HTTPException(status_code=404, detail=f"Workflow not found: {workflow_id}")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:165:@router.post("/{workflow_id}/cancel")
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:166:async def cancel_workflow(workflow_id: str) -> dict:
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:167:    """Cancel a running Temporal workflow.
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:170:        workflow_id: The workflow ID to cancel
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:175:    from src.platform.temporal.compat import cancel_workflow as do_cancel
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:178:        await do_cancel(workflow_id)
/Users/namanagarwal/system/backend/src/api/routers/workflows.py:179:        logger.info("workflow_cancelled", workflow_id=workflow_id)
```

# Cross-Cutting Concerns

## Bare Exception Handlers (POTENTIAL BUGS)
```
/Users/namanagarwal/system/backend/src/api/dependencies.py:134:    except Exception:
/Users/namanagarwal/system/backend/src/shared/error_utils.py:80:    Use this instead of bare `except Exception: pass` to ensure
/Users/namanagarwal/system/backend/src/features/process_mining/api/datasets/mapping.py:305:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/discovery/serialization.py:47:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/api/datasets/analytics.py:53:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/api/datasets/analytics.py:420:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/api/datasets/upload.py:472:            except Exception:
/Users/namanagarwal/system/backend/src/platform/devconsole/broker.py:87:            except Exception:
/Users/namanagarwal/system/backend/src/platform/devconsole/broker.py:232:            except Exception:
/Users/namanagarwal/system/backend/src/platform/devconsole/logging.py:254:    except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/services/quality_service.py:187:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/services/quality_service.py:230:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/services/quality_service.py:292:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/ingestion/service.py:546:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/ocpm/service.py:352:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/ocpm/service.py:695:        except Exception:
/Users/namanagarwal/system/backend/src/platform/infrastructure/circuit_breaker.py:190:            except Exception:
/Users/namanagarwal/system/backend/src/platform/infrastructure/circuit_breaker.py:206:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/services/loader.py:329:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/services/ingestion/service.py:546:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/filtering/router.py:354:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/filtering/router.py:362:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/services/mining_algorithms/providers/pm4py_provider.py:264:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/filtering/service.py:600:        except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/api/mapping.py:305:            except Exception:
/Users/namanagarwal/system/backend/src/platform/health/router.py:216:    except Exception:
/Users/namanagarwal/system/backend/src/platform/infrastructure/tasks/dataset_tasks.py:517:            except Exception:
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/api/upload.py:472:            except Exception:
/Users/namanagarwal/system/backend/src/platform/devtools/dev_data.py:65:        except Exception:
/Users/namanagarwal/system/backend/src/platform/core/api_logging.py:81:            except Exception:
/Users/namanagarwal/system/backend/src/platform/core/api_logging.py:182:    except Exception:
/Users/namanagarwal/system/backend/src/platform/temporal/activities/quality.py:139:        except Exception:
/Users/namanagarwal/system/backend/src/platform/temporal/activities/quality.py:224:            except Exception:
/Users/namanagarwal/system/backend/src/platform/temporal/activities/quality.py:231:        except Exception:
/Users/namanagarwal/system/backend/src/platform/temporal/activities/dataset.py:75:        except Exception:
```

## Missing Logger Imports
```
/Users/namanagarwal/system/backend/src/platform/temporal/config.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/compat.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/client.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/workflows/ingestion.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/workflows/analysis.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/workflows/quality.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/activities/analysis.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/activities/dataset.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/workers/ingestion.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/temporal/workers/analysis.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/organizations/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/error_messages.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/enums.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/config.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/result.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/value_objects.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/rate_limit.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/permissions.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/core/validation.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/service.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/tasks/analysis.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/tasks/dataset.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/registry.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/templates.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/engine.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/repository.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/dag/executor.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/admin/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/workflows/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/workflows/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/workspaces/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/system/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/devtools/dev_data.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/user.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/organization.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/schemas/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/workspace.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/users/project.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/jobs/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/object_storage.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/tasks/analysis_tasks.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/tasks/maintenance_tasks.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/tasks/dataset_tasks.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/tasks/base.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/infrastructure/cache.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/platform/devconsole/models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/enums.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/models/enums.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/models/uploaded_file.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/models/dataset.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/datasets/services/ingestion/migration/pickle_migration.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/enums.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/ocel.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/process_model_models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/variants.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/organizational.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/analysis_enums.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/events_models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/lookup_tables.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/prediction.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/uploaded_file.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/dataset.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/cache_models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/algorithm_registry.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/models/analysis_models.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/simulation.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/predictions.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/ocel.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/organizational.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/discovery.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/visualization.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/conformance.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/workflows.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/analytics.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/converters.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/schemas/analyses.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/ocpm/service.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/engine/loader.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/ingestion/migration/pickle_migration.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/serializers/pnml_exporter.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/serializers/graph_serializer.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/mining_algorithms/providers/base.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/domain/value_objects.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/features/process_mining/services/domain/repositories.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/base_schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/base_repository.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/api_responses.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/events.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/database.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/container.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/schemas.py: NO LOGGER IMPORTED
/Users/namanagarwal/system/backend/src/shared/repositories.py: NO LOGGER IMPORTED
```

## Console.log/error in Frontend
```
/Users/namanagarwal/system/frontend-new/src/api/client.ts:34:        console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}: ${message}`);
/Users/namanagarwal/system/frontend-new/src/shared/design-system.ts:80:        console.log(`[Action] ${category}`, action);
/Users/namanagarwal/system/frontend-new/src/shared/design-system.ts:82:        console.log(`[Action] ${category}${action ? `: ${action}` : ''}`, details || '');
/Users/namanagarwal/system/frontend-new/src/shared/design-system.ts:88:    console.error(`[Error] ${category}: ${msg}`, context || '');
/Users/namanagarwal/system/frontend-new/src/shared/design-system.ts:92:    console.log(`[Request] ${method} ${url}`, data || '');
/Users/namanagarwal/system/frontend-new/src/shared/design-system.ts:96:    console.log(`[Response] ${method} ${url} - ${status}${typeof duration === 'number' ? ` (${duration}ms)` : ''}`, data || '');
/Users/namanagarwal/system/frontend-new/src/shared/components.tsx:190:        console.error('[ErrorBoundary] Caught error:', error, errorInfo);
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useURLState.ts:63: * console.log(state.tab); // 'performance'
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useBackendLogs.ts:251:          console.error('[BackendLogs] Failed to parse log:', err);
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useBackendLogs.ts:305:          console.error('[BackendLogs] Failed to parse heartbeat:', err);
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useBackendLogs.ts:317:        console.log(`[BackendLogs] Reconnecting in ${delay}ms...`);
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useBackendLogs.ts:322:        console.log('[BackendLogs] ✓ Connected to backend observability stream');
/Users/namanagarwal/system/frontend-new/src/shared/hooks/useBackendLogs.ts:334:      console.error('[BackendLogs] Failed to connect:', err);
/Users/namanagarwal/system/frontend-new/src/shared/core/components/FeatureErrorBoundary.tsx:31:        console.error(`[FeatureErrorBoundary:${this.props.featureId}] Error:`, error);
/Users/namanagarwal/system/frontend-new/src/shared/core/components/FeatureErrorBoundary.tsx:32:        console.error('Component stack:', info.componentStack);
/Users/namanagarwal/system/frontend-new/src/config/env.ts:10: * console.log(env.API_BASE_URL);
/Users/namanagarwal/system/frontend-new/src/config/env.ts:92:    console.error(
/Users/namanagarwal/system/frontend-new/src/config/env.ts:104:    console.warn('[Env] Using default configuration due to validation errors');
/Users/namanagarwal/system/frontend-new/src/config/env.ts:119:  console.log('[Env] Configuration loaded:', {
/Users/namanagarwal/system/frontend-new/src/shared/core/plugins/FeatureRegistry.ts:95:      console.warn(`[FeatureRegistry] Feature ${id} already registered, overwriting`);
/Users/namanagarwal/system/frontend-new/src/shared/core/plugins/FeatureRegistry.ts:215:        console.error('[FeatureRegistry] Listener error:', error);
/Users/namanagarwal/system/frontend-new/src/App.tsx:27:    console.error('[App] Global error captured:', report);
/Users/namanagarwal/system/frontend-new/src/main.tsx:20:const originalConsoleError = console.error;
/Users/namanagarwal/system/frontend-new/src/main.tsx:21:console.error = (...args: unknown[]) => {
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsole/PageErrorBoundary.tsx:94:        console.error(`[PageErrorBoundary] ${pageName} crashed:`, error);
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsole/PageErrorBoundary.tsx:95:        console.error('Component Stack:', errorInfo.componentStack);
/Users/namanagarwal/system/frontend-new/src/shared/ui/GlobalErrorBoundary/index.tsx:201:      console.error('[GlobalErrorBoundary] Caught error:', error);
/Users/namanagarwal/system/frontend-new/src/shared/ui/GlobalErrorBoundary/index.tsx:202:      console.error('[GlobalErrorBoundary] Error Info:', errorInfo);
/Users/namanagarwal/system/frontend-new/src/shared/ui/GlobalErrorBoundary/index.tsx:203:      console.error('[GlobalErrorBoundary] Full Report:', report);
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:14:    console.log('[DIAGNOSTIC] Running DevConsole diagnostics...');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:18:      console.log('[DIAGNOSTIC] Test 1: Local devLog.info');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:24:      console.log('[DIAGNOSTIC] Test 2: Local devLog.action');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:30:      console.log('[DIAGNOSTIC] Test 3: Local devLog.error');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:36:      console.log('[DIAGNOSTIC] Test 4: Design-system logAction');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:42:      console.log('[DIAGNOSTIC] Test 5: Design-system logError');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:48:      console.log('[DIAGNOSTIC] Test 6: Design-system logRequest/logResponse');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:58:      console.log('[DIAGNOSTIC] Test 7: Throw and catch error');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsoleDiagnostic/index.tsx:66:    console.log('[DIAGNOSTIC] All diagnostic tests scheduled');
/Users/namanagarwal/system/frontend-new/src/shared/ui/DevConsole/index.tsx:258:    console.log(`%c[${level.toUpperCase()}] ${source}`, style, message, data || '');
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/pages/UploadWizardPage.tsx:65:        console.log('[UploadWizard:Page] Wizard initialized', {
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/pages/UploadWizardPage.tsx:83:        console.log('[UploadWizard:Page] Step changed', {
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/pages/UploadWizardPage.tsx:107:            console.error('[UploadWizard:Page] Error occurred', {
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/pages/UploadWizardPage.tsx:156:                            console.log('[UploadWizard:Page] Upload complete callback', {
/Users/namanagarwal/system/frontend-new/src/features/ai/pages/PredictionsPage.tsx:92:    console.warn('Training not implemented yet due to missing hooks');
/Users/namanagarwal/system/frontend-new/src/features/ai/pages/PredictionsPage.tsx:106:        console.warn('Deletion not implemented yet due to missing hooks');
/Users/namanagarwal/system/frontend-new/src/features/platform/projects/pages/ProjectsListPage.tsx:96:      console.error('Failed to create project:', error);
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/hooks/useUploadWizard.ts:39:    console.log('[API:fetchPreview] Request started', { datasetId, rows });
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/hooks/useUploadWizard.ts:43:        console.error('[API:fetchPreview] Request failed', { status: res.status });
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/hooks/useUploadWizard.ts:48:    console.log('[API:fetchPreview] Success', { columns: data.columns?.length, rows: data.rows?.length });
/Users/namanagarwal/system/frontend-new/src/features/platform/upload-wizard/hooks/useUploadWizard.ts:54:    console.log('[API:fetchSheets] Request started', { datasetId });
```

## Silent Error Swallowing
```
```

## TODO/FIXME Comments
```
/Users/namanagarwal/system/frontend-new/src/App.tsx:30:  // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
/Users/namanagarwal/system/frontend-new/src/features/ai/hooks/index.ts:87: * TODO: Implement train() method in predictions module
/Users/namanagarwal/system/frontend-new/src/features/ai/hooks/index.ts:102: * TODO: Implement delete() method in predictions module
/Users/namanagarwal/system/backend/src/platform/storage/storage.py:117:    TODO: Implement when needed for production deployment.
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:73:        # TODO: Publish JOB_CREATED event to Redis for SSE
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:110:        # TODO: Publish JOB_STARTED event to Redis for SSE
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:134:            # TODO: Publish JOB_PROGRESS event to Redis for SSE
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:162:            # TODO: Publish JOB_COMPLETED event to Redis for SSE
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:188:            # TODO: Publish JOB_FAILED event to Redis for SSE
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:212:        # TODO: Cancel Celery task if running
/Users/namanagarwal/system/backend/src/platform/jobs/service.py:213:        # TODO: Publish JOB_CANCELLED event to Redis for SSE
/Users/namanagarwal/system/frontend-new/src/features/explorer/pages/ExplorerDetailPage.tsx:335:  // TODO: Re-implement when adding path highlighting feature to CytoscapeCanvas
/Users/namanagarwal/system/frontend-new/src/features/explorer/pages/ExplorerDetailPage.tsx:584:          {/* TODO: Replace with real filtered case count when filter backend is implemented
/Users/namanagarwal/system/backend/src/platform/dag/router.py:387:        total=len(items),  # TODO: proper count query
```
