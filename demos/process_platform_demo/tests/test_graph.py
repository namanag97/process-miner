"""
Tests for Process Graph Module
"""
import pytest
import pandas as pd
from datetime import datetime


class TestProcessGraph:
    """Tests for ProcessGraph class."""
    
    def test_graph_initialization(self):
        """Test graph initializes correctly."""
        from demos.graph import ProcessGraph
        
        graph = ProcessGraph()
        
        assert graph.graph.number_of_nodes() == 0
        assert graph.graph.number_of_edges() == 0
        assert len(graph.activity_counts) == 0
    
    def test_build_from_event_log(self, minimal_event_log):
        """Test building graph from event log."""
        from demos.graph import ProcessGraph
        
        events = minimal_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        assert graph.graph.number_of_nodes() == 3  # Start, Process, End
        assert graph.graph.number_of_edges() >= 2
    
    def test_get_start_activities(self, minimal_event_log):
        """Test finding start activities."""
        from demos.graph import ProcessGraph
        
        events = minimal_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        start_activities = graph.get_start_activities()
        assert "Start" in start_activities
    
    def test_get_end_activities(self, minimal_event_log):
        """Test finding end activities."""
        from demos.graph import ProcessGraph
        
        events = minimal_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        end_activities = graph.get_end_activities()
        assert "End" in end_activities
    
    def test_detect_bottleneck(self, sample_event_log):
        """Test bottleneck detection."""
        from demos.graph import ProcessGraph
        
        events = sample_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        bottleneck = graph.detect_bottleneck()
        # Should return a non-empty string
        assert isinstance(bottleneck, str)
    
    def test_calculate_metrics(self, sample_event_log):
        """Test metrics calculation."""
        from demos.graph import ProcessGraph
        
        events = sample_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        metrics = graph.calculate_metrics()
        
        assert metrics.num_activities > 0
        assert metrics.num_transitions >= 0
        assert metrics.avg_path_length > 0
        assert metrics.variants_count > 0
    
    def test_to_vis_format(self, minimal_event_log):
        """Test visualization format export."""
        from demos.graph import ProcessGraph
        
        events = minimal_event_log.to_dict("records")
        graph = ProcessGraph()
        graph.build_from_event_log(events)
        
        vis_data = graph.to_vis_format()
        
        assert "nodes" in vis_data
        assert "edges" in vis_data
        assert len(vis_data["nodes"]) == 3


class TestBuildGraphFromDataframe:
    """Tests for build_graph_from_dataframe function."""
    
    def test_build_from_dataframe(self, sample_event_log):
        """Test building graph from DataFrame."""
        from demos.graph import build_graph_from_dataframe
        
        graph = build_graph_from_dataframe(sample_event_log)
        
        assert graph.graph.number_of_nodes() > 0
        assert len(graph.variants) > 0


class TestRunDemo:
    """Tests for run_demo function."""
    
    def test_run_demo_returns_expected_keys(self, sample_event_log):
        """Test run_demo returns all expected keys."""
        from demos.graph import run_demo
        
        results = run_demo(sample_event_log)
        
        assert "metrics" in results
        assert "activity_statistics" in results
        assert "top_transitions" in results
        assert "top_variants" in results
        assert "visualization_data" in results
