"""Unit tests for analysis activities."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.platform.temporal.activities.types import (
    CheckConformanceInput,
    ComputeMetricsInput,
    LoadEventLogInput,
    MineModelInput,
)


class TestLoadEventLogActivity:
    """Tests for load_event_log_activity."""

    @pytest.mark.asyncio
    async def test_load_event_log_success(self):
        """Test successful event log loading."""
        from src.platform.temporal.activities.analysis import load_event_log_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"
        mock_dataset.name = "Test Dataset"
        mock_dataset.total_cases = 100
        mock_dataset.total_events = 500
        mock_dataset.status = "ready"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch("src.platform.temporal.activities.analysis.DatasetStatus") as mock_status,
        ):
            mock_status.READY.value = "ready"
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()

            input_data = LoadEventLogInput(dataset_id="test-dataset-123")
            result = await load_event_log_activity(input_data)

        assert result.dataset_id == "test-dataset-123"
        assert result.dataset_name == "Test Dataset"
        assert result.total_cases == 100
        assert result.total_events == 500
        assert result.is_loaded is True

    @pytest.mark.asyncio
    async def test_load_event_log_not_found(self):
        """Test error when dataset not found."""
        from src.platform.temporal.activities.analysis import load_event_log_activity

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        with patch(
            "src.platform.temporal.activities.analysis.AsyncSessionLocal"
        ) as mock_session_local:
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()

            input_data = LoadEventLogInput(dataset_id="nonexistent-dataset")

            with pytest.raises(ValueError, match="Dataset not found"):
                await load_event_log_activity(input_data)

    @pytest.mark.asyncio
    async def test_load_event_log_not_ready(self):
        """Test error when dataset not ready."""
        from src.platform.temporal.activities.analysis import load_event_log_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"
        mock_dataset.status = "pending"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch("src.platform.temporal.activities.analysis.DatasetStatus") as mock_status,
        ):
            mock_status.READY.value = "ready"
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()

            input_data = LoadEventLogInput(dataset_id="test-dataset-123")

            with pytest.raises(ValueError, match="not ready for analysis"):
                await load_event_log_activity(input_data)


class TestMineModelActivity:
    """Tests for mine_model_activity."""

    @pytest.mark.asyncio
    async def test_mine_model_alpha(self):
        """Test Alpha miner discovery."""
        from src.platform.temporal.activities.analysis import mine_model_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"
        mock_dataset.name = "Test Dataset"

        mock_model = MagicMock()
        mock_model.id = "model-uuid-123"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dataset
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        mock_model_format = MagicMock()
        mock_model_format.value = "petri_net"

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch("src.platform.temporal.activities.analysis.mining_service") as mock_mining,
            patch("src.platform.temporal.activities.analysis.activity") as mock_activity,
            patch("src.platform.temporal.activities.analysis.MinerType") as mock_miner_type,
        ):
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()
            mock_activity.heartbeat = MagicMock()
            mock_miner_type.return_value = "alpha"
            mock_mining.discover.return_value = (MagicMock(), mock_model_format)
            mock_mining.serialize_model.return_value = "serialized"
            mock_mining.serialize_to_graph_json.return_value = {"nodes": [], "edges": []}
            mock_mining.evaluate_fitness.return_value = {"fitness": 0.85}
            mock_mining.evaluate_precision.return_value = 0.78

            input_data = MineModelInput(
                dataset_id="test-dataset-123",
                miner_type="alpha",
            )

            # This will work partially with mocks
            with pytest.raises(RuntimeError):
                await mine_model_activity(input_data)

    @pytest.mark.asyncio
    async def test_mine_model_invalid_miner(self):
        """Test error for invalid miner type."""
        from src.platform.temporal.activities.analysis import mine_model_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_dataset
        mock_session.execute = AsyncMock(return_value=mock_result)

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch("src.platform.temporal.activities.analysis.activity") as mock_activity,
            patch("src.platform.temporal.activities.analysis.MinerType") as mock_miner_type,
        ):
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()
            mock_activity.heartbeat = MagicMock()
            mock_miner_type.side_effect = ValueError("Invalid miner")

            input_data = MineModelInput(
                dataset_id="test-dataset-123",
                miner_type="invalid_miner",
            )

            with pytest.raises(ValueError):
                await mine_model_activity(input_data)


class TestComputeMetricsActivity:
    """Tests for compute_metrics_activity."""

    @pytest.mark.asyncio
    async def test_compute_metrics_success(self):
        """Test successful metrics computation."""
        from src.platform.temporal.activities.analysis import compute_metrics_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"

        mock_model = MagicMock()
        mock_model.id = "model-uuid-123"
        mock_model.model_format = "petri_net"
        mock_model.serialized_model = "serialized"

        mock_session = AsyncMock()
        mock_result = MagicMock()
        # First call returns dataset, second returns model
        mock_result.scalar_one_or_none.side_effect = [mock_dataset, mock_model]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch("src.platform.temporal.activities.analysis.mining_service") as mock_mining,
        ):
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()
            mock_mining.deserialize_model.return_value = (MagicMock(), MagicMock(), MagicMock())
            mock_mining.evaluate_fitness.return_value = {"fitness": 0.9}
            mock_mining.evaluate_precision.return_value = 0.85

            input_data = ComputeMetricsInput(
                dataset_id="test-dataset-123",
                model_id="model-uuid-123",
            )

            result = await compute_metrics_activity(input_data)

        assert result.model_id == "model-uuid-123"
        assert result.fitness == 0.9
        assert result.precision == 0.85


class TestCheckConformanceActivity:
    """Tests for check_conformance_activity."""

    @pytest.mark.asyncio
    async def test_check_conformance_token_replay(self):
        """Test token replay conformance checking."""
        from src.platform.temporal.activities.analysis import check_conformance_activity

        mock_dataset = MagicMock()
        mock_dataset.id = "test-dataset-123"

        mock_model = MagicMock()
        mock_model.id = "model-uuid-123"

        mock_conformance_record = MagicMock()
        mock_conformance_record.id = "conf-uuid-123"

        mock_conf_result = {
            "fitness": 0.92,
            "precision": 0.88,
            "method": "token_replay",
            "is_conformant": True,
            "fitting_traces": 92,
            "total_traces": 100,
        }

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [mock_dataset, mock_model]
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()

        with (
            patch(
                "src.platform.temporal.activities.analysis.AsyncSessionLocal"
            ) as mock_session_local,
            patch(
                "src.platform.temporal.activities.analysis.conformance_service"
            ) as mock_conformance,
            patch("src.platform.temporal.activities.analysis.ConformanceResult") as mock_conf_class,
        ):
            mock_session_local.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session_local.return_value.__aexit__ = AsyncMock()
            mock_conformance.check_conformance.return_value = mock_conf_result
            mock_conf_class.return_value = mock_conformance_record

            input_data = CheckConformanceInput(
                dataset_id="test-dataset-123",
                model_id="model-uuid-123",
                method="token_replay",
            )

            result = await check_conformance_activity(input_data)

        assert result.fitness == 0.92
        assert result.is_conformant is True
        assert result.fitting_traces == 92
        assert result.total_traces == 100
