/**
 * Common Zod Schemas - Shared primitives for API validation
 */
import { z } from 'zod';

// ============================================
// Pagination
// ============================================

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    total: z.number(),
    page: z.number(),
    page_size: z.number(),
    pages: z.number(),
  });

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

// ============================================
// Date Range
// ============================================

export const DateRangeSchema = z.object({
  start: z.string(),
  end: z.string(),
});

export type DateRange = z.infer<typeof DateRangeSchema>;

// ============================================
// API Error
// ============================================

export const APIErrorDetailSchema = z.object({
  code: z.string().optional(),
  message: z.string(),
  field: z.string().optional(),
});

export const APIErrorResponseSchema = z.object({
  status: z.number(),
  message: z.string(),
  detail: z.union([z.string(), z.array(APIErrorDetailSchema)]).optional(),
  type: z.string().optional(),
  title: z.string().optional(),
  instance: z.string().optional(),
});

export type APIErrorResponse = z.infer<typeof APIErrorResponseSchema>;

// ============================================
// Common Value Types
// ============================================

export const SeveritySchema = z.enum(['low', 'medium', 'high', 'critical']);
export type Severity = z.infer<typeof SeveritySchema>;

export const StatusSchema = z.enum(['pending', 'processing', 'completed', 'failed']);
export type Status = z.infer<typeof StatusSchema>;

// ============================================
// Helper function for safe parsing
// ============================================

export function validateResponse<T>(schema: z.ZodType<T>, data: unknown): T {
  const result = schema.safeParse(data);
  if (!result.success) {
    console.error('[API Validation Error]', result.error.format());
    throw new Error(`API response validation failed: ${result.error.message}`);
  }
  return result.data;
}

export function safeValidateResponse<T>(
  schema: z.ZodType<T>,
  data: unknown
): { success: true; data: T } | { success: false; error: z.ZodError } {
  const result = schema.safeParse(data);
  if (result.success) {
    return { success: true, data: result.data };
  }
  return { success: false, error: result.error };
}
