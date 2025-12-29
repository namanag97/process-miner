"""
Process Optimization Demo
Using PuLP for Linear Programming
"""
from pulp import *
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StaffingProblem:
    """Staffing optimization problem definition."""
    shifts: List[str]
    demand: Dict[str, int]  # Minimum staff needed per shift
    cost_per_hour: Dict[str, float]  # Cost per hour per shift
    hours_per_shift: int = 8
    max_staff_per_shift: int = 20
    

@dataclass
class OptimizationResult:
    """Result of optimization."""
    status: str
    optimal_staffing: Dict[str, int]
    total_cost: float
    total_staff: int
    cost_breakdown: Dict[str, float]


class StaffingOptimizer:
    """
    Optimize staffing levels to meet demand at minimum cost.
    
    Uses Linear Programming (LP) via PuLP library.
    """
    
    def __init__(self, problem: StaffingProblem):
        self.problem = problem
        
    def solve(self) -> OptimizationResult:
        """
        Solve the staffing optimization problem.
        
        Decision Variables: Number of staff per shift (integer)
        Objective: Minimize total labor cost
        Constraints: 
            - Meet minimum demand per shift
            - Maximum staff capacity per shift
        """
        # Create the problem
        prob = LpProblem("Staffing_Optimization", LpMinimize)
        
        # Decision variables: staff per shift (integer)
        staff = LpVariable.dicts(
            "staff", 
            self.problem.shifts, 
            lowBound=0, 
            upBound=self.problem.max_staff_per_shift,
            cat='Integer'
        )
        
        # Objective: Minimize total cost
        prob += lpSum([
            staff[s] * self.problem.cost_per_hour[s] * self.problem.hours_per_shift 
            for s in self.problem.shifts
        ]), "Total_Labor_Cost"
        
        # Constraints: Meet minimum demand per shift
        for s in self.problem.shifts:
            prob += staff[s] >= self.problem.demand[s], f"Demand_{s}"
        
        # Solve
        prob.solve(PULP_CBC_CMD(msg=0))
        
        # Extract results
        optimal_staffing = {s: int(staff[s].varValue) for s in self.problem.shifts}
        
        cost_breakdown = {
            s: optimal_staffing[s] * self.problem.cost_per_hour[s] * self.problem.hours_per_shift
            for s in self.problem.shifts
        }
        
        return OptimizationResult(
            status=LpStatus[prob.status],
            optimal_staffing=optimal_staffing,
            total_cost=value(prob.objective),
            total_staff=sum(optimal_staffing.values()),
            cost_breakdown=cost_breakdown
        )


class ProcessRoutingOptimizer:
    """
    Optimize process routing/assignment.
    
    Example: Assign cases to resources to minimize total processing time.
    """
    
    def __init__(self, cases: List[str], resources: List[str], 
                 processing_times: Dict[tuple, float], 
                 resource_capacity: Dict[str, int]):
        self.cases = cases
        self.resources = resources
        self.processing_times = processing_times  # (case, resource) -> time
        self.resource_capacity = resource_capacity
    
    def solve(self) -> Dict:
        """Solve the assignment problem."""
        prob = LpProblem("Process_Assignment", LpMinimize)
        
        # Decision variables: binary assignment
        assign = LpVariable.dicts(
            "assign",
            [(c, r) for c in self.cases for r in self.resources],
            cat='Binary'
        )
        
        # Objective: Minimize total processing time
        prob += lpSum([
            assign[(c, r)] * self.processing_times.get((c, r), 999)
            for c in self.cases
            for r in self.resources
        ]), "Total_Processing_Time"
        
        # Constraint: Each case assigned to exactly one resource
        for c in self.cases:
            prob += lpSum([assign[(c, r)] for r in self.resources]) == 1, f"Assign_{c}"
        
        # Constraint: Resource capacity
        for r in self.resources:
            prob += lpSum([assign[(c, r)] for c in self.cases]) <= self.resource_capacity[r], f"Capacity_{r}"
        
        prob.solve(PULP_CBC_CMD(msg=0))
        
        # Extract assignments
        assignments = {}
        for c in self.cases:
            for r in self.resources:
                if assign[(c, r)].varValue == 1:
                    assignments[c] = r
                    break
        
        return {
            'status': LpStatus[prob.status],
            'assignments': assignments,
            'total_time': value(prob.objective)
        }


class SLAOptimizer:
    """
    Optimize resource allocation to minimize SLA breaches.
    """
    
    def optimize_for_sla(self, current_backlog: int, sla_hours: float,
                         productivity_per_staff: float, staff_cost: float,
                         sla_breach_penalty: float) -> Dict:
        """
        Find optimal staffing to balance cost vs SLA breaches.
        
        Args:
            current_backlog: Number of cases in queue
            sla_hours: Target hours to complete each case
            productivity_per_staff: Cases processed per staff per hour
            staff_cost: Cost per staff member per hour
            sla_breach_penalty: Penalty cost per breached case
        """
        prob = LpProblem("SLA_Optimization", LpMinimize)
        
        # Decision variable: number of staff
        staff = LpVariable("staff", lowBound=1, upBound=50, cat='Integer')
        
        # Calculate processing capacity
        hours_available = sla_hours
        
        # Cases that can be processed
        # This is a simplification - in reality would need more complex modeling
        
        # For demo, we'll try different staffing levels
        best_cost = float('inf')
        best_staff = 1
        
        for s in range(1, 51):
            capacity = s * productivity_per_staff * hours_available
            breaches = max(0, current_backlog - capacity)
            cost = s * staff_cost * hours_available + breaches * sla_breach_penalty
            
            if cost < best_cost:
                best_cost = cost
                best_staff = s
        
        capacity = best_staff * productivity_per_staff * hours_available
        breaches = max(0, current_backlog - capacity)
        
        return {
            'optimal_staff': best_staff,
            'processing_capacity': capacity,
            'expected_breaches': breaches,
            'staff_cost': best_staff * staff_cost * hours_available,
            'breach_cost': breaches * sla_breach_penalty,
            'total_cost': best_cost
        }


def run_demo() -> Dict:
    """Run the optimization demo."""
    results = {}
    
    # Demo 1: Staffing Optimization
    problem = StaffingProblem(
        shifts=["Morning", "Afternoon", "Evening", "Night"],
        demand={"Morning": 8, "Afternoon": 12, "Evening": 6, "Night": 3},
        cost_per_hour={"Morning": 25, "Afternoon": 25, "Evening": 30, "Night": 35},
        hours_per_shift=8
    )
    
    optimizer = StaffingOptimizer(problem)
    staffing_result = optimizer.solve()
    
    results['staffing_optimization'] = {
        'status': staffing_result.status,
        'optimal_staffing': staffing_result.optimal_staffing,
        'total_staff': staffing_result.total_staff,
        'total_daily_cost': f"${staffing_result.total_cost:,.2f}",
        'cost_breakdown': {k: f"${v:,.2f}" for k, v in staffing_result.cost_breakdown.items()}
    }
    
    # Demo 2: Case Assignment
    cases = [f"CASE-{i}" for i in range(1, 11)]
    resources = ["Alice", "Bob", "Carol"]
    
    # Random processing times
    import random
    random.seed(42)
    processing_times = {
        (c, r): random.uniform(0.5, 4.0)
        for c in cases
        for r in resources
    }
    
    routing_optimizer = ProcessRoutingOptimizer(
        cases=cases,
        resources=resources,
        processing_times=processing_times,
        resource_capacity={"Alice": 4, "Bob": 4, "Carol": 4}
    )
    
    routing_result = routing_optimizer.solve()
    results['case_assignment'] = {
        'status': routing_result['status'],
        'assignments': routing_result['assignments'],
        'total_processing_time': f"{routing_result['total_time']:.2f} hours"
    }
    
    # Demo 3: SLA Optimization
    sla_optimizer = SLAOptimizer()
    sla_result = sla_optimizer.optimize_for_sla(
        current_backlog=100,
        sla_hours=8,
        productivity_per_staff=3,  # 3 cases per hour per person
        staff_cost=30,  # $30/hour
        sla_breach_penalty=500  # $500 per breach
    )
    
    results['sla_optimization'] = {
        'optimal_staff': sla_result['optimal_staff'],
        'processing_capacity': f"{sla_result['processing_capacity']:.0f} cases",
        'expected_sla_breaches': int(sla_result['expected_breaches']),
        'labor_cost': f"${sla_result['staff_cost']:,.2f}",
        'breach_penalty_cost': f"${sla_result['breach_cost']:,.2f}",
        'total_cost': f"${sla_result['total_cost']:,.2f}"
    }
    
    return results
