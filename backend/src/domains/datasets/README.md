# Datasets Domain

Data lifecycle management - upload, ingestion, storage.

## Responsibilities
- File upload (direct & presigned S3)
- Column detection and mapping
- Data ingestion (DuckDB-based)
- Dataset CRUD operations
- File storage (S3/MinIO)

## Usage
```python
from src.domains.datasets.models import Dataset, DatasetStatus
from src.domains.datasets.services import IngestionService
```
