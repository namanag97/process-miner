/**
 * AI Feature Module
 *
 * Self-contained feature module for AI & predictions.
 * Provides AI assistant, automated insights, and ML predictions.
 */

import { FeatureRegistry } from '../../core/plugins/FeatureRegistry';
import { aiRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'ai';

export const FEATURE_CONFIG = {
  id: 'ai',
  name: 'AI & Predictions',
  version: '1.0.0',
  icon: 'RobotOutlined',
  navPath: '/ai',
  navOrder: 6,
};

// Register feature
FeatureRegistry.register({
  ...FEATURE_CONFIG,
  routes: aiRouteConfig,
});

// ============================================
// Page Exports
// ============================================

export {
  AIIndexPage,
  AIAssistantPage,
  AIInsightsPage,
  PredictionsPage,
  PredictorDetailPage,
} from './pages';

// ============================================
// Route Exports
// ============================================

export { AIRoutes, aiRouteConfig } from './routes';

// ============================================
// Hook Exports
// ============================================

export { useAIProcesses } from './hooks';

// ============================================
// Component Exports
// ============================================

export { ProcessSelector, ChatMessage, InsightCard } from './components';

// ============================================
// Type Exports
// ============================================

export type {
  ChatMessage as ChatMessageType,
  ProcessInsight,
  ProcessSummary,
  ProcessStats,
  BottleneckItem,
  ReworkItem,
  PatternItem,
  ThroughputData,
  CycleTimeData,
  PromptSuggestion,
} from './types';

export { DEFAULT_PROMPTS } from './types';

// ============================================
// Utils Exports
// ============================================

export { buildProcessContext, buildQuickContext } from './utils/processContextBuilder';
