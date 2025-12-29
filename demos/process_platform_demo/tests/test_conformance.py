"""
Tests for Conformance Checking Module
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta


class TestConformanceChecker:
    """Tests for ConformanceChecker class."""
    
    def test_checker_initialization(self):
        """Test checker initializes correctly."""
        from demos.conformance import ConformanceChecker
        
        checker = ConformanceChecker()
        
        assert checker.rules == []
        assert checker.reference_model == []
    
    def test_add_precedence_rule(self):
        """Test adding precedence rules."""
        from demos.conformance import ConformanceChecker
        
        checker = ConformanceChecker()
        checker.add_precedence_rule("TestRule", "A", "B")
        
        assert len(checker.rules) == 1
        assert checker.rules[0].rule_type == "precedence"
        assert checker.rules[0].activities == ["A", "B"]
    
    def test_add_response_rule(self):
        """Test adding response rules."""
        from demos.conformance import ConformanceChecker
        
        checker = ConformanceChecker()
        checker.add_response_rule("TestRule", "Trigger", "Response")
        
        assert len(checker.rules) == 1
        assert checker.rules[0].rule_type == "response"
    
    def test_add_exclusion_rule(self):
        """Test adding exclusion rules."""
        from demos.conformance import ConformanceChecker
        
        checker = ConformanceChecker()
        checker.add_exclusion_rule("TestRule", "A", "B")
        
        assert len(checker.rules) == 1
        assert checker.rules[0].rule_type == "exclusion"
    
    def test_check_conformance_all_conformant(self):
        """Test checking conformance with all conformant cases."""
        from demos.conformance import ConformanceChecker
        
        # Create event log where A always comes before B
        df = pd.DataFrame([
            {"case_id": "C1", "activity": "A", "timestamp": datetime(2024, 1, 1, 10, 0)},
            {"case_id": "C1", "activity": "B", "timestamp": datetime(2024, 1, 1, 11, 0)},
            {"case_id": "C2", "activity": "A", "timestamp": datetime(2024, 1, 1, 10, 0)},
            {"case_id": "C2", "activity": "B", "timestamp": datetime(2024, 1, 1, 11, 0)},
        ])
        
        checker = ConformanceChecker()
        checker.add_precedence_rule("ABeforeB", "A", "B")
        
        result = checker.check_conformance(df)
        
        assert result.conformant_cases == 2
        assert result.non_conformant_cases == 0
        assert result.fitness == 1.0
    
    def test_check_conformance_detects_violations(self):
        """Test that conformance checking detects violations."""
        from demos.conformance import ConformanceChecker
        
        # Create event log where B comes before A in one case
        df = pd.DataFrame([
            {"case_id": "C1", "activity": "B", "timestamp": datetime(2024, 1, 1, 10, 0)},
            {"case_id": "C1", "activity": "A", "timestamp": datetime(2024, 1, 1, 11, 0)},
        ])
        
        checker = ConformanceChecker()
        checker.add_precedence_rule("ABeforeB", "A", "B")
        
        result = checker.check_conformance(df)
        
        assert result.non_conformant_cases >= 1
    
    def test_get_deviation_report(self, sample_event_log):
        """Test deviation report generation."""
        from demos.conformance import ConformanceChecker
        
        checker = ConformanceChecker()
        checker.add_precedence_rule("TestRule", "NonExistent1", "NonExistent2")
        
        result = checker.check_conformance(sample_event_log)
        report = checker.get_deviation_report(result)
        
        assert isinstance(report, pd.DataFrame)


class TestCreateO2CChecker:
    """Tests for Order-to-Cash conformance checker."""
    
    def test_creates_checker_with_rules(self):
        """Test O2C checker has expected rules."""
        from demos.conformance import create_o2c_conformance_checker
        
        checker = create_o2c_conformance_checker()
        
        assert len(checker.rules) > 0
        assert checker.reference_model is not None


class TestRunDemo:
    """Tests for run_demo function."""
    
    def test_run_demo_returns_expected_keys(self, sample_event_log):
        """Test run_demo returns all expected keys."""
        from demos.conformance import run_demo
        
        results = run_demo(sample_event_log)
        
        assert "fitness_score" in results
        assert "precision_score" in results
        assert "conformant_cases" in results
        assert "non_conformant_cases" in results
        assert "rules_checked" in results
