/**
 * Auth Types for Process Mining SDK
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// REQUEST TYPES
// =============================================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

// =============================================================================
// RESPONSE TYPES
// =============================================================================

export interface AuthToken extends HypermediaResponse {
  accessToken: string;
  tokenType: string;
}

export interface UserProfile extends HypermediaResponse {
  id: string;
  email: string;
  name?: string;
  roles?: string[];
}
