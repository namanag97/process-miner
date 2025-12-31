/**
 * Process/Event Log Zod Schemas
 */
import { z } from 'zod';

// ============================================
// Process / Event Log
// ============================================

export const ProcessResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  source_format: z.string(),
  total_events: z.number(),
  total_cases: z.number(),
  total_activities: z.number(),
  activities: z.array(z.string()),
  created_at: z.string(),
  source_file: z.string().optional(),
});

export type ProcessResponse = z.infer<typeof ProcessResponseSchema>;

export const ProcessDetailResponseSchema = ProcessResponseSchema.extend({
  statistics: z.record(z.string(), z.unknown()).optional(),
  updated_at: z.string().optional(),
});

export type ProcessDetailResponse = z.infer<typeof ProcessDetailResponseSchema>;

// ============================================
// Column Detection (Upload)
// ============================================

export const ColumnSuggestionsSchema = z.object({
  case_id: z.string().optional(),
  activity: z.string().optional(),
  timestamp: z.string().optional(),
  resource: z.string().optional(),
});

export type ColumnSuggestions = z.infer<typeof ColumnSuggestionsSchema>;

export const ColumnDetectionResponseSchema = z.object({
  columns: z.array(z.string()),
  suggestions: ColumnSuggestionsSchema,
  sample_rows: z.array(z.record(z.string(), z.unknown())),
  row_count: z.number(),
});

export type ColumnDetectionResponse = z.infer<typeof ColumnDetectionResponseSchema>;

// ============================================
// Statistics
// ============================================

export const StatisticsResponseSchema = z.object({
  total_events: z.number(),
  total_cases: z.number(),
  total_activities: z.number(),
  total_variants: z.number(),
  activities: z.array(z.string()),
  start_activities: z.record(z.string(), z.number()),
  end_activities: z.record(z.string(), z.number()),
  avg_case_duration_seconds: z.number().optional(),
  min_case_duration_seconds: z.number().optional(),
  max_case_duration_seconds: z.number().optional(),
  date_range: z
    .object({
      start: z.string(),
      end: z.string(),
    })
    .optional(),
});

export type StatisticsResponse = z.infer<typeof StatisticsResponseSchema>;

// ============================================
// Process List Response
// ============================================

export const ProcessListResponseSchema = z.object({
  items: z.array(ProcessResponseSchema),
  total: z.number(),
});

export type ProcessListResponse = z.infer<typeof ProcessListResponseSchema>;

// ============================================
// Upload Response
// ============================================

export const UploadResponseSchema = z.object({
  id: z.string(),
  message: z.string().optional(),
});

export type UploadResponse = z.infer<typeof UploadResponseSchema>;
