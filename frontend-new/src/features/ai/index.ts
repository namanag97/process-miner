/**
 * AI Feature Module
 *
 * Self-contained feature module for AI & predictions.
 * Provides AI assistant, automated insights, and ML predictions.
 */

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
