"""Object Storage Client for S3/MinIO.

Production-grade abstraction for file storage with presigned URLs,
streaming support, and comprehensive error handling.

Supports:
- AWS S3 (production)
- MinIO (local development)
- LocalStack (testing)

Cost Optimization Features (Phase 12):
- Automatic compression for PNML/XML files (gzip)
- S3 lifecycle policies for tiered storage
- Automated deletion policies
- Storage cost tracking per tenant
"""

import gzip
import io
from collections.abc import Iterator
from pathlib import Path

import boto3
import structlog
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from src.platform.core.config import get_settings
from src.platform.core.exceptions import ProcessingError

logger = structlog.get_logger(__name__)
settings = get_settings()


class ObjectStorageError(ProcessingError):
    """Base exception for object storage operations."""

    def __init__(self, message: str, bucket: str | None = None, key: str | None = None):
        """Initialize storage error.

        Args:
            message: Error description
            bucket: S3 bucket name (if applicable)
            key: Object key (if applicable)
        """
        super().__init__(message)
        self.bucket = bucket
        self.key = key


class ObjectNotFoundError(ObjectStorageError):
    """Raised when object does not exist in storage."""


class ObjectStorageClient:
    """S3/MinIO client abstraction for file storage.

    Features:
    - Presigned URL generation for direct client uploads
    - Streaming upload/download to prevent memory exhaustion
    - Automatic bucket initialization
    - Multi-environment support (AWS/MinIO/LocalStack)

    Environment-based bucket naming:
    - Development: pm-raw-dev, pm-models-dev, pm-cache-dev
    - Production: pm-raw-prod, pm-models-prod, pm-cache-prod
    """

    # Bucket templates with environment suffix
    BUCKET_TEMPLATES = {
        "raw": "pm-raw",
        "models": "pm-models",
        "cache": "pm-cache",
    }

    def __init__(self):
        """Initialize S3/MinIO client from application settings."""
        self.settings = settings

        # Determine environment suffix from bucket name
        env_suffix = self.settings.s3_bucket_raw.split("-")[-1]  # Extract "dev" or "prod"

        # Construct bucket names with environment
        self.buckets = {
            "raw": f"{self.BUCKET_TEMPLATES['raw']}-{env_suffix}",
            "models": f"{self.BUCKET_TEMPLATES['models']}-{env_suffix}",
            "cache": f"{self.BUCKET_TEMPLATES['cache']}-{env_suffix}",
        }

        # Configure S3 client
        # For MinIO/LocalStack: endpoint_url is set
        # For AWS S3: endpoint_url is None (uses default AWS endpoints)
        self.client = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=self.settings.s3_access_key_id,
            aws_secret_access_key=self.settings.s3_secret_access_key,
            region_name=self.settings.s3_region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"} if self.settings.s3_endpoint_url else {},
            ),
        )

        logger.info(
            "object_storage_initialized",
            endpoint=self.settings.s3_endpoint_url or "AWS S3",
            region=self.settings.s3_region,
            buckets=list(self.buckets.values()),
        )

    def ensure_buckets_exist(self) -> None:
        """Create buckets if they don't exist.

        Should be called during application startup.
        Safe to call multiple times (idempotent).

        Raises:
            ObjectStorageError: If bucket creation fails
        """
        for bucket_type, bucket_name in self.buckets.items():
            try:
                self.client.head_bucket(Bucket=bucket_name)
                logger.debug("bucket_exists", bucket=bucket_name, bucket_type=bucket_type)
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                if error_code == "404":
                    # Bucket doesn't exist, create it
                    try:
                        if self.settings.s3_region == "us-east-1":
                            # us-east-1 doesn't accept LocationConstraint
                            self.client.create_bucket(Bucket=bucket_name)
                        else:
                            self.client.create_bucket(
                                Bucket=bucket_name,
                                CreateBucketConfiguration={
                                    "LocationConstraint": self.settings.s3_region
                                },
                            )
                        logger.info("bucket_created", bucket=bucket_name, bucket_type=bucket_type)
                    except (BotoCoreError, ClientError) as create_error:
                        raise ObjectStorageError(
                            f"Failed to create bucket: {create_error}",
                            bucket=bucket_name,
                        )
                else:
                    raise ObjectStorageError(
                        f"Failed to check bucket existence: {e}",
                        bucket=bucket_name,
                    )

    def get_presigned_upload_url(
        self,
        bucket_type: str,
        key: str,
        expires_in: int | None = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Generate presigned PUT URL for direct client-to-S3 upload.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key (path within bucket)
            expires_in: URL expiration in seconds (default from config)
            content_type: Expected content type for upload

        Returns:
            Presigned PUT URL valid for specified duration

        Raises:
            ObjectStorageError: If URL generation fails
            ValueError: If bucket_type is invalid
        """
        logger.info(
            "🔧 [STORAGE] get_presigned_upload_url called",
            bucket_type=bucket_type,
            key=key,
            content_type=content_type,
        )

        bucket = self._get_bucket(bucket_type)
        expires_in = expires_in or self.settings.s3_presigned_url_expiry

        logger.info(
            "🪣 [STORAGE] Bucket resolved and expiry set",
            bucket=bucket,
            expires_in=expires_in,
            s3_endpoint=self.settings.s3_endpoint_url,
            s3_region=self.settings.s3_region,
        )

        params = {
            "Bucket": bucket,
            "Key": key,
            "ContentType": content_type,
        }

        logger.info(
            "📋 [STORAGE] Generating presigned URL with params",
            params=params,
            http_method="PUT",
            client_method="put_object",
        )

        try:
            url = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params=params,
                ExpiresIn=expires_in,
                HttpMethod="PUT",
            )

            logger.info(
                "✅ [STORAGE] Presigned upload URL generated successfully",
                bucket=bucket,
                key=key,
                expires_in=expires_in,
                url_length=len(url),
                url_starts_with=url[:50] if url else None,
            )

            return url

        except BotoCoreError as e:
            logger.error(
                "❌ [STORAGE] BotoCoreError generating presigned URL",
                bucket=bucket,
                key=key,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise ObjectStorageError(
                f"Failed to generate presigned upload URL (BotoCoreError): {e}",
                bucket=bucket,
                key=key,
            )
        except ClientError as e:
            error_code = (
                e.response.get("Error", {}).get("Code") if hasattr(e, "response") else "Unknown"
            )
            error_message = (
                e.response.get("Error", {}).get("Message") if hasattr(e, "response") else str(e)
            )
            logger.error(
                "❌ [STORAGE] ClientError generating presigned URL",
                bucket=bucket,
                key=key,
                error_code=error_code,
                error_message=error_message,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise ObjectStorageError(
                f"Failed to generate presigned upload URL (ClientError): {e}",
                bucket=bucket,
                key=key,
            )
        except Exception as e:
            logger.error(
                "❌ [STORAGE] Unexpected error generating presigned URL",
                bucket=bucket,
                key=key,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise ObjectStorageError(
                f"Failed to generate presigned upload URL (Unexpected): {e}",
                bucket=bucket,
                key=key,
            )

    def get_presigned_download_url(
        self,
        bucket_type: str,
        key: str,
        expires_in: int | None = None,
        filename: str | None = None,
    ) -> str:
        """Generate presigned GET URL for direct client download.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key
            expires_in: URL expiration in seconds (default from config)
            filename: Optional Content-Disposition filename

        Returns:
            Presigned GET URL

        Raises:
            ObjectStorageError: If URL generation fails
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)
        expires_in = expires_in or self.settings.s3_presigned_url_expiry

        try:
            params = {"Bucket": bucket, "Key": key}

            if filename:
                params["ResponseContentDisposition"] = f'attachment; filename="{filename}"'

            url = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params=params,
                ExpiresIn=expires_in,
                HttpMethod="GET",
            )

            logger.info(
                "presigned_download_url_generated",
                bucket=bucket,
                key=key,
                expires_in=expires_in,
            )

            return url

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to generate presigned download URL: {e}",
                bucket=bucket,
                key=key,
            )

    def upload_file(
        self,
        bucket_type: str,
        key: str,
        file_path: Path,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Upload file from local filesystem to S3.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key
            file_path: Local file path to upload
            content_type: MIME type (auto-detected if None)
            metadata: Optional metadata dict

        Raises:
            ObjectStorageError: If upload fails
            ValueError: If bucket_type is invalid
            FileNotFoundError: If local file doesn't exist
        """
        bucket = self._get_bucket(bucket_type)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            extra_args: dict[str, str | dict[str, str]] = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_file(
                str(file_path),
                bucket,
                key,
                ExtraArgs=extra_args if extra_args else None,
            )

            logger.info(
                "file_uploaded",
                bucket=bucket,
                key=key,
                file_size=file_path.stat().st_size,
            )

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to upload file: {e}",
                bucket=bucket,
                key=key,
            )

    def upload_fileobj(
        self,
        bucket_type: str,
        key: str,
        file_obj: io.BytesIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Upload file object to S3 (streaming).

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key
            file_obj: File-like object (BytesIO, file handle)
            content_type: MIME type
            metadata: Optional metadata dict

        Raises:
            ObjectStorageError: If upload fails
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)

        try:
            extra_args: dict[str, str | dict[str, str]] = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = metadata

            self.client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs=extra_args if extra_args else None,
            )

            logger.info("fileobj_uploaded", bucket=bucket, key=key)

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to upload file object: {e}",
                bucket=bucket,
                key=key,
            )

    def download_file(self, bucket_type: str, key: str, dest_path: Path) -> None:
        """Download file from S3 to local filesystem.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key
            dest_path: Local destination path

        Raises:
            ObjectStorageError: If download fails
            ObjectNotFoundError: If object doesn't exist
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)

        try:
            # Ensure parent directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            self.client.download_file(bucket, key, str(dest_path))

            logger.info(
                "file_downloaded",
                bucket=bucket,
                key=key,
                dest_path=str(dest_path),
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise ObjectNotFoundError(
                    f"Object not found: {key}",
                    bucket=bucket,
                    key=key,
                )
            raise ObjectStorageError(
                f"Failed to download file: {e}",
                bucket=bucket,
                key=key,
            )
        except BotoCoreError as e:
            raise ObjectStorageError(
                f"Failed to download file: {e}",
                bucket=bucket,
                key=key,
            )

    def download_fileobj(self, bucket_type: str, key: str) -> io.BytesIO:
        """Download file from S3 to BytesIO object (streaming).

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key

        Returns:
            BytesIO object containing file contents

        Raises:
            ObjectStorageError: If download fails
            ObjectNotFoundError: If object doesn't exist
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)

        try:
            buffer = io.BytesIO()
            self.client.download_fileobj(bucket, key, buffer)
            buffer.seek(0)  # Reset to beginning for reading

            logger.info("fileobj_downloaded", bucket=bucket, key=key)

            return buffer

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise ObjectNotFoundError(
                    f"Object not found: {key}",
                    bucket=bucket,
                    key=key,
                )
            raise ObjectStorageError(
                f"Failed to download file object: {e}",
                bucket=bucket,
                key=key,
            )
        except BotoCoreError as e:
            raise ObjectStorageError(
                f"Failed to download file object: {e}",
                bucket=bucket,
                key=key,
            )

    def file_exists(self, bucket_type: str, key: str) -> bool:
        """Check if object exists in S3.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key

        Returns:
            True if object exists, False otherwise

        Raises:
            ObjectStorageError: If check fails (not including 404)
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)

        try:
            self.client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                return False
            raise ObjectStorageError(
                f"Failed to check object existence: {e}",
                bucket=bucket,
                key=key,
            )

    def get_file_size(self, bucket_type: str, key: str) -> int:
        """Get file size in bytes.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key

        Returns:
            File size in bytes

        Raises:
            ObjectStorageError: If operation fails
            ObjectNotFoundError: If object doesn't exist
            ValueError: If bucket_type is invalid
        """
        bucket = self._get_bucket(bucket_type)

        try:
            response = self.client.head_object(Bucket=bucket, Key=key)
            return response["ContentLength"]
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise ObjectNotFoundError(
                    f"Object not found: {key}",
                    bucket=bucket,
                    key=key,
                )
            raise ObjectStorageError(
                f"Failed to get file size: {e}",
                bucket=bucket,
                key=key,
            )

    def stream_file(
        self,
        bucket_type: str,
        key: str,
        chunk_size: int = 64 * 1024,  # 64 KB default
    ) -> Iterator[bytes]:
        """Stream file from S3 in chunks (memory-efficient).

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key
            chunk_size: Chunk size in bytes (default 64KB)

        Yields:
            File chunks as bytes

        Raises:
            ObjectStorageError: If streaming fails
            ObjectNotFoundError: If object doesn't exist
            ValueError: If bucket_type is invalid

        Example:
            ```python
            for chunk in client.stream_file("raw", "dataset.csv"):
                process_chunk(chunk)
            ```
        """
        bucket = self._get_bucket(bucket_type)

        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            stream = response["Body"]

            # Stream in chunks
            while True:
                chunk = stream.read(chunk_size)
                if not chunk:
                    break
                yield chunk

            logger.info("file_streamed", bucket=bucket, key=key, chunk_size=chunk_size)

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("NoSuchKey", "404"):
                raise ObjectNotFoundError(
                    f"Object not found: {key}",
                    bucket=bucket,
                    key=key,
                )
            raise ObjectStorageError(
                f"Failed to stream file: {e}",
                bucket=bucket,
                key=key,
            )
        except BotoCoreError as e:
            raise ObjectStorageError(
                f"Failed to stream file: {e}",
                bucket=bucket,
                key=key,
            )

    def delete_file(self, bucket_type: str, key: str) -> None:
        """Delete object from S3.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key

        Raises:
            ObjectStorageError: If deletion fails
            ValueError: If bucket_type is invalid

        Note:
            S3 delete is idempotent - deleting non-existent object succeeds
        """
        bucket = self._get_bucket(bucket_type)

        try:
            self.client.delete_object(Bucket=bucket, Key=key)
            logger.info("file_deleted", bucket=bucket, key=key)
        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to delete file: {e}",
                bucket=bucket,
                key=key,
            )

    # =============================================================================
    # Phase 12: Cost Optimization Features
    # =============================================================================

    def upload_with_compression(
        self,
        bucket_type: str,
        key: str,
        data: bytes,
        content_type: str = "application/gzip",
        metadata: dict[str, str] | None = None,
    ) -> None:
        """Upload data with gzip compression (for PNML, XML, text files).

        Automatically compresses data before upload to reduce storage costs.
        Ideal for PNML files which are XML-based and highly compressible.

        Args:
            bucket_type: Bucket type (raw, models, cache)
            key: Object key (should end with .gz)
            data: Uncompressed data bytes
            content_type: MIME type (default: application/gzip)
            metadata: Optional metadata (compression ratio logged automatically)

        Raises:
            ObjectStorageError: If upload fails
            ValueError: If bucket_type is invalid

        Example:
            ```python
            storage = get_storage_client()
            pnml_data = pnml_exporter.export(model)
            storage.upload_with_compression(
                "models",
                f"{model_id}.pnml.gz",
                pnml_data.encode("utf-8")
            )
            ```
        """
        bucket = self._get_bucket(bucket_type)

        # Compress data
        compressed = io.BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb", compresslevel=9) as gz:
            gz.write(data)
        compressed.seek(0)

        # Calculate compression ratio for metrics
        original_size = len(data)
        compressed_size = len(compressed.getvalue())
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        # Add compression metadata
        meta = metadata or {}
        meta["original-size"] = str(original_size)
        meta["compressed-size"] = str(compressed_size)
        meta["compression-ratio"] = f"{compression_ratio:.1f}%"

        try:
            self.client.upload_fileobj(
                compressed,
                bucket,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "ContentEncoding": "gzip",
                    "Metadata": meta,
                },
            )

            logger.info(
                "compressed_file_uploaded",
                bucket=bucket,
                key=key,
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=f"{compression_ratio:.1f}%",
            )

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to upload compressed file: {e}",
                bucket=bucket,
                key=key,
            )

    def configure_lifecycle_policy(
        self,
        bucket_type: str,
        transition_to_ia_days: int = 30,
        transition_to_glacier_days: int = 90,
        expiration_days: int | None = None,
    ) -> None:
        """Configure S3 lifecycle policy for cost optimization.

        Automatically transitions objects to cheaper storage classes:
        - Standard → Standard-IA (Infrequent Access) after 30 days
        - Standard-IA → Glacier after 90 days
        - Optional: Delete after expiration_days

        Args:
            bucket_type: Bucket type (raw, models, cache)
            transition_to_ia_days: Days until transition to Standard-IA
            transition_to_glacier_days: Days until transition to Glacier
            expiration_days: Days until deletion (None = no auto-delete)

        Raises:
            ObjectStorageError: If policy configuration fails
            ValueError: If bucket_type is invalid

        Example:
            ```python
            # Cache bucket: 30d → IA, 90d → Glacier, 180d → Delete
            storage.configure_lifecycle_policy("cache", 30, 90, 180)

            # Models bucket: 30d → IA, 90d → Glacier, never delete
            storage.configure_lifecycle_policy("models", 30, 90, None)
            ```
        """
        bucket = self._get_bucket(bucket_type)

        rules = [
            {
                "ID": f"{bucket_type}-lifecycle-rule",
                "Status": "Enabled",
                "Filter": {"Prefix": ""},
                "Transitions": [
                    {
                        "Days": transition_to_ia_days,
                        "StorageClass": "STANDARD_IA",
                    },
                    {
                        "Days": transition_to_glacier_days,
                        "StorageClass": "GLACIER",
                    },
                ],
            }
        ]

        # Add expiration if specified
        if expiration_days:
            rules[0]["Expiration"] = {"Days": expiration_days}

        try:
            self.client.put_bucket_lifecycle_configuration(
                Bucket=bucket,
                LifecycleConfiguration={"Rules": rules},
            )

            logger.info(
                "lifecycle_policy_configured",
                bucket=bucket,
                transition_ia_days=transition_to_ia_days,
                transition_glacier_days=transition_to_glacier_days,
                expiration_days=expiration_days,
            )

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to configure lifecycle policy: {e}",
                bucket=bucket,
            )

    def get_bucket_storage_metrics(self, bucket_type: str) -> dict[str, int]:
        """Get storage metrics for cost tracking.

        Returns object count and total size for a bucket.
        Use for per-tenant cost allocation.

        Args:
            bucket_type: Bucket type (raw, models, cache)

        Returns:
            Dict with 'object_count' and 'total_bytes'

        Raises:
            ObjectStorageError: If metrics retrieval fails
            ValueError: If bucket_type is invalid

        Example:
            ```python
            metrics = storage.get_bucket_storage_metrics("raw")
            # {"object_count": 1523, "total_bytes": 5368709120}
            ```
        """
        bucket = self._get_bucket(bucket_type)

        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=bucket)

            total_bytes = 0
            object_count = 0

            for page in pages:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        total_bytes += obj["Size"]
                        object_count += 1

            logger.info(
                "storage_metrics_retrieved",
                bucket=bucket,
                object_count=object_count,
                total_bytes=total_bytes,
            )

            return {
                "object_count": object_count,
                "total_bytes": total_bytes,
            }

        except (BotoCoreError, ClientError) as e:
            raise ObjectStorageError(
                f"Failed to get storage metrics: {e}",
                bucket=bucket,
            )

    def get_workspace_storage_metrics(self, workspace_id: str) -> dict[str, int]:
        """Get storage metrics for a specific workspace (tenant).

        Calculates total storage used by a workspace across all buckets
        by filtering objects with workspace_id prefix.

        Args:
            workspace_id: Workspace UUID

        Returns:
            Dict with 'object_count' and 'total_bytes'

        Raises:
            ObjectStorageError: If metrics retrieval fails

        Example:
            ```python
            metrics = storage.get_workspace_storage_metrics("ws-123")
            # {"object_count": 42, "total_bytes": 1073741824}
            ```
        """
        total_bytes = 0
        object_count = 0

        # Check all bucket types for workspace objects
        for bucket_type in self.buckets:
            bucket = self._get_bucket(bucket_type)

            try:
                paginator = self.client.get_paginator("list_objects_v2")
                pages = paginator.paginate(
                    Bucket=bucket,
                    Prefix=f"{workspace_id}/",
                )

                for page in pages:
                    if "Contents" in page:
                        for obj in page["Contents"]:
                            total_bytes += obj["Size"]
                            object_count += 1

            except (BotoCoreError, ClientError) as e:
                raise ObjectStorageError(
                    f"Failed to get workspace metrics: {e}",
                    bucket=bucket,
                )

        logger.info(
            "workspace_storage_metrics_retrieved",
            workspace_id=workspace_id,
            object_count=object_count,
            total_bytes=total_bytes,
        )

        return {
            "object_count": object_count,
            "total_bytes": total_bytes,
        }

    def _get_bucket(self, bucket_type: str) -> str:
        """Get bucket name by type.

        Args:
            bucket_type: Bucket type (raw, models, cache)

        Returns:
            Full bucket name with environment suffix

        Raises:
            ValueError: If bucket_type is invalid
        """
        if bucket_type not in self.buckets:
            raise ValueError(
                f"Invalid bucket type: {bucket_type}. Allowed: {', '.join(self.buckets.keys())}"
            )
        return self.buckets[bucket_type]


# =============================================================================
# Global Instance (Singleton Pattern)
# =============================================================================

class LocalStorageClient:
    """Local filesystem storage client for development/testing.
    
    Mimics S3 client interface but stores files locally.
    Enabled when storage_type="local" in settings.
    """

    def __init__(self):
        self.settings = settings
        self.base_path = Path("./data/storage")
        
        # Bucket templates -> local directories
        env_suffix = "dev" # Default for local
        self.buckets = {
            "raw": self.base_path / f"pm-raw-{env_suffix}",
            "models": self.base_path / f"pm-models-{env_suffix}",
            "cache": self.base_path / f"pm-cache-{env_suffix}",
        }
        
    def ensure_buckets_exist(self) -> None:
        """Create local directories for buckets."""
        for path in self.buckets.values():
            path.mkdir(parents=True, exist_ok=True)
            logger.info("local_bucket_created", path=str(path))

    def _get_bucket_path(self, bucket_type: str) -> Path:
        if bucket_type not in self.buckets:
            raise ValueError(f"Invalid bucket type: {bucket_type}")
        return self.buckets[bucket_type]

    def _get_object_path(self, bucket_type: str, key: str) -> Path:
        return self._get_bucket_path(bucket_type) / key

    def upload_fileobj(
        self,
        bucket_type: str,
        key: str,
        file_obj: io.BytesIO,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        dest_path = self._get_object_path(bucket_type, key)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dest_path, "wb") as f:
            f.write(file_obj.read())
            
        logger.info("local_file_uploaded", path=str(dest_path))

    def upload_file(
        self,
        bucket_type: str,
        key: str,
        file_path: Path,
        content_type: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> None:
        dest_path = self._get_object_path(bucket_type, key)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(file_path, dest_path)
        logger.info("local_file_copied", src=str(file_path), dest=str(dest_path))

    def download_fileobj(self, bucket_type: str, key: str) -> io.BytesIO:
        src_path = self._get_object_path(bucket_type, key)
        if not src_path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}", bucket=bucket_type, key=key)
            
        with open(src_path, "rb") as f:
            return io.BytesIO(f.read())

    def download_file(self, bucket_type: str, key: str, dest_path: Path) -> None:
        src_path = self._get_object_path(bucket_type, key)
        if not src_path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}", bucket=bucket_type, key=key)
            
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(src_path, dest_path)

    def file_exists(self, bucket_type: str, key: str) -> bool:
        return self._get_object_path(bucket_type, key).exists()

    def get_file_size(self, bucket_type: str, key: str) -> int:
        path = self._get_object_path(bucket_type, key)
        if not path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}", bucket=bucket_type, key=key)
        return path.stat().st_size

    def stream_file(
        self,
        bucket_type: str, 
        key: str,
        chunk_size: int = 64 * 1024,
    ) -> Iterator[bytes]:
        path = self._get_object_path(bucket_type, key)
        if not path.exists():
            raise ObjectNotFoundError(f"Object not found: {key}", bucket=bucket_type, key=key)
            
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                yield chunk

    def delete_file(self, bucket_type: str, key: str) -> None:
        path = self._get_object_path(bucket_type, key)
        if path.exists():
            path.unlink()
            logger.info("local_file_deleted", path=str(path))

    def get_presigned_upload_url(
        self,
        bucket_type: str,
        key: str,
        expires_in: int | None = None,
        content_type: str = "application/octet-stream",
    ) -> str:
        # For local dev, we might need a workaround if frontend relies on this.
        # Returning a fake URL that won't work for real PUTs but satisfies the string return type.
        return f"http://localhost/local-storage/{bucket_type}/{key}"

    def get_presigned_download_url(
        self,
        bucket_type: str,
        key: str,
        expires_in: int | None = None,
        filename: str | None = None,
    ) -> str:
        return f"http://localhost/local-storage/{bucket_type}/{key}"

    def configure_lifecycle_policy(self, *args, **kwargs) -> None:
        pass # No-op for local

    def upload_with_compression(
        self,
        bucket_type: str,
        key: str,
        data: bytes,
        content_type: str = "application/gzip",
        metadata: dict[str, str] | None = None,
    ) -> None:
        # Reuse standard upload for now, or implement compression if needed
        import gzip
        compressed = io.BytesIO()
        with gzip.GzipFile(fileobj=compressed, mode="wb", compresslevel=9) as gz:
            gz.write(data)
        compressed.seek(0)
        self.upload_fileobj(bucket_type, key, compressed, content_type, metadata)
        
    def get_bucket_storage_metrics(self, bucket_type: str) -> dict[str, int]:
        path = self._get_bucket_path(bucket_type)
        total_bytes = 0
        object_count = 0
        if path.exists():
            for p in path.rglob("*"):
                if p.is_file():
                    object_count += 1
                    total_bytes += p.stat().st_size
        return {"object_count": object_count, "total_bytes": total_bytes}

    def get_workspace_storage_metrics(self, workspace_id: str) -> dict[str, int]:
        total_bytes = 0
        object_count = 0
        for bucket_type in self.buckets:
            path = self._get_bucket_path(bucket_type)
            if path.exists():
                # Naive implementation assuming key starts with workspace_id or is inside a folder named workspace_id
                # S3 keys are usually "{workspace_id}/..."
                # Local paths are "bucket/parent/file"
                for p in path.rglob("*"):
                    if p.is_file() and str(p).find(workspace_id) != -1:
                         object_count += 1
                         total_bytes += p.stat().st_size
        return {"object_count": object_count, "total_bytes": total_bytes}


# =============================================================================
# Global Instance (Singleton Pattern)
# =============================================================================

_storage_client: ObjectStorageClient | LocalStorageClient | None = None


def get_storage_client() -> ObjectStorageClient | LocalStorageClient:
    """Get global storage client instance (singleton).

    Returns ObjectStorageClient (S3) or LocalStorageClient based on configuration.
    """
    global _storage_client
    if _storage_client is None:
        logger.info("initializing_storage_client", storage_type=settings.storage_type)
        if settings.storage_type == "local":
            logger.info("using_local_storage_client")
            _storage_client = LocalStorageClient()
            _storage_client.ensure_buckets_exist()
        else:
            logger.info("using_s3_storage_client")
            _storage_client = ObjectStorageClient()
            _storage_client.ensure_buckets_exist()
    return _storage_client
