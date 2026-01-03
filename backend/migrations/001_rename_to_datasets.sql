-- Migration: Rename event_logs to datasets for better ontological naming
-- This aligns the database with the ORM models

-- Step 1: Rename event_logs table to datasets
ALTER TABLE event_logs RENAME TO datasets;

-- Step 2: Rename log_id to dataset_id in process_cases
-- SQLite doesn't support renaming columns directly, so we need to recreate the table
CREATE TABLE process_cases_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    case_id VARCHAR(255) NOT NULL,
    variant_key TEXT,
    start_time DATETIME,
    end_time DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);

-- Copy data from old table
INSERT INTO process_cases_new (id, dataset_id, case_id, variant_key, start_time, end_time)
SELECT id, log_id, case_id, variant_key, start_time, end_time
FROM process_cases;

-- Drop old table and rename new one
DROP TABLE process_cases;
ALTER TABLE process_cases_new RENAME TO process_cases;

-- Recreate index
CREATE INDEX ix_process_cases_case_id ON process_cases (case_id);

-- Step 3: Rename log_id to dataset_id in uploaded_files
CREATE TABLE uploaded_files_new (
    id VARCHAR(36) NOT NULL,
    dataset_id VARCHAR(36) NOT NULL,
    filename VARCHAR(500) NOT NULL,
    storage_path VARCHAR(1000) NOT NULL,
    size_bytes INTEGER,
    mime_type VARCHAR(100),
    checksum VARCHAR(64),
    created_at DATETIME NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (dataset_id),
    FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);

-- Copy data from old table
INSERT INTO uploaded_files_new (id, dataset_id, filename, storage_path, size_bytes, mime_type, checksum, created_at)
SELECT id, log_id, filename, storage_path, size_bytes, mime_type, checksum, created_at
FROM uploaded_files;

-- Drop old table and rename new one
DROP TABLE uploaded_files;
ALTER TABLE uploaded_files_new RENAME TO uploaded_files;

-- Step 4: Update datasets table to rename source_log_id to source_dataset_id
-- This requires recreating the datasets table
CREATE TABLE datasets_new (
    id VARCHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    source_file VARCHAR(500),
    source_format VARCHAR(20) NOT NULL,
    project_id VARCHAR(36),
    total_cases INTEGER NOT NULL,
    total_events INTEGER NOT NULL,
    total_activities INTEGER NOT NULL,
    activities_json TEXT,
    statistics_json TEXT,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    mapping_json TEXT,
    source_dataset_id VARCHAR(36),
    filter_config_json TEXT,
    is_filtered BOOLEAN NOT NULL,
    filter_stats_json TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME,
    PRIMARY KEY (id),
    FOREIGN KEY(project_id) REFERENCES projects (id) ON DELETE SET NULL,
    FOREIGN KEY(source_dataset_id) REFERENCES datasets (id) ON DELETE CASCADE
);

-- Copy data from old table
INSERT INTO datasets_new 
SELECT id, name, source_file, source_format, project_id, total_cases, total_events, 
       total_activities, activities_json, statistics_json, status, error_message, 
       NULL as mapping_json, source_log_id, filter_config_json, is_filtered, 
       filter_stats_json, created_at, updated_at
FROM datasets;

-- Drop old table and rename new one
DROP TABLE datasets;
ALTER TABLE datasets_new RENAME TO datasets;
