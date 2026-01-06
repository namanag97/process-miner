"""Datasets Domain - Data Upload, Ingestion & Storage.

This domain handles the complete data lifecycle:
- File upload (direct and presigned S3)
- Column detection and schema inference
- Column mapping for process mining columns
- Data ingestion pipeline (DuckDB-based)
- File storage (S3/MinIO)
- Dataset metadata management
- Future: External data connectors

Key Models:
- Dataset: Core event log entity
- DatasetColumn: Detected columns from files
- DatasetColumnMapping: User-defined column mappings
- UploadedFile: File tracking for uploads
- DatasetMetadata: Computed metadata after ingestion

APIs:
- POST /datasets/ - Direct file upload
- POST /datasets/presign - Get presigned S3 URL
- GET /datasets/{id}/columns - Get detected columns
- POST /datasets/{id}/mapping - Submit column mapping
- POST /datasets/{id}/ingest - Trigger ingestion
- GET /datasets/ - List datasets
- GET /datasets/{id} - Get dataset details
- DELETE /datasets/{id} - Delete dataset
"""

# NOTE: API routers should be imported directly from src.domains.datasets.api
# NOT from this module to avoid circular imports
