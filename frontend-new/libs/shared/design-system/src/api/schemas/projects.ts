/**
 * Projects Zod Schemas
 * 
 * FIXED: Aligned with backend schemas.py ProjectResponse
 * - process_count → total_files, total_analyses
 * - processes → datasets
 * - Added workspaceId to CreateProjectSchema (required by BE)
 */
import { z } from 'zod';
import { ProcessResponseSchema } from './processes';

// ============================================
// Project
// ============================================

export const ProjectSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().nullable().optional(),
  tags: z.array(z.string()).default([]),
  total_files: z.number().default(0),
  total_analyses: z.number().default(0),
  created_at: z.string(),
  updated_at: z.string().nullable().optional(),
});

export type Project = z.infer<typeof ProjectSchema>;

export const ProjectDetailSchema = ProjectSchema.extend({
  // Backend returns 'datasets', not 'processes'
  datasets: z.array(ProcessResponseSchema).optional(),
});

export type ProjectDetail = z.infer<typeof ProjectDetailSchema>;

// ============================================
// Create/Update Project
// ============================================

export const CreateProjectSchema = z.object({
  name: z.string().min(1, 'Project name is required'),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
  // CRITICAL: workspaceId is REQUIRED by backend
  workspaceId: z.string().min(1, 'Workspace ID is required'),
});

export type CreateProject = z.infer<typeof CreateProjectSchema>;

export const UpdateProjectSchema = z.object({
  name: z.string().min(1).optional(),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
});

export type UpdateProject = z.infer<typeof UpdateProjectSchema>;

// ============================================
// Project List Response
// ============================================

export const ProjectListResponseSchema = z.object({
  items: z.array(ProjectSchema),
  total: z.number(),
  page: z.number().optional(),
  page_size: z.number().optional(),
  pages: z.number().optional(),
});

export type ProjectListResponse = z.infer<typeof ProjectListResponseSchema>;

// ============================================
// Add Dataset to Project
// ============================================

export const AddDatasetToProjectSchema = z.object({
  dataset_id: z.string(),
});

export type AddDatasetToProject = z.infer<typeof AddDatasetToProjectSchema>;

// Legacy alias for backward compatibility
export const AddProcessToProjectSchema = AddDatasetToProjectSchema;
export type AddProcessToProject = AddDatasetToProject;
