# Datasets Domain

**Owner**: Data Lifecycle Management  
**Bounded Context**: Event Log Upload, Ingestion, Storage

## Responsibilities

- File upload (direct & presigned S3 URLs)
- Column detection and schema inference
- Column mapping (user-defined process semantics)
- Data validation (format, structure, quality)
- DuckDB-based ingestion pipeline
- Event log storage and retrieval
- Dataset metadata computation
- Export functionality

## Models

| Model | Table | Description |
|-------|-------|-------------|
| `Dataset` | `datasets` | Core event log metadata |
| `DatasetColumn` | `dataset_columns` | Detected columns from validation |
| `DatasetColumnMapping` | `dataset_column_mappings` | User-defined process mappings |
| `UploadedFile` | `uploaded_files` | Raw file storage metadata |
| `DatasetMetadata` | `dataset_metadata` | Computed statistics post-ingestion |

## Enums

- `DatasetStatus`: Lifecycle states (PENDING → UPLOADED → VALIDATING → AWAITING_MAPPING → MAPPED → INGESTING → READY)

## APIs

- `POST /datasets/` - Direct file upload
- `POST /datasets/presign` - Get presigned S3 URL
- `GET /datasets/{id}/columns` - Get detected columns
- `POST /datasets/{id}/mapping` - Submit column mapping
- `POST /datasets/{id}/ingest` - Trigger ingestion
- `GET /datasets/` - List datasets
- `GET /datasets/{id}` - Get dataset details
- `DELETE /datasets/{id}` - Delete dataset
- `GET /datasets/{id}/export` - Export dataset

## Services

- **Upload Service**: Handles file uploads and S3 presigned URLs
- **Storage Service**: S3/MinIO integration
- **Ingestion Service**: DuckDB-based data parsing and validation
- **Metadata Service**: Computes aggregate statistics

## Dependencies

**Outbound**:
- Admin domain (`Project` reference)
- Platform infrastructure (`AsyncJob` for background tasks)
- S3/MinIO for object storage
- DuckDB for high-performance ingestion

**Inbound**:
- Analysis domain (uses datasets for process mining)

## Domain Rules

1. Datasets must belong to a project
2. 4-Phase lifecycle: Upload → Validate → Map → Ingest
3. Column mapping required before ingestion
4. Ingestion is async (background job)
5. Only READY datasets can be analyzed

## Migration Notes

**Migrated from**:
- `src/features/process_mining/api/datasets/` → `src/domains/datasets/api/`
- `src/features/process_mining/models/dataset.py` → `src/domains/datasets/models/`
- `src/features/process_mining/ingestion/` → `src/domains/datasets/services/ingestion/`

**Backward compatibility**: Legacy imports still work via re-exports.
