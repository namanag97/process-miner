/**
 * Discovery Feature
 * 
 * Process discovery with 15 algorithms, job tracking, and interactive visualization.
 */

import { FeatureRegistry } from '../../shared/core/plugins/FeatureRegistry';
import { discoveryRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'discovery';

export const FEATURE_CONFIG = {
    id: 'discovery',
    name: 'Process Discovery',
    version: '1.0.0',
    icon: 'ThunderboltOutlined',
    // No navPath - discovery is accessed from workspace
    navOrder: 5,
};

// Register feature (auto-registration on import)
FeatureRegistry.register({
    ...FEATURE_CONFIG,
    routes: discoveryRouteConfig,
});

// ============================================
// Page Exports
// ============================================

// Pages
export { DiscoveryPage } from './pages';

// Components
export { JobStatusPanel, ModelList, JSONViewer, GraphViewer } from './components';

// Hooks
export {
    useAnalysisMetadata,
    useDiscoveryMutation,
    useJobStatus,
    useDiscoveredModels,
    useModelVisualization,
    discoveryQueryKeys,
} from './hooks';

// Types
export type {
    Job,
    JobStatus,
    MinerType,
    ModelFormat,
    DiscoveryRequest,
    DiscoveryResponse,
    DiscoveredModel,
    AnalysisMetadata,
    AnalysisTypeInfo,
    ConfigSchemaField,
} from './types';
