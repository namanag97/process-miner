// Basic types for ProcessMiner application

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface DataModel {
  id: string;
  name: string;
  description?: string;
  status: 'processing' | 'ready' | 'failed';
  caseCount: number;
  eventCount: number;
  activities: string[];
  fileName: string;
  fileSize: number;
  uploadedAt: Date;
  processedAt?: Date;
  userId: string;
}

export interface ProcessCase {
  id: string;
  caseId: string;
  events: ProcessEvent[];
  startTime: Date;
  endTime: Date;
  duration: number;
  dataModelId: string;
}

export interface ProcessEvent {
  id: string;
  activity: string;
  timestamp: Date;
  caseId: string;
  attributes?: Record<string, unknown>;
}

export interface ProcessActivity {
  name: string;
  frequency: number;
  avgDuration: number;
  minDuration: number;
  maxDuration: number;
}

export interface ProcessTransition {
  source: string;
  target: string;
  frequency: number;
  avgDuration: number;
}

export interface ProcessModel {
  activities: ProcessActivity[];
  transitions: ProcessTransition[];
  startActivity: string;
  endActivity: string;
  totalCases: number;
  totalEvents: number;
}

export interface ProcessVariant {
  id: string;
  activities: string[];
  caseCount: number;
  percentage: number;
  avgDuration: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Dashboard stats
export interface DashboardStats {
  dataModels: number;
  totalCases: number;
  totalEvents: number;
  lastUpload: Date | null;
}
