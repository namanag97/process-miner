"""Tests for Object Storage Client (S3/MinIO).

Covers all ObjectStorageClient methods with mocked boto3 calls using moto.
"""

import gzip
import io
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from src.core.exceptions import ProcessingError
from src.infrastructure.object_storage import (
    ObjectNotFoundError,
    ObjectStorageClient,
    ObjectStorageError,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_settings():
    """Mock settings for ObjectStorageClient."""
    with patch("src.infrastructure.object_storage.settings") as settings:
        settings.s3_endpoint_url = "http://localhost:9000"
        settings.s3_access_key_id = "minioadmin"
        settings.s3_secret_access_key = "minioadmin"
        settings.s3_region = "us-east-1"
        settings.s3_bucket_raw = "pm-raw-dev"
        settings.s3_bucket_models = "pm-models-dev"
        settings.s3_bucket_cache = "pm-cache-dev"
        settings.s3_presigned_url_expiry = 3600
        yield settings


@pytest.fixture
def storage_client(mock_settings):
    """Create ObjectStorageClient with mocked S3."""
    with mock_aws():
        client = ObjectStorageClient()
        client.ensure_buckets_exist()
        yield client


@pytest.fixture
def sample_file_content():
    """Sample file content for testing."""
    return b"Test file content for object storage testing. " * 100


# =============================================================================
# Initialization Tests
# =============================================================================


@mock_aws
def test_client_initialization(mock_settings):
    """Test ObjectStorageClient initializes with correct configuration."""
    client = ObjectStorageClient()

    assert client.settings == mock_settings
    assert client.buckets["raw"] == "pm-raw-dev"
    assert client.buckets["models"] == "pm-models-dev"
    assert client.buckets["cache"] == "pm-cache-dev"
    assert client.client is not None


@mock_aws
def test_client_bucket_naming_production(mock_settings):
    """Test bucket names adapt to production environment."""
    mock_settings.s3_bucket_raw = "pm-raw-prod"
    client = ObjectStorageClient()

    assert client.buckets["raw"] == "pm-raw-prod"
    assert client.buckets["models"] == "pm-models-prod"
    assert client.buckets["cache"] == "pm-cache-prod"


# =============================================================================
# Bucket Management Tests
# =============================================================================


@mock_aws
def test_ensure_buckets_exist_creates_buckets(mock_settings):
    """Test ensure_buckets_exist creates missing buckets."""
    client = ObjectStorageClient()
    client.ensure_buckets_exist()

    # Verify all buckets exist
    for bucket_name in client.buckets.values():
        response = client.client.head_bucket(Bucket=bucket_name)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_ensure_buckets_exist_idempotent(mock_settings):
    """Test ensure_buckets_exist is safe to call multiple times."""
    client = ObjectStorageClient()
    client.ensure_buckets_exist()
    client.ensure_buckets_exist()  # Should not raise error

    # All buckets should still exist
    for bucket_name in client.buckets.values():
        response = client.client.head_bucket(Bucket=bucket_name)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock_aws
def test_ensure_buckets_exist_non_us_east_1(mock_settings):
    """Test bucket creation with LocationConstraint for non-us-east-1 regions."""
    mock_settings.s3_region = "eu-west-1"
    client = ObjectStorageClient()
    client.ensure_buckets_exist()

    # Bucket should be created successfully
    response = client.client.head_bucket(Bucket=client.buckets["raw"])
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


# =============================================================================
# Presigned URL Tests
# =============================================================================


def test_get_presigned_upload_url(storage_client):
    """Test presigned upload URL generation."""
    key = "test-uploads/file.csv"
    url = storage_client.get_presigned_upload_url("raw", key, content_type="text/csv")

    assert url.startswith("http")
    assert "pm-raw-dev" in url
    assert key in url
    assert "X-Amz-Signature" in url


def test_get_presigned_upload_url_custom_expiry(storage_client):
    """Test presigned URL with custom expiration."""
    key = "test-uploads/file.csv"
    url = storage_client.get_presigned_upload_url("raw", key, expires_in=1800)

    # Should generate valid URL
    assert url.startswith("http")
    assert "X-Amz-Signature" in url


def test_get_presigned_download_url(storage_client, sample_file_content):
    """Test presigned download URL generation."""
    # First upload a file
    key = "test-files/download-test.txt"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=sample_file_content,
    )

    # Generate download URL
    url = storage_client.get_presigned_download_url("raw", key)

    assert url.startswith("http")
    assert "pm-raw-dev" in url
    assert key in url


def test_get_presigned_download_url_custom_filename(storage_client, sample_file_content):
    """Test presigned download URL with custom filename."""
    key = "test-files/download-test.txt"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=sample_file_content,
    )

    url = storage_client.get_presigned_download_url(
        "raw",
        key,
        filename="custom-filename.txt"
    )

    assert "custom-filename.txt" in url
    assert "response-content-disposition" in url


# =============================================================================
# File Upload Tests
# =============================================================================


def test_upload_file(storage_client, sample_file_content, tmp_path):
    """Test file upload from filesystem path."""
    # Create temporary file
    test_file = tmp_path / "test-upload.txt"
    test_file.write_bytes(sample_file_content)

    # Upload file
    key = "test-uploads/uploaded-file.txt"
    storage_client.upload_file("raw", test_file, key)

    # Verify file exists in S3
    response = storage_client.client.get_object(
        Bucket=storage_client.buckets["raw"],
        Key=key
    )
    assert response["Body"].read() == sample_file_content


def test_upload_file_with_content_type(storage_client, tmp_path):
    """Test file upload with custom content type."""
    test_file = tmp_path / "test.csv"
    test_file.write_text("col1,col2\nval1,val2")

    key = "test-uploads/data.csv"
    storage_client.upload_file("raw", test_file, key, content_type="text/csv")

    # Verify content type
    response = storage_client.client.head_object(
        Bucket=storage_client.buckets["raw"],
        Key=key
    )
    assert response["ContentType"] == "text/csv"


def test_upload_fileobj(storage_client, sample_file_content):
    """Test file upload from file-like object."""
    file_obj = io.BytesIO(sample_file_content)
    key = "test-uploads/fileobj-upload.bin"

    storage_client.upload_fileobj("raw", file_obj, key)

    # Verify content
    response = storage_client.client.get_object(
        Bucket=storage_client.buckets["raw"],
        Key=key
    )
    assert response["Body"].read() == sample_file_content


def test_upload_fileobj_with_metadata(storage_client):
    """Test file upload with custom metadata."""
    file_obj = io.BytesIO(b"test content")
    key = "test-uploads/with-metadata.bin"
    metadata = {"user-id": "123", "dataset-name": "test-dataset"}

    storage_client.upload_fileobj("raw", file_obj, key, metadata=metadata)

    # Verify metadata
    response = storage_client.client.head_object(
        Bucket=storage_client.buckets["raw"],
        Key=key
    )
    assert response["Metadata"]["user-id"] == "123"
    assert response["Metadata"]["dataset-name"] == "test-dataset"


# =============================================================================
# File Download Tests
# =============================================================================


def test_download_file(storage_client, sample_file_content, tmp_path):
    """Test file download to filesystem path."""
    # Upload file first
    key = "test-files/to-download.txt"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=sample_file_content,
    )

    # Download file
    dest_path = tmp_path / "downloaded-file.txt"
    storage_client.download_file("raw", key, dest_path)

    # Verify content
    assert dest_path.read_bytes() == sample_file_content


def test_download_file_not_found(storage_client, tmp_path):
    """Test download of non-existent file raises ObjectNotFoundError."""
    dest_path = tmp_path / "nonexistent.txt"

    with pytest.raises(ObjectNotFoundError) as exc_info:
        storage_client.download_file("raw", "nonexistent-key", dest_path)

    assert "nonexistent-key" in str(exc_info.value)


def test_download_fileobj(storage_client, sample_file_content):
    """Test file download to file-like object."""
    # Upload file first
    key = "test-files/to-download-obj.bin"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=sample_file_content,
    )

    # Download to BytesIO
    file_obj = storage_client.download_fileobj("raw", key)

    assert file_obj.getvalue() == sample_file_content


# =============================================================================
# File Existence and Size Tests
# =============================================================================


def test_file_exists_true(storage_client):
    """Test file_exists returns True for existing file."""
    key = "test-files/exists.txt"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=b"test content",
    )

    assert storage_client.file_exists("raw", key) is True


def test_file_exists_false(storage_client):
    """Test file_exists returns False for non-existent file."""
    assert storage_client.file_exists("raw", "nonexistent-key") is False


def test_get_file_size(storage_client):
    """Test get_file_size returns correct size."""
    key = "test-files/sized-file.bin"
    content = b"X" * 1024  # 1KB
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=content,
    )

    size = storage_client.get_file_size("raw", key)
    assert size == 1024


def test_get_file_size_not_found(storage_client):
    """Test get_file_size raises ObjectNotFoundError for missing file."""
    with pytest.raises(ObjectNotFoundError):
        storage_client.get_file_size("raw", "nonexistent-key")


# =============================================================================
# Streaming Tests
# =============================================================================


def test_stream_file(storage_client):
    """Test file streaming with chunked reading."""
    key = "test-files/stream-test.bin"
    content = b"Chunk1|Chunk2|Chunk3|Chunk4"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=content,
    )

    # Stream file
    chunks = list(storage_client.stream_file("raw", key, chunk_size=7))

    assert len(chunks) == 4
    assert b"".join(chunks) == content


def test_stream_file_empty(storage_client):
    """Test streaming empty file."""
    key = "test-files/empty.bin"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=b"",
    )

    chunks = list(storage_client.stream_file("raw", key))
    assert chunks == []


def test_stream_file_not_found(storage_client):
    """Test streaming non-existent file raises ObjectNotFoundError."""
    with pytest.raises(ObjectNotFoundError):
        list(storage_client.stream_file("raw", "nonexistent-key"))


# =============================================================================
# File Deletion Tests
# =============================================================================


def test_delete_file(storage_client):
    """Test file deletion."""
    key = "test-files/to-delete.txt"
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=b"delete me",
    )

    # Verify file exists
    assert storage_client.file_exists("raw", key) is True

    # Delete file
    storage_client.delete_file("raw", key)

    # Verify file is gone
    assert storage_client.file_exists("raw", key) is False


def test_delete_file_nonexistent(storage_client):
    """Test deleting non-existent file (should be idempotent)."""
    # Should not raise error
    storage_client.delete_file("raw", "nonexistent-key")


# =============================================================================
# Compression Tests
# =============================================================================


def test_upload_with_compression(storage_client):
    """Test upload with automatic gzip compression."""
    content = b"<?xml version='1.0'?><pnml>test content</pnml>" * 100
    key = "test-models/compressed-model.pnml"

    storage_client.upload_with_compression("models", io.BytesIO(content), key)

    # Download and verify decompression
    response = storage_client.client.get_object(
        Bucket=storage_client.buckets["models"],
        Key=key
    )

    # Content should be gzip compressed
    compressed_data = response["Body"].read()
    decompressed = gzip.decompress(compressed_data)
    assert decompressed == content

    # Verify content encoding
    assert response.get("ContentEncoding") == "gzip"


def test_upload_with_compression_metadata(storage_client):
    """Test compression includes original size in metadata."""
    content = b"<pnml>test</pnml>" * 50
    key = "test-models/metadata-test.pnml"

    storage_client.upload_with_compression("models", io.BytesIO(content), key)

    # Check metadata
    response = storage_client.client.head_object(
        Bucket=storage_client.buckets["models"],
        Key=key
    )

    assert "original-size" in response["Metadata"]
    assert int(response["Metadata"]["original-size"]) == len(content)


# =============================================================================
# Lifecycle Policy Tests
# =============================================================================


def test_configure_lifecycle_policy(storage_client):
    """Test S3 lifecycle policy configuration."""
    # Note: moto doesn't fully support lifecycle policies, so we test the call doesn't error
    storage_client.configure_lifecycle_policy(
        "cache",
        transition_days=30,
        expiration_days=90
    )

    # Verify policy was set (moto limitation: can't fully verify policy content)
    # In real S3, we would check: client.get_bucket_lifecycle_configuration()


# =============================================================================
# Storage Metrics Tests
# =============================================================================


def test_get_bucket_storage_metrics(storage_client):
    """Test bucket storage metrics calculation."""
    # Upload several files
    files = [
        ("file1.txt", b"a" * 1000),
        ("file2.txt", b"b" * 2000),
        ("file3.txt", b"c" * 3000),
    ]

    for key, content in files:
        storage_client.client.put_object(
            Bucket=storage_client.buckets["raw"],
            Key=key,
            Body=content,
        )

    metrics = storage_client.get_bucket_storage_metrics("raw")

    assert metrics["total_objects"] == 3
    assert metrics["total_size_bytes"] == 6000  # 1000 + 2000 + 3000
    assert metrics["total_size_mb"] == pytest.approx(0.0057, abs=0.001)


def test_get_workspace_storage_metrics(storage_client):
    """Test workspace-specific storage metrics."""
    workspace_id = "ws-123"

    # Upload files with workspace prefix
    files = [
        (f"workspaces/{workspace_id}/file1.csv", b"x" * 500),
        (f"workspaces/{workspace_id}/file2.csv", b"y" * 1500),
        (f"workspaces/other-ws/file3.csv", b"z" * 1000),  # Different workspace
    ]

    for key, content in files:
        storage_client.client.put_object(
            Bucket=storage_client.buckets["raw"],
            Key=key,
            Body=content,
        )

    metrics = storage_client.get_workspace_storage_metrics(workspace_id)

    # Should only count files for this workspace
    assert metrics["total_objects"] == 2
    assert metrics["total_size_bytes"] == 2000  # 500 + 1500


def test_get_bucket_storage_metrics_empty_bucket(storage_client):
    """Test metrics for empty bucket."""
    metrics = storage_client.get_bucket_storage_metrics("raw")

    assert metrics["total_objects"] == 0
    assert metrics["total_size_bytes"] == 0
    assert metrics["total_size_mb"] == 0.0


# =============================================================================
# Error Handling Tests
# =============================================================================


def test_get_bucket_invalid_type(storage_client):
    """Test _get_bucket raises ValueError for invalid bucket type."""
    with pytest.raises(ValueError) as exc_info:
        storage_client._get_bucket("invalid-bucket-type")

    assert "Invalid bucket type" in str(exc_info.value)


def test_upload_file_invalid_bucket(storage_client, tmp_path):
    """Test upload with invalid bucket type raises ValueError."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    with pytest.raises(ValueError):
        storage_client.upload_file("invalid-type", test_file, "key")


def test_presigned_url_invalid_bucket(storage_client):
    """Test presigned URL generation with invalid bucket type."""
    with pytest.raises(ValueError):
        storage_client.get_presigned_upload_url("invalid-type", "key")


@mock_aws
def test_ensure_buckets_exist_handles_errors(mock_settings):
    """Test ensure_buckets_exist handles bucket creation errors gracefully."""
    client = ObjectStorageClient()

    # Mock a failure scenario by creating a bucket with an invalid configuration
    # In practice, this tests the error handling path
    with patch.object(client.client, "create_bucket") as mock_create:
        mock_create.side_effect = ClientError(
            {"Error": {"Code": "BucketAlreadyExists", "Message": "Bucket exists"}},
            "create_bucket"
        )

        # Should raise ObjectStorageError
        with pytest.raises(ObjectStorageError):
            client.ensure_buckets_exist()


# =============================================================================
# Edge Cases
# =============================================================================


def test_upload_large_file_simulation(storage_client, tmp_path):
    """Test upload of large file (simulated with smaller file)."""
    # Create a 10MB simulated file
    large_content = b"X" * (10 * 1024 * 1024)
    test_file = tmp_path / "large-file.bin"
    test_file.write_bytes(large_content)

    key = "test-uploads/large-file.bin"
    storage_client.upload_file("raw", test_file, key)

    # Verify size
    size = storage_client.get_file_size("raw", key)
    assert size == len(large_content)


def test_stream_file_large_chunks(storage_client):
    """Test streaming with large chunk size."""
    key = "test-files/stream-large.bin"
    content = b"DATA" * 10000  # 40KB
    storage_client.client.put_object(
        Bucket=storage_client.buckets["raw"],
        Key=key,
        Body=content,
    )

    # Stream with 32KB chunks
    chunks = list(storage_client.stream_file("raw", key, chunk_size=32 * 1024))

    assert b"".join(chunks) == content
    # Should be 2 chunks (32KB + 8KB)
    assert len(chunks) == 2


def test_special_characters_in_key(storage_client):
    """Test handling of special characters in object keys."""
    key = "test-files/file with spaces & special#chars.txt"
    content = b"test content"

    storage_client.upload_fileobj("raw", io.BytesIO(content), key)

    # Should be able to retrieve it
    assert storage_client.file_exists("raw", key) is True
    downloaded = storage_client.download_fileobj("raw", key)
    assert downloaded.getvalue() == content


def test_nested_path_in_key(storage_client):
    """Test deeply nested paths in object keys."""
    key = "level1/level2/level3/level4/file.txt"
    content = b"nested file"

    storage_client.upload_fileobj("raw", io.BytesIO(content), key)

    assert storage_client.file_exists("raw", key) is True
    size = storage_client.get_file_size("raw", key)
    assert size == len(content)
