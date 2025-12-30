# Backend API Documentation

**Base URL:** `http://localhost:8001/api`

> **⚠️ IMPORTANT:** This documentation shows both the **current implementation** and **recommended enhancements** to match pm4py's rich analysis capabilities.

---

## Response Structure Patterns

### Current Pattern (Simplified)

```typescript
{
  // Simple data without context
  "activity": "Approve",
  "count": 500
}
```

### Recommended Pattern (PM4Py-Aligned)

```typescript
{
  "metadata": {
    "analysis_timestamp": "ISO8601",
    "pm4py_version": "2.7.x",
    "total_cases": number,
    "total_events": number
  },
  "analyses": {
    "[analysis_name]": {
      "concept": "Human-readable name",
      "description": "What this analysis does",
      "reference": "Academic paper citation",
      "data": {
        // Actual analysis results
      }
    }
  }
}
```

---

## 1. Processes (Event Logs)

### 1.1 Upload Process

**POST** `/processes/upload`

**Current Response:**

```typescript
{
  id: string;
  name: string;
  source_format: "csv" | "xes";
  total_events: number;
  total_cases: number;
  total_activities: number;
  activities: string[];
  created_at: datetime;
}
```

**⚠️ Missing:** File validation details, column mapping confirmation, ingestion warnings/errors

**Recommended Enhancement:**

```typescript
{
  id: string;
  name: string;
  source_format: string;
  ingestion_metadata: {
    uploaded_at: datetime;
    file_size_bytes: number;
    processing_time_ms: number;
    warnings: string[];
    column_mapping: {
      case_id: string;
      activity: string;
      timestamp: string;
      resource?: string;
    };
  };
  statistics: {
    total_events: number;
    total_cases: number;
    total_activities: number;
    activities: string[];
    time_range: {
      start: datetime;
      end: datetime;
    };
  };
  created_at: datetime;
}
```

---

### 1.6 Get Statistics

**GET** `/processes/{process_id}/statistics`

**Current Response:**

```typescript
{
  total_events: number;
  total_cases: number;
  total_activities: number;
  total_variants: number;
  activities: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  avg_case_duration_seconds?: number;
  min_case_duration_seconds?: number;
  max_case_duration_seconds?: number;
  date_range?: { start: datetime; end: datetime };
}
```

**⚠️ Missing:** Academic context, analysis metadata, temporal statistics

**Recommended Enhancement:**

```typescript
{
  "metadata": {
    "analysis_timestamp": datetime;
    "pm4py_version": string;
    "log_id": string;
  },
  "analyses": {
    "event_data_statistics": {
      "concept": "Event Log Statistics",
      "description": "Basic statistics about the event log",
      "data": {
        "total_events": number;
        "total_cases": number;
        "total_activities": number;
        "total_variants": number;
        "activities": {
          "status": "success",
          "result": string[]
        },
        "start_activities": {
          "status": "success",
          "result": Record<string, number>
        },
        "end_activities": {
          "status": "success",
          "result": Record<string, number>
        },
        "activity_frequencies": {
          "status": "success",
          "result": Record<string, number>
        },
        "case_duration_stats": {
          "status": "success",
          "result": {
            "min_duration_seconds": number;
            "max_duration_seconds": number;
            "avg_duration_seconds": number;
            "median_duration_seconds": number;
          }
        }
      }
    },
    "temporal_statistics": {
      "concept": "Temporal Statistics",
      "description": "Time-based process statistics",
      "data": {
        "average_case_arrival_seconds": number;
        "log_timespan": {
          "start": datetime;
          "end": datetime;
        }
      }
    }
  }
}
```

---

## 2. Discovery

### 2.2 Discover Model

**POST** `/discovery/discover`

**Request:**

```typescript
{
  log_id: string;
  miner_type: "alpha" | "heuristics" | "inductive" | "dfg" | "split";
  model_name?: string;
}
```

**Current Response:**

```typescript
{
  id: string;
  name: string;
  miner_type: string;
  model_format: string;  // "petri_net", "process_tree", "dfg"
  log_id: string;
  fitness?: number;      // Single value, no context
  precision?: number;    // Single value, no context
  created_at: datetime;
}
```

**⚠️ Missing:**

- Algorithm metadata and references
- Detailed model structure
- Generation parameters
- Performance metrics

**Recommended Enhancement:**

```typescript
{
  id: string;
  name: string;
  log_id: string;
  discovery_metadata: {
    "concept": "Inductive Miner" | "Alpha Miner" | etc;
    "description": "Algorithm description";
    "reference": "Academic paper citation";
    "discovered_at": datetime;
    "processing_time_ms": number;
  },
  model_data: {
    "miner_type": string;
    "model_format": string;
    "structure": {
      // For Petri Net
      "places": string[];
      "transitions": string[];
      "arcs": string[];
      "initial_marking": string;
      "final_marking": string;
    } | {
      // For Process Tree
      "tree_string": string;
      "operator": string;
      "label": string | null;
    } | {
      // For DFG
      "nodes": string[];
      "edges": Record<string, number>;
    }
  },
  quality_metrics: {
    "fitness": {
      "value": number;
      "evaluation_method": "token_based_replay";
      "details": {
        "percentage_fit_traces": number;
        "average_trace_fitness": number;
        "log_fitness": number;
      }
    },
    "precision": {
      "value": number;
      "evaluation_method": "token_based_replay";
      "reference": "Munoz-Gama et al. - A fresh look at precision in process conformance";
    },
    "generalization": number;
    "simplicity": number;
  },
  created_at: datetime;
}
```

---

## 3. Visualization

### 3.1 Get DFG

**GET** `/visualization/{log_id}/dfg`

**Current Response:**

```typescript
{
  nodes: {
    id: string;
    name: string;
    frequency: number;
    is_start?: boolean;
    is_end?: boolean;
  }[];
  edges: {
    source: string;
    target: string;
    frequency: number;
    probability: number;
  }[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_frequency: number;
}
```

**✅ Adequate** but could be enhanced with:

**Recommended Enhancement:**

```typescript
{
  "metadata": {
    "log_id": string;
    "generated_at": datetime;
    "algorithm": "directly_follows_graph";
  },
  "analysis": {
    "concept": "Directly-Follows Graph (DFG)",
    "description": "Shows frequency of activity sequences",
    "reference": "van der Aalst - A practitioner's guide to process mining",
  },
  "graph": {
    "nodes": Array<{
      id: string;
      name: string;
      frequency: number;
      is_start: boolean;
      is_end: boolean;
    }>;
    "edges": Array<{
      source: string;
      target: string;
      frequency: number;
      probability: number;
    }>;
    "statistics": {
      "total_activities": number;
      "total_transitions": number;
      "total_frequency": number;
      "start_activities": Record<string, number>;
      "end_activities": Record<string, number>;
    }
  }
}
```

---

## 4. Conformance

### 4.1 Check Conformance

**POST** `/conformance/check`

**Current Response:**

```typescript
{
  id: string;
  log_id: string;
  model_id: string;
  fitness: number;          // Just a number
  precision?: number;       // Just a number
  method: string;
  is_conformant: boolean;   // Arbitrary threshold
  fitting_traces: number;
  total_traces: number;
  created_at: datetime;
}
```

**⚠️ Missing:**

- Detailed conformance diagnostics
- Token replay details
- Alignment information
- Academic references

**Recommended Enhancement:**

```typescript
{
  id: string;
  log_id: string;
  model_id: string;
  created_at: datetime;

  "analyses": {
    "token_based_replay": {
      "concept": "Token-Based Replay",
      "description": "Conformance checking using token replay",
      "reference": "Berti et al. - A novel token-based replay technique",
      "data": {
        "total_traces": number;
        "total_produced_tokens": number;
        "total_consumed_tokens": number;
        "total_missing_tokens": number;
        "total_remaining_tokens": number;
        "trace_fitness_available": boolean;
        "diagnostics": Array<{
          "trace_index": number;
          "trace_is_fit": boolean;
          "missing_tokens": number;
          "remaining_tokens": number;
          "produced_tokens": number;
          "consumed_tokens": number;
        }>
      }
    },

    "alignments": {
      "concept": "Alignments",
      "description": "Optimal alignment between log and model",
      "reference": "Adriansyah et al. - Conformance checking using cost-based fitness analysis",
      "data": {
        "total_traces_aligned": number;
        "average_alignment_cost": number;
        "min_cost": number;
        "max_cost": number;
        "alignments": Array<{
          "case_id": string;
          "cost": number;
          "alignment": Array<{
            "log_move": string | null;
            "model_move": string | null;
            "type": "sync" | "log" | "model";
          }>
        }>
      }
    },

    "fitness_evaluation": {
      "concept": "Fitness Evaluation",
      "description": "Measures how well the model reproduces the log",
      "reference": "Token-based replay fitness",
      "data": {
        "perc_fit_traces": number;
        "average_trace_fitness": number;
        "log_fitness": number;
        "percentage_of_fitting_traces": number;
      }
    },

    "precision_evaluation": {
      "concept": "Precision Evaluation",
      "description": "Measures model precision (avoids underfitting)",
      "reference": "Munoz-Gama et al. - A fresh look at precision in process conformance",
      "data": {
        "precision": number;
      }
    },

    "generalization_evaluation": {
      "concept": "Generalization Evaluation",
      "description": "Measures model generalization capability",
      "reference": "Buijs et al. - Quality dimensions in process discovery",
      "data": {
        "generalization": number;
      }
    },

    "simplicity_evaluation": {
      "concept": "Simplicity Evaluation",
      "description": "Measures structural simplicity of the model",
      "reference": "Vázquez-Barreiros et al. - ProDiGen",
      "data": {
        "simplicity": number;
      }
    }
  },

  "summary": {
    "is_conformant": boolean;
    "fitness": number;
    "precision": number;
    "generalization": number;
    "simplicity": number;
    "method": "token_replay" | "alignment";
    "fitting_traces": number;
    "total_traces": number;
  }
}
```

---

## 5. Analytics

### 5.1 Get Bottlenecks

**GET** `/analytics/logs/{log_id}/bottlenecks`

**Current Response:**

```typescript
{
  log_id: string;
  bottlenecks: Array<{
    activity: string;
    avg_waiting_time_seconds: number;
    avg_service_time_seconds: number;
    frequency: number;
    is_bottleneck: boolean;
    severity: "low" | "medium" | "high";
  }>;
  total_bottlenecks: number;
}
```

**⚠️ Missing:** Analysis metadata, methodology reference

**Recommended Enhancement:**

```typescript
{
  "metadata": {
    "log_id": string;
    "analysis_timestamp": datetime;
    "analysis_duration_ms": number;
  },
  "analysis": {
    "concept": "Bottleneck Detection",
    "description": "Identifies process bottlenecks based on waiting times",
    "methodology": "Waiting time threshold analysis (>1 hour = bottleneck)",
    "reference": "van der Aalst - Process Mining: Data Science in Action (Ch. 7)"
  },
  "data": {
    "bottlenecks": Array<{
      activity: string;
      avg_waiting_time_seconds: number;
      avg_service_time_seconds: number;
      frequency: number;
      is_bottleneck: boolean;
      severity: "low" | "medium" | "high";
      percentile_90_waiting_time: number;
      percentile_95_waiting_time: number;
    }>;
    "summary": {
      "total_bottlenecks": number;
      "total_activities_analyzed": number;
      "high_severity_count": number;
      "medium_severity_count": number;
      "low_severity_count": number;
    }
  }
}
```

---

### 5.7 Get Performance Dashboard

**GET** `/analytics/logs/{log_id}/performance`

**Current Response:**

```typescript
{
  log_id: string;
  cycle_time: {
    min_seconds: number;
    max_seconds: number;
    avg_seconds: number;
    median_seconds: number;
    percentile_25_seconds: number;
    percentile_75_seconds: number;
    percentile_95_seconds: number;
  }
  throughput: {
    total_cases: number;
    completed_cases: number;
    cases_per_day: number;
    cases_per_week: number;
    cases_per_month: number;
    time_range_days: number;
  }
  top_bottlenecks: Array<BottleneckResponse>;
  rework_summary: {
    total_rework_cases: number;
    rework_percentage: number;
    top_rework_activities: Array<{
      activity: string;
      rework_count: number;
      cases_with_rework: number;
      rework_percentage: number;
    }>;
  }
}
```

**✅ Good structure** but missing metadata wrapper

---

## 6. Organizational Mining

### 6.1 Get Handover Network

**GET** `/organizational/logs/{log_id}/handover-network`

**Current Response:**

```typescript
{
  log_id: string;
  network_type: string;
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    weight: number;
  }>;
  edges: Array<{
    source: string;
    target: string;
    weight: number;
    label?: string;
  }>;
  metrics: object; // ⚠️ Unstructured
}
```

**⚠️ Missing:**

- Academic references
- Network metrics details
- Analysis methodology

**Recommended Enhancement:**

```typescript
{
  "metadata": {
    "log_id": string;
    "analysis_timestamp": datetime;
  },
  "analysis": {
    "concept": "Social Network Analysis - Handover of Work",
    "description": "Analyzes resource handover patterns",
    "reference": "van der Aalst et al. - Discovering social networks from event logs",
  },
  "network": {
    "network_type": "handover_of_work",
    "nodes": Array<{
      id: string;
      label: string;
      type: "resource";
      weight: number;
      centrality?: number;
    }>;
    "edges": Array<{
      source: string;
      target: string;
      weight: number;
      frequency: number;
      label?: string;
    }>;
  },
  "metrics": {
    "total_nodes": number;
    "total_edges": number;
    "network_density": number;
    "average_degree": number;
    "clustering_coefficient": number;
    "top_central_resources": Array<{
      resource: string;
      centrality_score: number;
      rank: number;
    }>;
  }
}
```

---

### 6.4 Get Roles

**GET** `/organizational/logs/{log_id}/roles`

**Current Response:**

```typescript
Array<{
  role_id: string;
  resources: string[];
  activities: string[];
}>;
```

**⚠️ Missing:** Analysis context, discovery methodology

**Recommended Enhancement:**

```typescript
{
  "metadata": {
    "log_id": string;
    "analysis_timestamp": datetime;
  },
  "analysis": {
    "concept": "Organizational Roles",
    "description": "Discovers roles based on activity-resource patterns",
    "reference": "Burattin et al. - Business models enhancement through discovery of roles",
    "methodology": "Clustering based on activity profiles"
  },
  "data": {
    "roles": Array<{
      "role_id": string;
      "role_name": string;  // Generated or inferred
      "resources": string[];
      "activities": string[];
      "activity_profile": Record<string, number>;  // Activity frequencies
      "resource_importance": Record<string, number>;
      "coverage": {
        "cases_covered": number;
        "events_covered": number;
        "coverage_percentage": number;
      }
    }>;
    "summary": {
      "total_roles": number;
      "total_resources": number;
      "unassigned_resources": string[];
    }
  }
}
```

---

## 7. OCPM (Object-Centric)

### 7.1 Upload OCEL

**POST** `/ocpm/upload`

**Current Response:**

```typescript
{
  id: string;
  name: string;
  source_format: "jsonocel" | "sqlite" | "xmlocel";
  total_events: number;
  total_objects: number;
  total_object_types: number;
  object_types: string[];
  activities: string[];
  created_at: datetime;
}
```

**⚠️ Missing:** Object relationships, type statistics

**Recommended Enhancement:**

```typescript
{
  id: string;
  name: string;
  created_at: datetime;

  "ingestion_metadata": {
    "source_format": string;
    "file_size_bytes": number;
    "processing_time_ms": number;
    "ocel_version": "2.0";
  },

  "statistics": {
    "total_events": number;
    "total_objects": number;
    "total_object_types": number;
    "total_activities": number;

    "object_types": Array<{
      "name": string;
      "object_count": number;
      "attributes": string[];
      "avg_lifecycle_events": number;
    }>;

    "activities": string[];

    "object_relationships": {
      "total_relationships": number;
      "relationships_by_type": Record<string, number>;
    };

    "event_object_mapping": {
      "avg_objects_per_event": number;
      "max_objects_per_event": number;
      "events_by_object_cardinality": Record<number, number>;
    }
  }
}
```

---

## 8. Predictions

### 8.1 Train Predictor

**POST** `/predictions/logs/{log_id}/train`

**Current Response (sync):**

```typescript
{
  id: string;
  log_id: string;
  target_type: "next_activity" | "remaining_time" | "outcome";
  algorithm: string;
  metrics: Record<string, number>; // ⚠️ Minimal
  trained_at: datetime;
}
```

**⚠️ Missing:**

- Training details
- Feature importance
- Model validation metrics
- Prediction examples

**Recommended Enhancement:**

```typescript
{
  id: string;
  log_id: string;
  target_type: string;

  "training_metadata": {
    "algorithm": string;
    "algorithm_params": Record<string, any>;
    "trained_at": datetime;
    "training_duration_ms": number;
    "training_data_size": {
      "total_cases": number;
      "training_cases": number;
      "validation_cases": number;
      "test_cases": number;
    };
  },

  "features": {
    "feature_count": number;
    "feature_types": string[];
    "feature_importance": Array<{
      "feature": string;
      "importance": number;
      "rank": number;
    }>;
  },

  "metrics": {
    "training_metrics": {
      "accuracy"?: number;
      "precision"?: number;
      "recall"?: number;
      "f1_score"?: number;
      "mae"?: number;
      "rmse"?: number;
    };
    "validation_metrics": { /* same structure */ };
    "test_metrics": { /* same structure */ };
  },

  "model_info": {
    "model_size_bytes": number;
    "supported_prefix_lengths": {
      "min": number;
      "max": number;
    };
  }
}
```

---

### 8.5 Predict

**POST** `/predictions/predictors/{predictor_id}/predict`

**Current Response:**

```typescript
{
  predictor_id: string;
  case_prefix: string[];
  prediction: any;           // ⚠️ Type varies
  confidence?: number;
  alternatives?: object[];
}
```

**Recommended Enhancement:**

```typescript
{
  predictor_id: string;
  prediction_metadata: {
    "predicted_at": datetime;
    "prediction_time_ms": number;
    "model_version": string;
  },

  "input": {
    "case_prefix": string[];
    "prefix_length": number;
    "case_attributes"?: object;
  },

  "prediction": {
    // For next_activity
    "predicted_activity": string;
    "confidence": number;
    "alternatives": Array<{
      "activity": string;
      "probability": number;
      "rank": number;
    }>;
  } | {
    // For remaining_time
    "predicted_remaining_seconds": number;
    "confidence_interval": {
      "lower": number;
      "upper": number;
      "confidence_level": number;  // e.g., 0.95
    };
  } | {
    // For outcome
    "predicted_outcome": string;
    "confidence": number;
    "probabilities": Record<string, number>;
  },

  "explanation": {
    "feature_contributions": Array<{
      "feature": string;
      "contribution": number;
    }>;
    "similar_cases": Array<{
      "case_id": string;
      "similarity": number;
      "actual_outcome": string;
    }>;
  }
}
```

---

## Common Issues & Recommendations

### 1. **Missing Metadata**

❌ **Current:** Direct data responses  
✅ **Should:** Wrap with metadata (timestamps, versions, processing times)

### 2. **Missing Academic Context**

❌ **Current:** Results without explanation  
✅ **Should:** Include concept, description, references

### 3. **Inconsistent Error Handling**

❌ **Current:** HTTP errors only  
✅ **Should:** Per-analysis status with errors/warnings

### 4. **Limited Quality Metrics**

❌ **Current:** Single fitness/precision values  
✅ **Should:** Comprehensive quality assessment with multiple dimensions

### 5. **No Analysis Provenance**

❌**Current:** Results without methodology  
✅ **Should:** Document analysis parameters, thresholds, algorithms used

---

## Migration Guide: Enhancing Responses

To align with pm4py's rich outputs:

1. **Wrap all analysis responses** with metadata section
2. **Add academic references** for discovery/conformance algorithms
3. **Include per-analysis status** ("success", "failed", "partial")
4. **Expand quality metrics** beyond single values
5. **Add processing metadata** (timestamps, durations, versions)
6. **Document analysis parameters** (thresholds, algorithms, settings)
7. **Provide detailed diagnostics** for conformance checking
8. **Include feature importance** for ML predictions

---

## Error Responses

**Current:**

```json
{
  "type": "error",
  "title": "NotFoundError",
  "status": 404,
  "detail": "Event log not found",
  "instance": "/api/processes/log_123"
}
```

**Recommended Enhancement:**

```json
{
  "type": "error",
  "title": "NotFoundError",
  "status": 404,
  "detail": "Event log not found",
  "instance": "/api/processes/log_123",
  "metadata": {
    "error_id": "uuid",
    "timestamp": "ISO8601",
    "request_id": "uuid"
  },
  "context": {
    "log_id": "log_123",
    "available_logs": number,
    "suggestion": "Use GET /api/processes to list available logs"
  }
}
```
