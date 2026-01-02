"""Miners - Process Discovery algorithms.

Wraps pm4py.discover_* functions.
"""

from typing import Any, Dict, Literal, Optional, Tuple

import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.bpmn.obj import BPMN

from src.domain.models import ProcessModelType


# Type alias for algorithm names
MinerAlgorithm = Literal["alpha", "inductive", "heuristic", "dfg"]


def discover_petri_net(
    log: pm4py.EventLog,
    algorithm: MinerAlgorithm = "inductive",
    **params,
) -> Tuple[PetriNet, Marking, Marking]:
    """Discover a Petri Net from an event log.
    
    Args:
        log: PM4Py EventLog.
        algorithm: Mining algorithm to use.
        **params: Algorithm-specific parameters.
        
    Returns:
        Tuple of (PetriNet, initial_marking, final_marking).
    """
    if algorithm == "alpha":
        return pm4py.discover_petri_net_alpha(log, **params)
    elif algorithm == "inductive":
        return pm4py.discover_petri_net_inductive(log, **params)
    elif algorithm == "heuristic":
        return pm4py.discover_petri_net_heuristics(log, **params)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def discover_bpmn(
    log: pm4py.EventLog,
    algorithm: MinerAlgorithm = "inductive",
) -> BPMN:
    """Discover a BPMN model from an event log.
    
    Args:
        log: PM4Py EventLog.
        algorithm: Mining algorithm (converts via Petri net).
        
    Returns:
        BPMN object.
    """
    net, im, fm = discover_petri_net(log, algorithm)
    return pm4py.convert_to_bpmn(net, im, fm)


def discover_dfg(log: pm4py.EventLog) -> Dict[Tuple[str, str], int]:
    """Discover a Directly-Follows Graph.
    
    Args:
        log: PM4Py EventLog.
        
    Returns:
        Dict mapping (source_activity, target_activity) to frequency.
    """
    return pm4py.discover_dfg(log)


def discover_process_tree(log: pm4py.EventLog) -> Any:
    """Discover a Process Tree using Inductive Miner.
    
    Args:
        log: PM4Py EventLog.
        
    Returns:
        ProcessTree object.
    """
    return pm4py.discover_process_tree_inductive(log)


def serialize_petri_net(
    net: PetriNet,
    im: Marking,
    fm: Marking,
) -> str:
    """Serialize Petri Net to PNML format.
    
    Returns:
        PNML XML string.
    """
    from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".pnml", delete=False) as f:
        pnml_exporter.apply(net, im, f.name, final_marking=fm)
        with open(f.name, "r") as pnml_file:
            return pnml_file.read()


def serialize_bpmn(bpmn: BPMN) -> str:
    """Serialize BPMN to XML format.
    
    Returns:
        BPMN XML string.
    """
    from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter
    import tempfile
    
    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as f:
        bpmn_exporter.apply(bpmn, f.name)
        with open(f.name, "r") as bpmn_file:
            return bpmn_file.read()
