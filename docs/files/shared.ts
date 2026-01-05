// ============================================================================
// types/shared.ts
// SINGLE SOURCE OF TRUTH FOR ALL TYPES
// 
// RULES:
// - Import this file in ALL frontend and backend code
// - NEVER use 'any' type - always use these definitions
// - Enums MUST match database CHECK constraints exactly
// - Update this file FIRST when adding new features
// ============================================================================

// ============================================================================
// ENUMS (Must match database ENUM types exactly)
// ============================================================================

export const ORG_ROLES = ['owner', 'admin', 'member'] as const;
export type OrgRole = typeof ORG_ROLES[number];

export const WORKSPACE_ROLES = ['owner', 'admin', 'editor', 'viewer'] as const;
export type WorkspaceRole = typeof WORKSPACE_ROLES[number];

export const PLAN_TYPES = ['free', 'pro', 'enterprise'] as const;
export type PlanType = typeof PLAN_TYPES[number];

export const DATASET_STATUSES = ['pending', 'processing', 'ready', 'error', 'archived'] as const;
export type DatasetStatus = typeof DATASET_STATUSES[number];

export const JOB_STATUSES = ['pending', 'processing', 'completed', 'failed', 'cancelled'] as const;
export type JobStatus = typeof JOB_STATUSES[number];

export const INVITATION_STATUSES = ['pending', 'accepted', 'expired', 'revoked'] as const;
export type InvitationStatus = typeof INVITATION_STATUSES[number];

export const NOTIFICATION_TYPES = ['info', 'success', 'warning', 'error'] as const;
export type NotificationType = typeof NOTIFICATION_TYPES[number];

export const AUTH_PROVIDERS = ['email', 'google', 'microsoft', 'saml'] as const;
export type AuthProvider = typeof AUTH_PROVIDERS[number];

// ============================================================================
// ERROR CODES (Use these for consistent error handling)
// ============================================================================

export const ERROR_CODES = {
  // Auth errors (401)
  UNAUTHORIZED: 'UNAUTHORIZED',
  INVALID_CREDENTIALS: 'INVALID_CREDENTIALS',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  ACCOUNT_LOCKED: 'ACCOUNT_LOCKED',
  EMAIL_NOT_VERIFIED: 'EMAIL_NOT_VERIFIED',
  
  // Permission errors (403)
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_ROLE: 'INSUFFICIENT_ROLE',
  NOT_MEMBER: 'NOT_MEMBER',
  
  // Resource errors (404, 409)
  NOT_FOUND: 'NOT_FOUND',
  ALREADY_EXISTS: 'ALREADY_EXISTS',
  CONFLICT: 'CONFLICT',
  
  // Validation errors (400)
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  
  // Limit errors (402, 429)
  QUOTA_EXCEEDED: 'QUOTA_EXCEEDED',
  RATE_LIMITED: 'RATE_LIMITED',
  FILE_TOO_LARGE: 'FILE_TOO_LARGE',
  
  // System errors (500, 503)
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
} as const;

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES];

// ============================================================================
// ROLE PERMISSIONS (Use for authorization checks)
// ============================================================================

export const ORG_ROLE_HIERARCHY: Record<OrgRole, number> = {
  owner: 3,
  admin: 2,
  member: 1,
};

export const WORKSPACE_ROLE_HIERARCHY: Record<WorkspaceRole, number> = {
  owner: 4,
  admin: 3,
  editor: 2,
  viewer: 1,
};

export type WorkspaceAction = 
  | 'workspace.read'
  | 'workspace.update'
  | 'workspace.delete'
  | 'workspace.manage_members'
  | 'project.create'
  | 'project.read'
  | 'project.update'
  | 'project.delete'
  | 'dataset.create'
  | 'dataset.read'
  | 'dataset.update'
  | 'dataset.delete';

export const WORKSPACE_ACTION_REQUIRED_ROLES: Record<WorkspaceAction, WorkspaceRole> = {
  'workspace.read': 'viewer',
  'workspace.update': 'admin',
  'workspace.delete': 'owner',
  'workspace.manage_members': 'admin',
  'project.create': 'editor',
  'project.read': 'viewer',
  'project.update': 'editor',
  'project.delete': 'admin',
  'dataset.create': 'editor',
  'dataset.read': 'viewer',
  'dataset.update': 'editor',
  'dataset.delete': 'admin',
};

// ============================================================================
// BASE TYPES
// ============================================================================

/** All entities have these fields */
export interface BaseEntity {
  id: string;
  createdAt: string;  // ISO 8601 format
  updatedAt: string;
  deletedAt: string | null;
}

/** Standard API response wrapper */
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
  meta?: {
    timestamp: string;
    requestId: string;
  };
}

/** Standard error format */
export interface ApiError {
  code: ErrorCode;
  message: string;
  details?: Record<string, string[]>;  // Field-level validation errors
}

/** Paginated list response */
export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: PaginationMeta;
}

export interface PaginationMeta {
  page: number;
  pageSize: number;
  totalCount: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

/** Pagination query params */
export interface PaginationParams {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// ============================================================================
// DOMAIN ENTITIES
// ============================================================================

export interface User extends BaseEntity {
  email: string;
  emailVerified: boolean;
  emailVerifiedAt: string | null;
  displayName: string | null;
  avatarUrl: string | null;
  authProvider: AuthProvider;
  timezone: string;
  locale: string;
  theme: string;
  lastLoginAt: string | null;
}

export interface UserSession {
  id: string;
  userId: string;
  deviceInfo: string | null;
  ipAddress: string | null;
  expiresAt: string;
  lastUsedAt: string;
  createdAt: string;
}

export interface Organization extends BaseEntity {
  name: string;
  slug: string;
  logoUrl: string | null;
  plan: PlanType;
  planStartedAt: string | null;
  trialEndsAt: string | null;
  createdBy: string | null;
}

export interface OrganizationMember {
  id: string;
  organizationId: string;
  userId: string;
  role: OrgRole;
  createdAt: string;
  updatedAt: string;
  invitedBy: string | null;
  // Populated via JOIN
  user?: User;
}

export interface Invitation {
  id: string;
  organizationId: string;
  workspaceId: string | null;
  email: string;
  role: string;
  status: InvitationStatus;
  expiresAt: string;
  acceptedAt: string | null;
  acceptedBy: string | null;
  createdAt: string;
  invitedBy: string;
  // Populated via JOIN
  inviter?: User;
}

export interface Workspace extends BaseEntity {
  organizationId: string;
  name: string;
  description: string | null;
  createdBy: string | null;
  // Populated via JOIN or separate query
  memberCount?: number;
  projectCount?: number;
}

export interface WorkspaceMember {
  id: string;
  workspaceId: string;
  userId: string;
  role: WorkspaceRole;
  createdAt: string;
  updatedAt: string;
  addedBy: string | null;
  // Populated via JOIN
  user?: User;
}

export interface Project extends BaseEntity {
  workspaceId: string;
  name: string;
  description: string | null;
  tags: string[];
  datasetCount: number;
  totalCases: number;
  createdBy: string | null;
}

export interface Dataset extends BaseEntity {
  projectId: string;
  name: string;
  description: string | null;
  sourceFilename: string;
  sourceFilePath: string;
  fileSizeBytes: number;
  fileType: string;
  fileHash: string | null;
  status: DatasetStatus;
  errorMessage: string | null;
  errorDetails: Record<string, unknown> | null;
  processingStartedAt: string | null;
  processedAt: string | null;
  caseCount: number | null;
  eventCount: number | null;
  activityCount: number | null;
  dateRangeStart: string | null;
  dateRangeEnd: string | null;
  columnMapping: ColumnMapping | null;
  createdBy: string | null;
}

export interface ColumnMapping {
  caseId: string;
  activity: string;
  timestamp: string;
  resource?: string;
  customAttributes?: string[];
}

export interface FileUpload {
  id: string;
  organizationId: string;
  filename: string;
  fileSizeBytes: number;
  mimeType: string | null;
  uploadId: string | null;
  chunksTotal: number;
  chunksUploaded: number;
  storagePath: string | null;
  storageProvider: string;
  status: string;
  completedAt: string | null;
  expiresAt: string;
  createdAt: string;
  createdBy: string | null;
}

export interface Job {
  id: string;
  organizationId: string;
  jobType: string;
  jobData: Record<string, unknown>;
  priority: number;
  status: JobStatus;
  progressPercent: number;
  progressMessage: string | null;
  startedAt: string | null;
  completedAt: string | null;
  workerId: string | null;
  resultData: Record<string, unknown> | null;
  errorMessage: string | null;
  attemptCount: number;
  maxAttempts: number;
  nextRetryAt: string | null;
  createdAt: string;
  createdBy: string | null;
}

export interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  resourceType: string | null;
  resourceId: string | null;
  actionUrl: string | null;
  readAt: string | null;
  createdAt: string;
  expiresAt: string | null;
}

export interface NotificationPreferences {
  id: string;
  userId: string;
  inAppEnabled: boolean;
  emailEnabled: boolean;
  emailDigest: 'instant' | 'daily' | 'weekly';
  categorySettings: Record<string, { inApp: boolean; email: boolean }>;
}

export interface AuditLog {
  id: string;
  organizationId: string | null;
  userId: string | null;
  userEmail: string | null;
  ipAddress: string | null;
  userAgent: string | null;
  action: string;
  resourceType: string | null;
  resourceId: string | null;
  resourceName: string | null;
  oldValues: Record<string, unknown> | null;
  newValues: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  createdAt: string;
}

// ============================================================================
// REQUEST/INPUT TYPES
// ============================================================================

// Auth
export interface RegisterInput {
  email: string;
  password: string;
  displayName?: string;
  organizationName?: string;
}

export interface LoginInput {
  email: string;
  password: string;
  rememberMe?: boolean;
}

export interface LoginResponse {
  accessToken: string;
  refreshToken: string;
  expiresAt: string;
  user: User;
}

export interface ForgotPasswordInput {
  email: string;
}

export interface ResetPasswordInput {
  token: string;
  password: string;
}

export interface ChangePasswordInput {
  currentPassword: string;
  newPassword: string;
}

export interface ChangeEmailInput {
  newEmail: string;
  password: string;
}

// User
export interface UpdateUserInput {
  displayName?: string;
  avatarUrl?: string;
  timezone?: string;
  locale?: string;
  theme?: string;
}

// Organization
export interface CreateOrganizationInput {
  name: string;
  slug?: string;
}

export interface UpdateOrganizationInput {
  name?: string;
  slug?: string;
  logoUrl?: string;
}

// Invitation
export interface CreateInvitationInput {
  email: string;
  role: OrgRole | WorkspaceRole;
  workspaceId?: string;
}

export interface AcceptInvitationInput {
  token: string;
}

// Workspace
export interface CreateWorkspaceInput {
  organizationId: string;
  name: string;
  description?: string;
}

export interface UpdateWorkspaceInput {
  name?: string;
  description?: string;
}

export interface AddWorkspaceMemberInput {
  userId: string;
  role: WorkspaceRole;
}

export interface UpdateWorkspaceMemberInput {
  role: WorkspaceRole;
}

// Project
export interface CreateProjectInput {
  workspaceId: string;
  name: string;
  description?: string;
  tags?: string[];
}

export interface UpdateProjectInput {
  name?: string;
  description?: string;
  tags?: string[];
}

// Dataset
export interface CreateDatasetInput {
  projectId: string;
  name: string;
  description?: string;
  fileUploadId: string;
}

export interface UpdateDatasetInput {
  name?: string;
  description?: string;
  columnMapping?: ColumnMapping;
}

// File Upload
export interface InitUploadInput {
  filename: string;
  fileSizeBytes: number;
  mimeType?: string;
  chunksTotal?: number;
}

export interface InitUploadResponse {
  uploadId: string;
  uploadUrl?: string;  // For direct-to-storage uploads
  expiresAt: string;
}

// ============================================================================
// VALIDATION RULES
// ============================================================================

export const VALIDATION = {
  email: {
    maxLength: 255,
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  },
  password: {
    minLength: 8,
    maxLength: 128,
    pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/,
    message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number',
  },
  name: {
    minLength: 1,
    maxLength: 255,
  },
  slug: {
    minLength: 2,
    maxLength: 100,
    pattern: /^[a-z0-9-]+$/,
    message: 'Slug can only contain lowercase letters, numbers, and hyphens',
  },
  description: {
    maxLength: 2000,
  },
  tags: {
    maxCount: 20,
    maxTagLength: 50,
  },
} as const;

// ============================================================================
// PLAN LIMITS
// ============================================================================

export interface PlanLimits {
  maxWorkspaces: number;
  maxProjectsPerWorkspace: number;
  maxDatasetsPerProject: number;
  maxStorageBytes: number;
  maxFileSizeBytes: number;
  maxTeamMembers: number;
  maxCasesPerDataset: number;
  features: {
    apiAccess: boolean;
    ssoEnabled: boolean;
    auditLogs: boolean;
    advancedAnalytics: boolean;
    prioritySupport: boolean;
  };
}

export const PLAN_LIMITS: Record<PlanType, PlanLimits> = {
  free: {
    maxWorkspaces: 2,
    maxProjectsPerWorkspace: 5,
    maxDatasetsPerProject: 10,
    maxStorageBytes: 1 * 1024 * 1024 * 1024, // 1 GB
    maxFileSizeBytes: 50 * 1024 * 1024, // 50 MB
    maxTeamMembers: 3,
    maxCasesPerDataset: 10000,
    features: {
      apiAccess: false,
      ssoEnabled: false,
      auditLogs: false,
      advancedAnalytics: false,
      prioritySupport: false,
    },
  },
  pro: {
    maxWorkspaces: 10,
    maxProjectsPerWorkspace: 50,
    maxDatasetsPerProject: 100,
    maxStorageBytes: 50 * 1024 * 1024 * 1024, // 50 GB
    maxFileSizeBytes: 500 * 1024 * 1024, // 500 MB
    maxTeamMembers: 25,
    maxCasesPerDataset: 500000,
    features: {
      apiAccess: true,
      ssoEnabled: false,
      auditLogs: true,
      advancedAnalytics: true,
      prioritySupport: false,
    },
  },
  enterprise: {
    maxWorkspaces: -1, // Unlimited (-1 = unlimited)
    maxProjectsPerWorkspace: -1,
    maxDatasetsPerProject: -1,
    maxStorageBytes: -1,
    maxFileSizeBytes: 2 * 1024 * 1024 * 1024, // 2 GB
    maxTeamMembers: -1,
    maxCasesPerDataset: -1,
    features: {
      apiAccess: true,
      ssoEnabled: true,
      auditLogs: true,
      advancedAnalytics: true,
      prioritySupport: true,
    },
  },
};

// ============================================================================
// UTILITY TYPES
// ============================================================================

/** Make certain properties optional */
export type PartialBy<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/** Make certain properties required */
export type RequiredBy<T, K extends keyof T> = Omit<T, K> & Required<Pick<T, K>>;

/** Extract ID type from entity */
export type EntityId<T extends { id: string }> = T['id'];

/** Type for list filters */
export interface ListFilters {
  search?: string;
  status?: string;
  createdAfter?: string;
  createdBefore?: string;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Check if a role meets the minimum required level
 */
export function hasWorkspacePermission(
  userRole: WorkspaceRole,
  requiredRole: WorkspaceRole
): boolean {
  return WORKSPACE_ROLE_HIERARCHY[userRole] >= WORKSPACE_ROLE_HIERARCHY[requiredRole];
}

export function hasOrgPermission(
  userRole: OrgRole,
  requiredRole: OrgRole
): boolean {
  return ORG_ROLE_HIERARCHY[userRole] >= ORG_ROLE_HIERARCHY[requiredRole];
}

/**
 * Check if user can perform a workspace action
 */
export function canPerformWorkspaceAction(
  userRole: WorkspaceRole,
  action: WorkspaceAction
): boolean {
  const requiredRole = WORKSPACE_ACTION_REQUIRED_ROLES[action];
  return hasWorkspacePermission(userRole, requiredRole);
}

/**
 * Format file size for display
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * Check if limit is unlimited (-1)
 */
export function isUnlimited(limit: number): boolean {
  return limit === -1;
}

/**
 * Check if usage exceeds limit
 */
export function isOverLimit(usage: number, limit: number): boolean {
  if (isUnlimited(limit)) return false;
  return usage >= limit;
}
