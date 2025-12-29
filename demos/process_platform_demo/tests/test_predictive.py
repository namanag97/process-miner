"""
Tests for Predictive Analytics Module
"""
import pytest
import pandas as pd
import numpy as np


class TestProcessPredictor:
    """Tests for ProcessPredictor class."""
    
    def test_predictor_initialization(self):
        """Test predictor initializes correctly."""
        from demos.predictive import ProcessPredictor
        
        predictor = ProcessPredictor()
        
        assert predictor.outcome_model is None
        assert predictor.next_activity_model is None
        assert predictor.time_model is None
        assert predictor.label_encoders == {}
    
    def test_prepare_features(self, sample_event_log):
        """Test feature preparation from event log."""
        from demos.predictive import ProcessPredictor
        
        predictor = ProcessPredictor()
        features_df = predictor.prepare_features(sample_event_log)
        
        assert len(features_df) > 0
        assert "prefix_length" in features_df.columns
        assert "current_activity" in features_df.columns
        assert "next_activity" in features_df.columns
        assert "remaining_time" in features_df.columns
    
    def test_train_outcome_model(self, sample_event_log):
        """Test outcome model training."""
        from demos.predictive import ProcessPredictor
        
        predictor = ProcessPredictor()
        result = predictor.train_outcome_model(sample_event_log)
        
        assert "accuracy" in result
        assert 0 <= result["accuracy"] <= 1
        assert predictor.outcome_model is not None
    
    def test_train_next_activity_model(self, sample_event_log):
        """Test next activity model training."""
        from demos.predictive import ProcessPredictor
        
        predictor = ProcessPredictor()
        # First train outcome model to set up encoders
        predictor.train_outcome_model(sample_event_log)
        result = predictor.train_next_activity_model(sample_event_log)
        
        assert "accuracy" in result
        assert "classes" in result
        assert predictor.next_activity_model is not None
    
    def test_train_time_model(self, sample_event_log):
        """Test time prediction model training."""
        from demos.predictive import ProcessPredictor
        
        predictor = ProcessPredictor()
        predictor.train_outcome_model(sample_event_log)
        result = predictor.train_time_model(sample_event_log)
        
        assert "mae_hours" in result
        assert result["mae_hours"] >= 0
        assert predictor.time_model is not None


class TestRunDemo:
    """Tests for the run_demo function."""
    
    def test_run_demo_returns_all_results(self, sample_event_log):
        """Test that run_demo returns all expected results."""
        from demos.predictive import run_demo
        
        results = run_demo(sample_event_log)
        
        assert "outcome_model" in results
        assert "next_activity_model" in results
        assert "time_model" in results
        assert "sample_prediction" in results
    
    def test_sample_prediction_structure(self, sample_event_log):
        """Test sample prediction has expected structure."""
        from demos.predictive import run_demo
        
        results = run_demo(sample_event_log)
        pred = results["sample_prediction"]
        
        # Should have completion probability
        assert "completion_probability" in pred or len(pred) > 0
