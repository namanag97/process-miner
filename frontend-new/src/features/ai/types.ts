/**
 * AI Types - TypeScript interfaces for AI Assistant feature
 */

// =============================================================================
// Chat Message Types
// =============================================================================

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  insights?: ProcessInsight[];
  isLoading?: boolean;
}

export interface ProcessInsight {
  type: 'bottleneck' | 'pattern' | 'anomaly' | 'recommendation' | 'metric';
  title: string;
  description: string;
  severity?: 'high' | 'medium' | 'low' | 'info';
  data?: Record<string, unknown>;
  icon?: string;
}

// =============================================================================
// Process Summary Types (for LLM context)
// =============================================================================

export interface ProcessSummary {
  processId: string;
  processName: string;
  stats: ProcessStats;
  bottlenecks: BottleneckItem[];
  rework: ReworkItem[];
  patterns: PatternItem[];
  throughput: ThroughputData;
  cycleTime: CycleTimeData;
}

export interface ProcessStats {
  totalCases: number;
  totalEvents: number;
  totalActivities: number;
  activities: string[];
}

export interface BottleneckItem {
  activity: string;
  avgWaitingTimeSeconds: number;
  avgServiceTimeSeconds: number;
  frequency: number;
  isBottleneck: boolean;
  severity: string;
  bottleneckImpactScore: number;
}

export interface ReworkItem {
  activity: string;
  reworkCount: number;
  casesWithRework: number;
  reworkPercentage: number;
}

export interface PatternItem {
  pattern: string[];
  support: number;
  confidence: number;
  frequency: number;
}

export interface ThroughputData {
  totalCases: number;
  completedCases: number;
  casesPerDay: number;
  casesPerWeek: number;
  casesPerMonth: number;
  timeRangeDays: number;
}

export interface CycleTimeData {
  minSeconds: number;
  maxSeconds: number;
  avgSeconds: number;
  medianSeconds: number;
  percentile25Seconds: number;
  percentile75Seconds: number;
  percentile95Seconds: number;
}

// =============================================================================
// Prompt Suggestion Types
// =============================================================================

export interface PromptSuggestion {
  id: string;
  label: string;
  prompt: string;
  icon: string;
  category: 'performance' | 'patterns' | 'insights' | 'comparison';
}

// Default prompt suggestions
export const DEFAULT_PROMPTS: PromptSuggestion[] = [
  {
    id: 'bottlenecks',
    label: 'Find bottlenecks',
    prompt: 'What are the main bottlenecks in this process and how can I address them?',
    icon: 'ThunderboltOutlined',
    category: 'performance',
  },
  {
    id: 'rework',
    label: 'Analyze rework',
    prompt: 'Where does rework occur most frequently and what causes it?',
    icon: 'SyncOutlined',
    category: 'performance',
  },
  {
    id: 'patterns',
    label: 'Discover patterns',
    prompt: 'What are the most common process patterns and variants?',
    icon: 'NodeIndexOutlined',
    category: 'patterns',
  },
  {
    id: 'optimization',
    label: 'Optimization tips',
    prompt: 'How can I optimize this process to reduce cycle time?',
    icon: 'RocketOutlined',
    category: 'insights',
  },
  {
    id: 'anomalies',
    label: 'Detect anomalies',
    prompt: 'Are there any unusual patterns or anomalies in the process execution?',
    icon: 'WarningOutlined',
    category: 'insights',
  },
  {
    id: 'summary',
    label: 'Process summary',
    prompt: 'Give me a comprehensive summary of this process performance.',
    icon: 'FileTextOutlined',
    category: 'insights',
  },
];
