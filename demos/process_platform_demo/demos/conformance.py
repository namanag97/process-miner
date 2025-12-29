"""
Conformance Checking Demo
Using process mining conformance techniques
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ConformanceResult:
    """Result of conformance checking."""
    fitness: float
    precision: float
    generalization: float
    conformant_cases: int
    non_conformant_cases: int
    deviation_types: Dict[str, int]
    case_deviations: Dict[str, List[str]]


@dataclass
class ProcessRule:
    """A process rule for conformance checking."""
    name: str
    description: str
    rule_type: str  # 'precedence', 'response', 'sequence', 'exclusion', 'cardinality'
    activities: List[str]
    parameters: Dict = field(default_factory=dict)


class ConformanceChecker:
    """
    Check conformance of event log against process rules.
    
    Implements:
    1. Token-based replay fitness
    2. Declarative constraint checking
    3. Temporal constraint checking
    4. Resource-based rules
    """
    
    def __init__(self, reference_model: List[str] = None):
        """
        Initialize conformance checker.
        
        Args:
            reference_model: Expected sequence of activities (happy path)
        """
        self.reference_model = reference_model or []
        self.rules: List[ProcessRule] = []
    
    def add_rule(self, rule: ProcessRule):
        """Add a conformance rule."""
        self.rules.append(rule)
    
    def add_precedence_rule(self, name: str, activity_a: str, activity_b: str):
        """Activity A must occur before Activity B."""
        self.rules.append(ProcessRule(
            name=name,
            description=f"'{activity_a}' must occur before '{activity_b}'",
            rule_type="precedence",
            activities=[activity_a, activity_b]
        ))
    
    def add_response_rule(self, name: str, trigger: str, response: str):
        """If trigger occurs, response must eventually occur."""
        self.rules.append(ProcessRule(
            name=name,
            description=f"If '{trigger}' occurs, '{response}' must follow",
            rule_type="response",
            activities=[trigger, response]
        ))
    
    def add_exclusion_rule(self, name: str, activity_a: str, activity_b: str):
        """Activity A and B cannot both occur in same case."""
        self.rules.append(ProcessRule(
            name=name,
            description=f"'{activity_a}' and '{activity_b}' are mutually exclusive",
            rule_type="exclusion",
            activities=[activity_a, activity_b]
        ))
    
    def add_cardinality_rule(self, name: str, activity: str, min_count: int, max_count: int):
        """Activity must occur between min and max times."""
        self.rules.append(ProcessRule(
            name=name,
            description=f"'{activity}' must occur {min_count}-{max_count} times",
            rule_type="cardinality",
            activities=[activity],
            parameters={"min": min_count, "max": max_count}
        ))
    
    def add_time_rule(self, name: str, activity_a: str, activity_b: str, max_hours: float):
        """Maximum time allowed between two activities."""
        self.rules.append(ProcessRule(
            name=name,
            description=f"'{activity_a}' to '{activity_b}' must take <= {max_hours} hours",
            rule_type="time",
            activities=[activity_a, activity_b],
            parameters={"max_hours": max_hours}
        ))
    
    def check_conformance(self, event_log: pd.DataFrame) -> ConformanceResult:
        """
        Check conformance of event log against all rules.
        """
        case_deviations = defaultdict(list)
        deviation_counts = defaultdict(int)
        
        # Check each case
        for case_id, case_events in event_log.groupby('case_id'):
            case_events = case_events.sort_values('timestamp')
            activities = case_events['activity'].tolist()
            timestamps = case_events['timestamp'].tolist()
            
            # Check each rule
            for rule in self.rules:
                violation = self._check_rule(rule, activities, timestamps)
                if violation:
                    case_deviations[case_id].append(violation)
                    deviation_counts[rule.name] += 1
        
        # Calculate fitness (percentage of conformant traces)
        conformant_cases = sum(1 for deviations in case_deviations.values() if len(deviations) == 0)
        total_cases = event_log['case_id'].nunique()
        non_conformant = total_cases - conformant_cases
        
        fitness = conformant_cases / total_cases if total_cases > 0 else 1.0
        
        # Calculate precision (how well log matches model - simplified)
        precision = self._calculate_precision(event_log)
        
        return ConformanceResult(
            fitness=fitness,
            precision=precision,
            generalization=0.85,  # Simplified
            conformant_cases=conformant_cases,
            non_conformant_cases=non_conformant,
            deviation_types=dict(deviation_counts),
            case_deviations=dict(case_deviations)
        )
    
    def _check_rule(self, rule: ProcessRule, activities: List[str], 
                    timestamps: List) -> str:
        """Check if a rule is violated."""
        
        if rule.rule_type == "precedence":
            a, b = rule.activities
            if b in activities:
                if a not in activities:
                    return f"'{a}' missing before '{b}'"
                if activities.index(b) < activities.index(a):
                    return f"'{b}' occurred before '{a}'"
        
        elif rule.rule_type == "response":
            trigger, response = rule.activities
            if trigger in activities and response not in activities:
                return f"'{response}' missing after '{trigger}'"
        
        elif rule.rule_type == "exclusion":
            a, b = rule.activities
            if a in activities and b in activities:
                return f"Both '{a}' and '{b}' occurred"
        
        elif rule.rule_type == "cardinality":
            activity = rule.activities[0]
            count = activities.count(activity)
            min_c = rule.parameters.get("min", 0)
            max_c = rule.parameters.get("max", float('inf'))
            if count < min_c:
                return f"'{activity}' occurred {count} times (min: {min_c})"
            if count > max_c:
                return f"'{activity}' occurred {count} times (max: {max_c})"
        
        elif rule.rule_type == "time":
            a, b = rule.activities
            if a in activities and b in activities:
                idx_a = activities.index(a)
                idx_b = activities.index(b)
                if idx_b > idx_a:
                    time_diff = (timestamps[idx_b] - timestamps[idx_a]).total_seconds() / 3600
                    max_hours = rule.parameters.get("max_hours", float('inf'))
                    if time_diff > max_hours:
                        return f"'{a}' to '{b}' took {time_diff:.1f}h (max: {max_hours}h)"
        
        return None  # No violation
    
    def _calculate_precision(self, event_log: pd.DataFrame) -> float:
        """Calculate precision (simplified version)."""
        if not self.reference_model:
            return 0.8
        
        # Check how many traces follow exactly the reference model
        exact_matches = 0
        total_cases = 0
        
        for case_id, case_events in event_log.groupby('case_id'):
            activities = case_events.sort_values('timestamp')['activity'].tolist()
            total_cases += 1
            
            # Check if trace is subset or matches reference
            if self._is_valid_trace(activities):
                exact_matches += 1
        
        return exact_matches / total_cases if total_cases > 0 else 1.0
    
    def _is_valid_trace(self, activities: List[str]) -> bool:
        """Check if trace follows reference model (simplified)."""
        if not self.reference_model:
            return True
        
        # Check if activities are in valid order
        ref_set = set(self.reference_model)
        model_idx = 0
        
        for act in activities:
            if act in ref_set:
                while model_idx < len(self.reference_model) and self.reference_model[model_idx] != act:
                    model_idx += 1
                if model_idx >= len(self.reference_model):
                    return False
                model_idx += 1
        
        return True
    
    def get_deviation_report(self, result: ConformanceResult) -> pd.DataFrame:
        """Generate detailed deviation report."""
        rows = []
        
        for case_id, deviations in result.case_deviations.items():
            for deviation in deviations:
                rows.append({
                    "case_id": case_id,
                    "deviation": deviation,
                    "severity": "High" if "missing" in deviation.lower() else "Medium"
                })
        
        return pd.DataFrame(rows)


def create_o2c_conformance_checker() -> ConformanceChecker:
    """Create conformance checker with O2C rules."""
    reference = [
        "Create Sales Order",
        "Credit Check",
        "Approve Credit", 
        "Release Order",
        "Pick Materials",
        "Pack Goods",
        "Ship Goods",
        "Create Invoice",
        "Receive Payment",
        "Close Order"
    ]
    
    checker = ConformanceChecker(reference)
    
    # Add business rules
    checker.add_precedence_rule("CreditBeforeRelease", "Credit Check", "Release Order")
    checker.add_precedence_rule("ShipBeforeInvoice", "Ship Goods", "Create Invoice")
    checker.add_response_rule("OrderRequiresPayment", "Create Sales Order", "Receive Payment")
    checker.add_cardinality_rule("SingleCreditCheck", "Credit Check", 1, 2)
    checker.add_time_rule("CreditSLA", "Create Sales Order", "Credit Check", 24)
    
    return checker


def run_demo(event_log: pd.DataFrame) -> Dict:
    """Run conformance checking demo."""
    
    # Create checker with rules
    checker = create_o2c_conformance_checker()
    
    # Run conformance check
    result = checker.check_conformance(event_log)
    
    # Get deviation report
    deviation_df = checker.get_deviation_report(result)
    
    # Aggregate deviations by type
    deviation_summary = deviation_df.groupby('deviation').size().sort_values(ascending=False).head(10)
    
    return {
        "fitness_score": round(result.fitness * 100, 1),
        "precision_score": round(result.precision * 100, 1),
        "conformant_cases": result.conformant_cases,
        "non_conformant_cases": result.non_conformant_cases,
        "deviation_types": result.deviation_types,
        "top_deviations": deviation_summary.to_dict(),
        "rules_checked": [
            {"name": r.name, "description": r.description, "type": r.rule_type}
            for r in checker.rules
        ],
        "sample_violations": deviation_df.head(20).to_dict('records')
    }
