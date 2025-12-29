"""
Tests for Optimization Module
"""
import pytest


class TestStaffingProblem:
    """Tests for StaffingProblem class."""
    
    def test_default_problem_creation(self):
        """Test creating a staffing problem."""
        from demos.optimization import StaffingProblem
        
        problem = StaffingProblem(
            shifts=["Morning", "Evening"],
            demand={"Morning": 5, "Evening": 3},
            cost_per_hour={"Morning": 20, "Evening": 25}
        )
        
        assert len(problem.shifts) == 2
        assert problem.demand["Morning"] == 5
        assert problem.hours_per_shift == 8


class TestStaffingOptimizer:
    """Tests for StaffingOptimizer class."""
    
    def test_optimizer_solves_problem(self):
        """Test that optimizer finds a solution."""
        from demos.optimization import StaffingProblem, StaffingOptimizer
        
        problem = StaffingProblem(
            shifts=["Morning", "Evening"],
            demand={"Morning": 5, "Evening": 3},
            cost_per_hour={"Morning": 20, "Evening": 25}
        )
        
        optimizer = StaffingOptimizer(problem)
        result = optimizer.solve()
        
        assert result.status == "Optimal"
        assert result.total_staff >= 8  # At least meet demand
        assert result.optimal_staffing["Morning"] >= 5
        assert result.optimal_staffing["Evening"] >= 3
    
    def test_optimal_staffing_meets_demand(self):
        """Test that optimal solution meets all demand."""
        from demos.optimization import StaffingProblem, StaffingOptimizer
        
        problem = StaffingProblem(
            shifts=["Morning", "Afternoon", "Night"],
            demand={"Morning": 10, "Afternoon": 15, "Night": 5},
            cost_per_hour={"Morning": 25, "Afternoon": 25, "Night": 30}
        )
        
        optimizer = StaffingOptimizer(problem)
        result = optimizer.solve()
        
        for shift in problem.shifts:
            assert result.optimal_staffing[shift] >= problem.demand[shift]


class TestSLAOptimizer:
    """Tests for SLAOptimizer class."""
    
    def test_sla_optimization(self):
        """Test SLA optimization."""
        from demos.optimization import SLAOptimizer
        
        optimizer = SLAOptimizer()
        result = optimizer.optimize_for_sla(
            current_backlog=50,
            sla_hours=8,
            productivity_per_staff=2,
            staff_cost=25,
            sla_breach_penalty=100
        )
        
        assert "optimal_staff" in result
        assert "expected_breaches" in result
        assert "total_cost" in result
        assert result["optimal_staff"] >= 1
    
    def test_more_backlog_needs_more_staff(self):
        """Test that higher backlog leads to more staff."""
        from demos.optimization import SLAOptimizer
        
        optimizer = SLAOptimizer()
        
        result_low = optimizer.optimize_for_sla(
            current_backlog=20, sla_hours=8,
            productivity_per_staff=2, staff_cost=25, sla_breach_penalty=100
        )
        
        result_high = optimizer.optimize_for_sla(
            current_backlog=200, sla_hours=8,
            productivity_per_staff=2, staff_cost=25, sla_breach_penalty=100
        )
        
        assert result_high["optimal_staff"] >= result_low["optimal_staff"]


class TestRunDemo:
    """Tests for run_demo function."""
    
    def test_run_demo_returns_all_results(self):
        """Test run_demo returns all expected results."""
        from demos.optimization import run_demo
        
        results = run_demo()
        
        assert "staffing_optimization" in results
        assert "case_assignment" in results
        assert "sla_optimization" in results
    
    def test_staffing_result_structure(self):
        """Test staffing result has expected structure."""
        from demos.optimization import run_demo
        
        results = run_demo()
        staffing = results["staffing_optimization"]
        
        assert "status" in staffing
        assert "optimal_staffing" in staffing
        assert "total_staff" in staffing
        assert "total_daily_cost" in staffing
