/**
 * AI Chat API Mutations
 *
 * TanStack Query mutation hooks for AI Chat functionality.
 * Connects the frontend chat UI to the backend /api/v1/ai/chat endpoint.
 */

import { useMutation } from '@tanstack/react-query';

import apiClient from '../../../api/client';

// ============================================
// Types
// ============================================

export interface AIChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

export interface AIChatRequest {
  datasetId: string;
  message: string;
  conversationHistory?: AIChatMessage[];
  analysisType?: 'bottleneck' | 'rework' | 'cycle_time' | 'pattern' | 'summary';
}

export interface AIInsight {
  type: string;
  title: string;
  description: string;
  severity?: 'high' | 'medium' | 'low' | 'info';
  data?: Record<string, unknown>;
}

export interface AIChatResponse {
  message: string;
  insights: AIInsight[];
  contextUsed: string | null;
  model: string;
  tokensUsed: number | null;
}

// Backend expects snake_case, frontend uses camelCase
interface AIChatRequestBody {
  dataset_id: string;
  message: string;
  conversation_history?: Array<{
    role: string;
    content: string;
    timestamp?: string;
  }>;
  analysis_type?: string;
}

interface AIChatResponseBody {
  message: string;
  insights: Array<{
    type: string;
    title: string;
    description: string;
    severity?: string;
    data?: Record<string, unknown>;
  }>;
  context_used: string | null;
  model: string;
  tokens_used: number | null;
}

// ============================================
// API Functions
// ============================================

async function sendChatMessage(request: AIChatRequest): Promise<AIChatResponse> {
  // Transform camelCase to snake_case for backend
  const body: AIChatRequestBody = {
    dataset_id: request.datasetId,
    message: request.message,
    conversation_history: request.conversationHistory?.map((msg) => ({
      role: msg.role,
      content: msg.content,
      timestamp: msg.timestamp,
    })),
    analysis_type: request.analysisType,
  };

  const { data } = await apiClient.post<AIChatResponseBody>('/api/v1/ai/chat', body);

  // Transform snake_case response to camelCase
  return {
    message: data.message,
    insights: data.insights.map((insight) => ({
      type: insight.type,
      title: insight.title,
      description: insight.description,
      severity: insight.severity as AIInsight['severity'],
      data: insight.data,
    })),
    contextUsed: data.context_used,
    model: data.model,
    tokensUsed: data.tokens_used,
  };
}

// ============================================
// Mutation Hooks
// ============================================

/**
 * Hook to send messages to the AI chat assistant.
 *
 * @example
 * const { mutate: sendMessage, isPending } = useSendAIMessage();
 *
 * sendMessage(
 *   { datasetId: 'abc', message: 'What are the bottlenecks?' },
 *   {
 *     onSuccess: (response) => {
 *       // Handle response
 *     },
 *   }
 * );
 */
export function useSendAIMessage() {
  return useMutation({
    mutationFn: sendChatMessage,
    onError: (error) => {
      console.error('[AI Chat] Error sending message:', error);
    },
  });
}
