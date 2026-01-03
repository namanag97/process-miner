-- MEGA-MIGRATION: Align all secondary tables with Dataset ontology
-- This ensures all features work with the renamed datasets table

-- Disable foreign keys temporarily to avoid constraint violations during migration
PRAGMA foreign_keys = OFF;

-- List of tables to fix (all currently reference non-existent event_logs or use log_id)

-- 1. analyses
CREATE TABLE analyses_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL,
    config_json TEXT,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    result_summary_json TEXT,
    model_id VARCHAR(36),
    created_at DATETIME NOT NULL,
    completed_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE,
    FOREIGN KEY(model_id) REFERENCES process_models (id) ON DELETE SET NULL
);
INSERT INTO analyses_new SELECT id, log_id, name, analysis_type, config_json, status, error_message, result_summary_json, model_id, created_at, completed_at FROM analyses;
DROP TABLE analyses;
ALTER TABLE analyses_new RENAME TO analyses;

-- 2. analytics_cache
CREATE TABLE analytics_cache_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    result_json TEXT,
    computed_at DATETIME NOT NULL,
    ttl_seconds INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);
INSERT INTO analytics_cache_new SELECT id, log_id, metric_type, result_json, computed_at, ttl_seconds FROM analytics_cache;
DROP TABLE analytics_cache;
ALTER TABLE analytics_cache_new RENAME TO analytics_cache;

-- 3. conformance_results
CREATE TABLE conformance_results_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    model_id VARCHAR(36) NOT NULL,
    fitness FLOAT NOT NULL,
    precision FLOAT,
    method VARCHAR(50) NOT NULL,
    generalization FLOAT,
    simplicity FLOAT,
    f_score FLOAT,
    non_fitting_traces INTEGER,
    average_alignment_cost FLOAT,
    diagnostics_json TEXT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE,
    FOREIGN KEY(model_id) REFERENCES process_models (id) ON DELETE CASCADE
);
INSERT INTO conformance_results_new SELECT id, log_id, model_id, fitness, precision, method, generalization, simplicity, f_score, non_fitting_traces, average_alignment_cost, diagnostics_json, created_at FROM conformance_results;
DROP TABLE conformance_results;
ALTER TABLE conformance_results_new RENAME TO conformance_results;

-- 4. prediction_models
CREATE TABLE prediction_models_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    target_type VARCHAR(50) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    model_binary BLOB,
    metrics_json TEXT,
    trained_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);
INSERT INTO prediction_models_new SELECT id, log_id, target_type, algorithm, model_binary, metrics_json, trained_at FROM prediction_models;
DROP TABLE prediction_models;
ALTER TABLE prediction_models_new RENAME TO prediction_models;

-- 5. process_models
CREATE TABLE process_models_new (
    id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    dataset_id VARCHAR(36),
    miner_type VARCHAR(50) NOT NULL,
    model_format VARCHAR(50) NOT NULL,
    serialized_model BLOB,
    fitness FLOAT,
    precision FLOAT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE SET NULL
);
INSERT INTO process_models_new SELECT id, name, log_id, miner_type, model_format, serialized_model, fitness, precision, created_at FROM process_models;
DROP TABLE process_models;
ALTER TABLE process_models_new RENAME TO process_models;

-- 6. recommendations
CREATE TABLE recommendations_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    case_id VARCHAR(255) NOT NULL,
    signal_type VARCHAR(50) NOT NULL,
    signal_data_json TEXT,
    action_type VARCHAR(50) NOT NULL,
    action_params_json TEXT,
    priority VARCHAR(20) NOT NULL,
    state VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);
INSERT INTO recommendations_new SELECT id, log_id, case_id, signal_type, signal_data_json, action_type, action_params_json, priority, state, created_at FROM recommendations;
DROP TABLE recommendations;
ALTER TABLE recommendations_new RENAME TO recommendations;

-- 7. social_networks
CREATE TABLE social_networks_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    network_type VARCHAR(50) NOT NULL,
    graph_json TEXT,
    metrics_json TEXT,
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);
INSERT INTO social_networks_new SELECT id, log_id, network_type, graph_json, metrics_json, created_at FROM social_networks;
DROP TABLE social_networks;
ALTER TABLE social_networks_new RENAME TO social_networks;

-- 8. workflow_runs
CREATE TABLE workflow_runs_new (
    id VARCHAR(36) NOT NULL,
    workflow_id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36),
    status VARCHAR(50) NOT NULL,
    result_json TEXT,
    error TEXT,
    started_at DATETIME,
    completed_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(workflow_id) REFERENCES workflows (id) ON DELETE CASCADE,
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE SET NULL
);
INSERT INTO workflow_runs_new SELECT id, workflow_id, log_id, status, result_json, error, started_at, completed_at FROM workflow_runs;
DROP TABLE workflow_runs;
ALTER TABLE workflow_runs_new RENAME TO workflow_runs;

-- 9. ocel2_events
CREATE TABLE ocel2_events_new (
    id VARCHAR(36) NOT NULL,
    event_type_id VARCHAR(36) NOT NULL,
    activity VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    attributes JSON,
    source_dataset_id VARCHAR(36),
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(event_type_id) REFERENCES ocel2_event_types (id) ON DELETE CASCADE,
    FOREIGN KEY(source_dataset_id) REFERENCES datasets (id) ON DELETE SET NULL
);
INSERT INTO ocel2_events_new SELECT id, event_type_id, activity, timestamp, attributes, source_log_id, created_at FROM ocel2_events;
DROP TABLE ocel2_events;
ALTER TABLE ocel2_events_new RENAME TO ocel2_events;

-- Re-enable foreign keys
PRAGMA foreign_keys = ON;
