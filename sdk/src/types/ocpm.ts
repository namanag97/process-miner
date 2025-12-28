/**
 * OCPM (Object-Centric Process Mining) Types
 */

import { HypermediaResponse } from './common.js';

// =============================================================================
// OCEL LOG
// =============================================================================

export interface OCELLog extends HypermediaResponse {
  id: string;
  name: string;
  sourceFile?: string;
  sourceFormat: string;
  totalEvents: number;
  totalObjects: number;
  totalObjectTypes: number;
  objectTypes: string[];
  activities: string[];
  createdAt: string;
}

export interface ObjectType extends HypermediaResponse {
  name: string;
  objectCount: number;
  attributes: string[];
}

export interface ObjectInstance extends HypermediaResponse {
  objectId: string;
  objectType: string;
  attributes: Record<string, unknown>;
}

// =============================================================================
// STATISTICS
// =============================================================================

export interface OCELStatistics extends HypermediaResponse {
  logId: string;
  totalEvents: number;
  totalObjects: number;
  totalObjectTypes: number;
  totalActivities: number;
  objectTypes: string[];
  activities: string[];
  objectsPerType: Record<string, number>;
}

// =============================================================================
// OBJECT-CENTRIC DFG
// =============================================================================

export interface OCDFGEdge {
  source: string;
  target: string;
  frequency: number;
}

export interface ObjectCentricDFG extends HypermediaResponse {
  logId: string;
  objectTypes: string[];
  activities: string[];
  edgesPerType: Record<string, OCDFGEdge[]>;
}

// =============================================================================
// OBJECT-CENTRIC PETRI NET
// =============================================================================

export interface OCPetriNet extends HypermediaResponse {
  id: string;
  logId: string;
  name: string;
  objectTypes: string[];
  createdAt: string;
}

// =============================================================================
// INGEST OPTIONS
// =============================================================================

export interface IngestOCELOptions {
  name?: string;
}
