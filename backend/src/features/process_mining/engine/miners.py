"""Miners - Process Discovery algorithms.

Wraps pm4py.discover_* functions.
"""

from typing import Any, Literal

import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.petri_net.obj import Marking, PetriNet

# Type alias for algorithm names
MinerAlgorithm = Literal["alpha", "inductive", "heuristic", "dfg"]


def discover_petri_net(
    log: pm4py.EventLog,
    algorithm: MinerAlgorithm = "inductive",
    **params,
) -> tuple[PetriNet, Marking, Marking]:
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
    if algorithm == "inductive":
        return pm4py.discover_petri_net_inductive(log, **params)
    if algorithm == "heuristic":
        return pm4py.discover_petri_net_heuristics(log, **params)
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


def discover_dfg(log: pm4py.EventLog) -> dict[tuple[str, str], int]:
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
    import tempfile

    from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

    with tempfile.NamedTemporaryFile(suffix=".pnml", delete=False) as f:
        pnml_exporter.apply(net, im, f.name, final_marking=fm)
        with open(f.name) as pnml_file:
            return pnml_file.read()


def serialize_bpmn(bpmn: BPMN) -> str:
    """Serialize BPMN to XML format.

    Returns:
        BPMN XML string.
    """
    import tempfile

    from pm4py.objects.bpmn.exporter import exporter as bpmn_exporter

    with tempfile.NamedTemporaryFile(suffix=".bpmn", delete=False) as f:
        bpmn_exporter.apply(bpmn, f.name)
        with open(f.name) as bpmn_file:
            return bpmn_file.read()
