"""
Process Simulation Demo
Using SimPy for Discrete Event Simulation
"""
import simpy
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
import statistics


@dataclass
class SimulationConfig:
    """Configuration for process simulation."""
    num_clerks: int = 3
    num_credit_checkers: int = 2
    num_warehouse_staff: int = 4
    num_shippers: int = 2
    
    # Activity durations (mean in hours)
    order_processing_time: float = 0.5
    credit_check_time: float = 2.0
    stock_check_time: float = 1.0
    pick_pack_time: float = 4.0
    shipping_time: float = 24.0
    
    # Arrival rate (cases per hour)
    arrival_rate: float = 2.0
    
    # Simulation duration (hours)
    simulation_duration: float = 168  # 1 week


@dataclass
class SimulationResults:
    """Results from process simulation."""
    total_cases: int = 0
    completed_cases: int = 0
    avg_cycle_time: float = 0.0
    min_cycle_time: float = 0.0
    max_cycle_time: float = 0.0
    p50_cycle_time: float = 0.0
    p90_cycle_time: float = 0.0
    avg_wait_time: float = 0.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    bottleneck: str = ""
    cycle_times: List[float] = field(default_factory=list)
    throughput_per_hour: float = 0.0


class ProcessSimulator:
    """
    Discrete Event Simulation for Order-to-Cash process.
    
    Simulates the process flow with:
    - Resource constraints (staff availability)
    - Stochastic activity durations
    - Queue management
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = None
        self.resources = {}
        self.cycle_times = []
        self.wait_times = []
        self.resource_busy_time = {}
        
    def setup_environment(self):
        """Initialize SimPy environment and resources."""
        self.env = simpy.Environment()
        
        self.resources = {
            'clerks': simpy.Resource(self.env, capacity=self.config.num_clerks),
            'credit_checkers': simpy.Resource(self.env, capacity=self.config.num_credit_checkers),
            'warehouse': simpy.Resource(self.env, capacity=self.config.num_warehouse_staff),
            'shippers': simpy.Resource(self.env, capacity=self.config.num_shippers)
        }
        
        self.resource_busy_time = {name: 0 for name in self.resources.keys()}
        self.cycle_times = []
        self.wait_times = []
    
    def exponential_duration(self, mean: float) -> float:
        """Generate exponentially distributed duration."""
        return random.expovariate(1.0 / mean)
    
    def process_case(self, case_id: int):
        """
        Process a single case through the Order-to-Cash flow.
        """
        arrival_time = self.env.now
        total_wait = 0
        
        # Activity 1: Order Received (Clerk)
        with self.resources['clerks'].request() as req:
            wait_start = self.env.now
            yield req
            total_wait += self.env.now - wait_start
            
            duration = self.exponential_duration(self.config.order_processing_time)
            self.resource_busy_time['clerks'] += duration
            yield self.env.timeout(duration)
        
        # Activity 2: Credit Check
        with self.resources['credit_checkers'].request() as req:
            wait_start = self.env.now
            yield req
            total_wait += self.env.now - wait_start
            
            duration = self.exponential_duration(self.config.credit_check_time)
            self.resource_busy_time['credit_checkers'] += duration
            yield self.env.timeout(duration)
        
        # 10% chance of credit rejection - case ends
        if random.random() < 0.1:
            cycle_time = self.env.now - arrival_time
            self.cycle_times.append(cycle_time)
            self.wait_times.append(total_wait)
            return
        
        # Activity 3: Stock Check & Pick/Pack (Warehouse)
        with self.resources['warehouse'].request() as req:
            wait_start = self.env.now
            yield req
            total_wait += self.env.now - wait_start
            
            # Stock check
            duration = self.exponential_duration(self.config.stock_check_time)
            self.resource_busy_time['warehouse'] += duration
            yield self.env.timeout(duration)
            
            # 5% chance of backorder
            if random.random() < 0.05:
                yield self.env.timeout(random.uniform(24, 72))  # Wait for stock
            
            # Pick and pack
            duration = self.exponential_duration(self.config.pick_pack_time)
            self.resource_busy_time['warehouse'] += duration
            yield self.env.timeout(duration)
        
        # Activity 4: Shipping
        with self.resources['shippers'].request() as req:
            wait_start = self.env.now
            yield req
            total_wait += self.env.now - wait_start
            
            duration = self.exponential_duration(self.config.shipping_time)
            self.resource_busy_time['shippers'] += duration
            yield self.env.timeout(duration)
        
        # Record metrics
        cycle_time = self.env.now - arrival_time
        self.cycle_times.append(cycle_time)
        self.wait_times.append(total_wait)
    
    def case_generator(self):
        """Generate cases according to arrival rate."""
        case_id = 0
        while True:
            # Inter-arrival time follows exponential distribution
            yield self.env.timeout(self.exponential_duration(1.0 / self.config.arrival_rate))
            case_id += 1
            self.env.process(self.process_case(case_id))
    
    def run(self) -> SimulationResults:
        """Run the simulation and return results."""
        self.setup_environment()
        
        # Start case generation
        self.env.process(self.case_generator())
        
        # Run simulation
        self.env.run(until=self.config.simulation_duration)
        
        # Calculate results
        results = SimulationResults()
        
        if self.cycle_times:
            results.total_cases = len(self.cycle_times)
            results.completed_cases = len([t for t in self.cycle_times if t > 0])
            results.avg_cycle_time = statistics.mean(self.cycle_times)
            results.min_cycle_time = min(self.cycle_times)
            results.max_cycle_time = max(self.cycle_times)
            results.p50_cycle_time = statistics.median(self.cycle_times)
            results.p90_cycle_time = np.percentile(self.cycle_times, 90)
            results.cycle_times = self.cycle_times
            results.throughput_per_hour = results.completed_cases / self.config.simulation_duration
        
        if self.wait_times:
            results.avg_wait_time = statistics.mean(self.wait_times)
        
        # Calculate resource utilization
        for name, resource in self.resources.items():
            total_capacity_hours = resource.capacity * self.config.simulation_duration
            utilization = self.resource_busy_time[name] / total_capacity_hours if total_capacity_hours > 0 else 0
            results.resource_utilization[name] = min(utilization, 1.0)  # Cap at 100%
        
        # Identify bottleneck (highest utilization)
        if results.resource_utilization:
            results.bottleneck = max(results.resource_utilization, key=results.resource_utilization.get)
        
        return results


def compare_scenarios(base_config: SimulationConfig, scenarios: Dict[str, SimulationConfig]) -> Dict[str, SimulationResults]:
    """
    Compare multiple simulation scenarios.
    Useful for what-if analysis.
    """
    results = {}
    
    # Run baseline
    simulator = ProcessSimulator(base_config)
    results['baseline'] = simulator.run()
    
    # Run scenarios
    for name, config in scenarios.items():
        simulator = ProcessSimulator(config)
        results[name] = simulator.run()
    
    return results


def run_demo() -> Dict:
    """Run the simulation demo with sample scenarios."""
    
    # Baseline configuration
    base_config = SimulationConfig()
    
    # Scenario: Add more credit checkers
    scenario_more_credit = SimulationConfig(num_credit_checkers=4)
    
    # Scenario: Add more warehouse staff
    scenario_more_warehouse = SimulationConfig(num_warehouse_staff=6)
    
    # Scenario: Higher demand
    scenario_high_demand = SimulationConfig(arrival_rate=4.0)
    
    scenarios = {
        'more_credit_checkers': scenario_more_credit,
        'more_warehouse_staff': scenario_more_warehouse,
        'high_demand': scenario_high_demand
    }
    
    results = compare_scenarios(base_config, scenarios)
    
    # Format results for display
    formatted = {}
    for name, result in results.items():
        formatted[name] = {
            'total_cases': result.total_cases,
            'avg_cycle_time_hours': round(result.avg_cycle_time, 2),
            'avg_cycle_time_days': round(result.avg_cycle_time / 24, 2),
            'p90_cycle_time_hours': round(result.p90_cycle_time, 2),
            'avg_wait_time_hours': round(result.avg_wait_time, 2),
            'throughput_per_day': round(result.throughput_per_hour * 24, 1),
            'bottleneck': result.bottleneck,
            'resource_utilization': {k: f"{v*100:.1f}%" for k, v in result.resource_utilization.items()}
        }
    
    return formatted
