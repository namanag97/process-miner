"""
Tests for Simulation Module
"""
import pytest


class TestSimulationConfig:
    """Tests for SimulationConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        from demos.simulation import SimulationConfig
        
        config = SimulationConfig()
        
        assert config.num_clerks == 3
        assert config.num_credit_checkers == 2
        assert config.num_warehouse_staff == 4
        assert config.num_shippers == 2
        assert config.simulation_duration == 168  # 1 week
    
    def test_custom_config(self):
        """Test custom configuration values."""
        from demos.simulation import SimulationConfig
        
        config = SimulationConfig(
            num_clerks=5,
            num_credit_checkers=3,
            arrival_rate=5.0
        )
        
        assert config.num_clerks == 5
        assert config.num_credit_checkers == 3
        assert config.arrival_rate == 5.0


class TestProcessSimulator:
    """Tests for ProcessSimulator class."""
    
    def test_simulator_initialization(self):
        """Test simulator initializes correctly."""
        from demos.simulation import SimulationConfig, ProcessSimulator
        
        config = SimulationConfig()
        simulator = ProcessSimulator(config)
        
        assert simulator.config == config
        assert simulator.env is None
    
    def test_setup_environment(self):
        """Test environment setup."""
        from demos.simulation import SimulationConfig, ProcessSimulator
        
        config = SimulationConfig()
        simulator = ProcessSimulator(config)
        simulator.setup_environment()
        
        assert simulator.env is not None
        assert "clerks" in simulator.resources
        assert "credit_checkers" in simulator.resources
        assert "warehouse" in simulator.resources
        assert "shippers" in simulator.resources
    
    def test_run_simulation(self):
        """Test running a simulation."""
        from demos.simulation import SimulationConfig, ProcessSimulator
        
        # Use shorter simulation for testing
        config = SimulationConfig(simulation_duration=24)
        simulator = ProcessSimulator(config)
        
        result = simulator.run()
        
        assert result.total_cases > 0
        assert result.avg_cycle_time >= 0
        assert result.bottleneck != ""
        assert len(result.resource_utilization) == 4
    
    def test_resource_utilization_range(self):
        """Test resource utilization is between 0 and 1."""
        from demos.simulation import SimulationConfig, ProcessSimulator
        
        config = SimulationConfig(simulation_duration=24)
        simulator = ProcessSimulator(config)
        result = simulator.run()
        
        for util in result.resource_utilization.values():
            assert 0 <= util <= 1


class TestCompareScenarios:
    """Tests for compare_scenarios function."""
    
    def test_compare_scenarios(self):
        """Test scenario comparison."""
        from demos.simulation import SimulationConfig, compare_scenarios
        
        base = SimulationConfig(simulation_duration=24)
        scenarios = {
            "more_staff": SimulationConfig(num_clerks=5, simulation_duration=24)
        }
        
        results = compare_scenarios(base, scenarios)
        
        assert "baseline" in results
        assert "more_staff" in results


class TestRunDemo:
    """Tests for run_demo function."""
    
    def test_run_demo_returns_all_scenarios(self):
        """Test run_demo returns all scenarios."""
        from demos.simulation import run_demo
        
        results = run_demo()
        
        assert "baseline" in results
        assert len(results) >= 2  # At least baseline + one scenario
        
        # Check baseline has expected keys
        baseline = results["baseline"]
        assert "total_cases" in baseline
        assert "avg_cycle_time_hours" in baseline
        assert "bottleneck" in baseline
        assert "resource_utilization" in baseline
