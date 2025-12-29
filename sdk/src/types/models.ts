/**
 * Process Models Types
 */

import { HypermediaResponse } from "./common.js";

export interface ProcessModelSummary extends HypermediaResponse {
  id: string;
  name: string;
  modelType: string;
  sourceLogId: string;
  createdAt: string;
  description?: string;
}

export interface UpdateModelMetadata {
  name?: string;
  description?: string;
}
