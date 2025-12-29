/**
 * Visualization Types - Process Visualization
 *
 * TODO: These types should be auto-generated from OpenAPI spec
 * For now, they match the backend Pydantic schemas
 */

export interface DFGNode {
  id: string;
  label: string;
  frequency: number;
}

export interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  performance?: number;
}

export interface DFGResponse {
  log_id: string;
  nodes: DFGNode[];
  edges: DFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_cases: number;
}

export interface PetriNetPlace {
  id: string;
  name: string;
}

export interface PetriNetTransition {
  id: string;
  name: string;
  label?: string;
}

export interface PetriNetArc {
  source: string;
  target: string;
  weight?: number;
}

export interface PetriNetMarking {
  [placeId: string]: number;
}

export interface PetriNetResponse {
  model_id: string;
  places: PetriNetPlace[];
  transitions: PetriNetTransition[];
  arcs: PetriNetArc[];
  initial_marking: PetriNetMarking;
  final_marking: PetriNetMarking;
}

export interface FootprintsResponse {
  log_id: string;
  activities: string[];
  sequence_relations: Array<[string, string]>;
  parallel_relations: Array<[string, string]>;
  choice_relations: Array<[string, string]>;
  matrix: Record<string, Record<string, string>>;
}
