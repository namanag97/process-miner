/**
 * Projects Zod Schemas
 */
import { z } from 'zod';
import { ProcessResponseSchema } from './processes';

// ============================================
// Project
// ============================================

export const ProjectSchema = z.object({
  id: z.string(),
  name: z.string(),
  description: z.string().optional(),
  created_at: z.string(),
  updated_at: z.string().optional(),
  process_count: z.number().default(0),
});

export type Project = z.infer<typeof ProjectSchema>;

export const ProjectDetailSchema = ProjectSchema.extend({
  processes: z.array(ProcessResponseSchema).optional(),
});

export type ProjectDetail = z.infer<typeof ProjectDetailSchema>;

// ============================================
// Create/Update Project
// ============================================

export const CreateProjectSchema = z.object({
  name: z.string().min(1, 'Project name is required'),
  description: z.string().optional(),
});

export type CreateProject = z.infer<typeof CreateProjectSchema>;

export const UpdateProjectSchema = z.object({
  name: z.string().min(1).optional(),
  description: z.string().optional(),
});

export type UpdateProject = z.infer<typeof UpdateProjectSchema>;

// ============================================
// Project List Response
// ============================================

export const ProjectListResponseSchema = z.object({
  items: z.array(ProjectSchema),
  total: z.number(),
});

export type ProjectListResponse = z.infer<typeof ProjectListResponseSchema>;

// ============================================
// Add Process to Project
// ============================================

export const AddProcessToProjectSchema = z.object({
  process_id: z.string(),
});

export type AddProcessToProject = z.infer<typeof AddProcessToProjectSchema>;
