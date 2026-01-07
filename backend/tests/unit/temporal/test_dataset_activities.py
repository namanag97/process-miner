"""Unit tests for dataset activities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infra.temporal.activities.types import (
    ComputeStatsInput,
    DetectColumnsInput,
    ParseToParquetInput,
    ValidateFileInput,
)


class TestValidateFileActivity:
    """Tests for validate_file_activity."""

    @pytest.mark.asyncio
    async def test_validate_csv_valid(self):
        """Test validation of valid CSV file."""
        from src.infra.temporal.activities.dataset import validate_file_activity

        mock_storage = MagicMock()
        mock_storage.stream_file.return_value = iter(
            [b"case_id,activity,timestamp\n1,A,2024-01-01"]
        )
        mock_storage.get_file_size.return_value = 1000

        with patch(
            "src.infra.temporal.activities.dataset.get_storage_client",
            return_value=mock_storage,
        ):
            input_data = ValidateFileInput(
                dataset_id="test-dataset-123",
                storage_key="datasets/test.csv",
            )
            result = await validate_file_activity(input_data)

        assert result.is_valid is True
        assert result.file_format == "csv"
        assert result.file_size_bytes == 1000
        assert result.error_message is None

    @pytest.mark.asyncio
    async def test_validate_xes_valid(self):
        """Test validation of valid XES file."""
        from src.infra.temporal.activities.dataset import validate_file_activity

        mock_storage = MagicMock()
        mock_storage.stream_file.return_value = iter([b"<?xml version='1.0'?><log />"])
        mock_storage.get_file_size.return_value = 2000

        with patch(
            "src.infra.temporal.activities.dataset.get_storage_client",
            return_value=mock_storage,
        ):
            input_data = ValidateFileInput(
                dataset_id="test-dataset-123",
                storage_key="datasets/test.xes",
            )
            result = await validate_file_activity(input_data)

        assert result.is_valid is True
        assert result.file_format == "xes"

    @pytest.mark.asyncio
    async def test_validate_csv_binary_invalid(self):
        """Test validation rejects binary data as CSV."""
        from src.infra.temporal.activities.dataset import validate_file_activity

        mock_storage = MagicMock()
        # Binary content that can't be decoded as UTF-8
        mock_storage.stream_file.return_value = iter([bytes([0x80, 0x81, 0x82, 0x83] * 256)])
        mock_storage.get_file_size.return_value = 1024

        with patch(
            "src.infra.temporal.activities.dataset.get_storage_client",
            return_value=mock_storage,
        ):
            input_data = ValidateFileInput(
                dataset_id="test-dataset-123",
                storage_key="datasets/test.csv",
            )
            result = await validate_file_activity(input_data)

        assert result.is_valid is False
        assert "binary data" in result.error_message.lower()

    @pytest.mark.asyncio
    async def test_validate_xes_invalid_signature(self):
        """Test validation rejects non-XML as XES."""
        from src.infra.temporal.activities.dataset import validate_file_activity

        mock_storage = MagicMock()
        mock_storage.stream_file.return_value = iter([b"not xml content"])
        mock_storage.get_file_size.return_value = 100

        with patch(
            "src.infra.temporal.activities.dataset.get_storage_client",
            return_value=mock_storage,
        ):
            input_data = ValidateFileInput(
                dataset_id="test-dataset-123",
                storage_key="datasets/test.xes",
            )
            result = await validate_file_activity(input_data)

        assert result.is_valid is False
        assert "XES" in result.error_message


class TestDetectColumnsActivity:
    """Tests for detect_columns_activity."""

    @pytest.mark.asyncio
    async def test_detect_columns_success(self):
        """Test successful column detection."""
        from src.infra.temporal.activities.dataset import detect_columns_activity

        mock_detection_result = {
            "columns": [
                {"name": "case_id", "dtype": "STRING"},
                {"name": "activity", "dtype": "STRING"},
                {"name": "timestamp", "dtype": "TIMESTAMP"},
            ],
            "suggestions": {
                "case_id": {"column": "case_id", "confidence": 0.95},
                "activity": {"column": "activity", "confidence": 0.92},
                "timestamp": {"column": "timestamp", "confidence": 0.98},
            },
            "row_count": 1000,
        }

        with patch(
            "src.infra.temporal.activities.dataset.unified_ingestion_service"
        ) as mock_service:
            mock_service.detect_columns.return_value = mock_detection_result

            input_data = DetectColumnsInput(
                dataset_id="test-dataset-123",
                file_content=b"case_id,activity,timestamp\n1,A,2024-01-01",
                filename="test.csv",
            )
            result = await detect_columns_activity(input_data)

        assert len(result.columns) == 3
        assert result.row_count == 1000
        assert result.can_auto_map is True

    @pytest.mark.asyncio
    async def test_detect_columns_low_confidence(self):
        """Test column detection with low confidence disables auto-map."""
        from src.infra.temporal.activities.dataset import detect_columns_activity

        mock_detection_result = {
            "columns": [{"name": "col1", "dtype": "STRING"}],
            "suggestions": {
                "case_id": {"column": "col1", "confidence": 0.5},  # Low confidence
            },
            "row_count": 100,
        }

        with patch(
            "src.infra.temporal.activities.dataset.unified_ingestion_service"
        ) as mock_service:
            mock_service.detect_columns.return_value = mock_detection_result

            input_data = DetectColumnsInput(
                dataset_id="test-dataset-123",
                file_content=b"col1\n1",
                filename="test.csv",
            )
            result = await detect_columns_activity(input_data)

        assert result.can_auto_map is False


class TestParseToParquetActivity:
    """Tests for parse_to_parquet_activity."""

    @pytest.mark.asyncio
    async def test_parse_success(self):
        """Test successful CSV parsing."""
        import pyarrow as pa

        from src.infra.temporal.activities.dataset import parse_to_parquet_activity

        # Create mock Arrow tables
        cases_table = pa.table(
            {
                "case_id": ["1", "2"],
                "variant": ["A->B", "A->C"],
                "start_time": [None, None],
                "end_time": [None, None],
            }
        )
        events_table = pa.table(
            {
                "case_id": ["1", "1", "2"],
                "activity": ["A", "B", "A"],
                "timestamp": [None, None, None],
            }
        )

        mock_duck_result = {
            "statistics": {
                "total_cases": 2,
                "total_events": 3,
                "total_activities": 2,
            },
            "cases_arrow": cases_table,
            "events_arrow": events_table,
        }

        mock_storage = MagicMock()
        mock_file_obj = MagicMock()
        mock_file_obj.read.return_value = b"case_id,activity,timestamp\n1,A,2024-01-01"
        mock_storage.download_fileobj.return_value = mock_file_obj

        with (
            patch(
                "src.infra.temporal.activities.dataset.get_storage_client",
                return_value=mock_storage,
            ),
            patch(
                "src.infra.temporal.activities.dataset.duckdb_ingestion_service"
            ) as mock_duckdb,
            patch("src.infra.temporal.activities.dataset.activity") as mock_activity,
        ):
            mock_duckdb.parse_csv_fast.return_value = mock_duck_result
            mock_activity.heartbeat = MagicMock()

            input_data = ParseToParquetInput(
                dataset_id="test-dataset-123",
                storage_key="datasets/test.csv",
                case_id_column="case_id",
                activity_column="activity",
                timestamp_column="timestamp",
            )
            result = await parse_to_parquet_activity(input_data)

        assert result.total_cases == 2
        assert result.total_events == 3
        assert len(result.cases_data) == 2
        assert len(result.events_data) == 3


class TestComputeStatisticsActivity:
    """Tests for compute_statistics_activity."""

    @pytest.mark.asyncio
    async def test_compute_stats_success(self):
        """Test successful statistics computation."""
        from src.infra.temporal.activities.dataset import compute_statistics_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dataset
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        with patch(
            "src.infra.temporal.activities.dataset.AsyncSessionLocal"
        ) as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()

            input_data = ComputeStatsInput(
                dataset_id="test-dataset-123",
                statistics={
                    "total_cases": 100,
                    "total_events": 500,
                    "total_activities": 10,
                    "total_variants": 25,
                },
            )

            result = await compute_statistics_activity(input_data)

        assert result.total_cases == 100
        assert result.total_events == 500
        assert result.total_activities == 10
        assert result.total_variants == 25
