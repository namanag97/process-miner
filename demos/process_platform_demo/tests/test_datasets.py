"""
Tests for Dataset Loader Module
"""
import pytest
import pandas as pd


class TestDatasetLoader:
    """Tests for DatasetLoader class."""
    
    def test_list_datasets(self):
        """Test listing available datasets."""
        from utils.datasets import DatasetLoader
        
        datasets = DatasetLoader.list_datasets()
        
        assert len(datasets) > 0
        assert "order_to_cash" in datasets
        assert "procure_to_pay" in datasets
        assert "incident_management" in datasets
    
    def test_load_order_to_cash(self):
        """Test loading O2C dataset."""
        from utils.datasets import DatasetLoader
        
        df = DatasetLoader.load_dataset("order_to_cash", n_cases=50)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "case_id" in df.columns
        assert "activity" in df.columns
        assert "timestamp" in df.columns
    
    def test_load_procure_to_pay(self):
        """Test loading P2P dataset."""
        from utils.datasets import DatasetLoader
        
        df = DatasetLoader.load_dataset("procure_to_pay", n_cases=50)
        
        assert isinstance(df, pd.DataFrame)
        assert df["case_id"].nunique() <= 50
    
    def test_load_incident_management(self):
        """Test loading ITSM dataset."""
        from utils.datasets import DatasetLoader
        
        df = DatasetLoader.load_dataset("incident_management", n_cases=30)
        
        assert isinstance(df, pd.DataFrame)
        assert "Incident Reported" in df["activity"].values
    
    def test_load_patient_treatment(self):
        """Test loading healthcare dataset."""
        from utils.datasets import DatasetLoader
        
        df = DatasetLoader.load_dataset("patient_treatment", n_cases=30)
        
        assert isinstance(df, pd.DataFrame)
        assert "Patient Registration" in df["activity"].values
    
    def test_load_loan_application(self):
        """Test loading loan application dataset."""
        from utils.datasets import DatasetLoader
        
        df = DatasetLoader.load_dataset("loan_application", n_cases=30)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
    
    def test_invalid_dataset_raises_error(self):
        """Test loading invalid dataset raises error."""
        from utils.datasets import DatasetLoader
        
        with pytest.raises(ValueError):
            DatasetLoader.load_dataset("nonexistent_dataset")
    
    def test_dataset_has_required_columns(self):
        """Test all datasets have required columns."""
        from utils.datasets import DatasetLoader
        
        required_cols = ["case_id", "activity", "timestamp"]
        
        for dataset_name in ["order_to_cash", "procure_to_pay", "incident_management"]:
            df = DatasetLoader.load_dataset(dataset_name, n_cases=20)
            for col in required_cols:
                assert col in df.columns, f"{dataset_name} missing {col}"
    
    def test_reproducible_with_seed(self):
        """Test datasets are reproducible with same seed."""
        from utils.datasets import DatasetLoader
        
        df1 = DatasetLoader.load_dataset("order_to_cash", n_cases=20, seed=42)
        df2 = DatasetLoader.load_dataset("order_to_cash", n_cases=20, seed=42)
        
        # Should be identical
        pd.testing.assert_frame_equal(df1, df2)


class TestGetDatasetStatistics:
    """Tests for get_dataset_statistics function."""
    
    def test_statistics_structure(self, sample_event_log):
        """Test statistics have expected structure."""
        from utils.datasets import get_dataset_statistics
        
        stats = get_dataset_statistics(sample_event_log)
        
        assert "total_cases" in stats
        assert "total_events" in stats
        assert "total_activities" in stats
        assert "avg_case_length" in stats
        assert "avg_duration_hours" in stats
    
    def test_statistics_values(self, sample_event_log):
        """Test statistics values are reasonable."""
        from utils.datasets import get_dataset_statistics
        
        stats = get_dataset_statistics(sample_event_log)
        
        assert stats["total_cases"] > 0
        assert stats["total_events"] > 0
        assert stats["avg_case_length"] > 0
