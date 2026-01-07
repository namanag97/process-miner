"""Quality Evaluation Activities.

Temporal activities for computing process model quality metrics.
"""

from dataclasses import dataclass
from typing import Any

from temporalio import activity


@dataclass
class QualityMetricsInput:
    """Input for quality metric computation."""
    model_id: str
    dataset_id: str | None = None


@dataclass
class QualityMetricResult:
    """Result of quality metric computation."""
    value: float | None
    method: str
    error: str | None = None
    details: dict | None = None


@activity.defn
async def compute_fitness_activity(input: dict) -> dict:
    """Compute fitness metric using token-based replay.
    
    Args:
        input: dict with model_id, dataset_id
        
    Returns:
        dict with fitness value, method, and details
    """
    import pm4py
    from sqlalchemy import select
    
    from src.features.process_mining.models import ProcessModel
    from src.features.process_mining.services.event_log_loader import EventLogLoader
    from src.platform.infrastructure.database import async_session_maker
    
    model_id = input["model_id"]
    dataset_id = input["dataset_id"]
    
    async with async_session_maker() as db:
        # Load model
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model or not model.serialized_model:
            return {"value": None, "method": "error", "error": "Model not found"}
        
        # Deserialize model
        import pickle
        model_data = pickle.loads(model.serialized_model)
        
        # Load event log
        loader = EventLogLoader(db)
        log = await loader.load_pm4py_log(dataset_id)
        
        # Convert to Petri net if needed
        if model.model_format in ["process_tree"]:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
        elif model.model_format in ["petri_net"] and isinstance(model_data, tuple):
            net, im, fm = model_data
        else:
            try:
                net, im, fm = pm4py.convert_to_petri_net(model_data)
            except Exception as e:
                return {"value": None, "method": "error", "error": f"Cannot convert model: {e}"}
        
        # Compute fitness
        fitness_result = pm4py.fitness_token_based_replay(log, net, im, fm)
        
        return {
            "value": round(fitness_result.get("log_fitness", 0), 4),
            "method": "token_replay",
            "details": {
                "average_trace_fitness": fitness_result.get("average_trace_fitness"),
                "percentage_fitting": fitness_result.get("percentage_of_fitting_traces"),
            },
        }


@activity.defn
async def compute_precision_activity(input: dict) -> dict:
    """Compute precision metric.
    
    Args:
        input: dict with model_id, dataset_id
        
    Returns:
        dict with precision value and method
    """
    import pm4py
    from sqlalchemy import select
    
    from src.features.process_mining.models import ProcessModel
    from src.features.process_mining.services.event_log_loader import EventLogLoader
    from src.platform.infrastructure.database import async_session_maker
    
    model_id = input["model_id"]
    dataset_id = input["dataset_id"]
    
    async with async_session_maker() as db:
        # Load model
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model or not model.serialized_model:
            return {"value": None, "method": "error", "error": "Model not found"}
        
        import pickle
        model_data = pickle.loads(model.serialized_model)
        
        loader = EventLogLoader(db)
        log = await loader.load_pm4py_log(dataset_id)
        
        # Convert to Petri net
        if model.model_format in ["process_tree"]:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
        elif model.model_format in ["petri_net"] and isinstance(model_data, tuple):
            net, im, fm = model_data
        else:
            try:
                net, im, fm = pm4py.convert_to_petri_net(model_data)
            except Exception as e:
                return {"value": None, "method": "error", "error": f"Cannot convert model: {e}"}
        
        # Compute precision
        try:
            precision = pm4py.precision_token_based_replay(log, net, im, fm)
            return {"value": round(precision, 4), "method": "token_replay"}
        except Exception:
            try:
                precision = pm4py.precision_alignments(log, net, im, fm)
                return {"value": round(precision, 4), "method": "alignments"}
            except Exception as e:
                return {"value": None, "method": "error", "error": str(e)}


@activity.defn
async def compute_generalization_activity(input: dict) -> dict:
    """Compute generalization metric.
    
    This can be slow for large logs.
    """
    import pm4py
    from sqlalchemy import select
    
    from src.features.process_mining.models import ProcessModel
    from src.features.process_mining.services.event_log_loader import EventLogLoader
    from src.platform.infrastructure.database import async_session_maker
    
    model_id = input["model_id"]
    dataset_id = input["dataset_id"]
    
    async with async_session_maker() as db:
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model or not model.serialized_model:
            return {"value": None, "method": "error", "error": "Model not found"}
        
        import pickle
        model_data = pickle.loads(model.serialized_model)
        
        loader = EventLogLoader(db)
        log = await loader.load_pm4py_log(dataset_id)
        
        if model.model_format in ["process_tree"]:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
        elif model.model_format in ["petri_net"] and isinstance(model_data, tuple):
            net, im, fm = model_data
        else:
            try:
                net, im, fm = pm4py.convert_to_petri_net(model_data)
            except Exception as e:
                return {"value": None, "method": "error", "error": str(e)}
        
        try:
            gen = pm4py.generalization_tbr(log, net, im, fm)
            return {"value": round(gen, 4), "method": "token_replay"}
        except Exception as e:
            return {"value": None, "method": "unavailable", "error": str(e)}


@activity.defn
async def compute_simplicity_activity(input: dict) -> dict:
    """Compute simplicity metric based on model structure."""
    import pm4py
    from sqlalchemy import select
    
    from src.features.process_mining.models import ProcessModel
    from src.platform.infrastructure.database import async_session_maker
    
    model_id = input["model_id"]
    
    async with async_session_maker() as db:
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model or not model.serialized_model:
            return {"value": None, "method": "error", "error": "Model not found"}
        
        import pickle
        model_data = pickle.loads(model.serialized_model)
        
        # Convert to Petri net for analysis
        if model.model_format in ["process_tree"]:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
        elif model.model_format in ["petri_net"] and isinstance(model_data, tuple):
            net, im, fm = model_data
        else:
            try:
                net, im, fm = pm4py.convert_to_petri_net(model_data)
            except Exception:
                # Use basic metrics
                return {"value": 0.5, "method": "default"}
        
        try:
            simplicity = pm4py.simplicity_arc_degree(net)
            return {"value": round(simplicity, 4), "method": "arc_degree"}
        except Exception:
            # Manual computation
            places = len(net.places) if hasattr(net, "places") else 0
            transitions = len(net.transitions) if hasattr(net, "transitions") else 0
            arcs = len(net.arcs) if hasattr(net, "arcs") else 0
            nodes = places + transitions
            simplicity = 1 / (1 + arcs / max(nodes, 1)) if nodes > 0 else 0.5
            return {
                "value": round(simplicity, 4),
                "method": "arc_ratio",
                "details": {"places": places, "transitions": transitions, "arcs": arcs},
            }


@activity.defn
async def store_quality_metrics_activity(input: dict) -> dict:
    """Store computed quality metrics in the database."""
    from datetime import datetime
    from uuid import uuid4
    
    from sqlalchemy import select
    
    from src.features.process_mining.models import ProcessModel, ProcessModelMetrics
    from src.platform.infrastructure.database import async_session_maker
    
    model_id = input["model_id"]
    dataset_id = input["dataset_id"]
    results = input["results"]
    
    async with async_session_maker() as db:
        # Check if metrics exist
        query = select(ProcessModelMetrics).where(ProcessModelMetrics.model_id == model_id)
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        def get_value(r):
            if isinstance(r, dict):
                return r.get("value")
            return r
        
        fitness = get_value(results.get("fitness"))
        precision = get_value(results.get("precision"))
        generalization = get_value(results.get("generalization"))
        simplicity = get_value(results.get("simplicity"))
        
        f_score = None
        if fitness and precision and (fitness + precision) > 0:
            f_score = 2 * fitness * precision / (fitness + precision)
        
        if existing:
            existing.fitness = fitness
            existing.precision = precision
            existing.generalization = generalization
            existing.simplicity = simplicity
            existing.f_score = f_score
            existing.computed_at = datetime.utcnow()
        else:
            metrics = ProcessModelMetrics(
                id=str(uuid4()),
                model_id=model_id,
                dataset_id=dataset_id,
                fitness=fitness,
                precision=precision,
                generalization=generalization,
                simplicity=simplicity,
                f_score=f_score,
            )
            db.add(metrics)
        
        # Update quick metrics on model
        model_query = select(ProcessModel).where(ProcessModel.id == model_id)
        model_result = await db.execute(model_query)
        model = model_result.scalar_one_or_none()
        if model:
            model.fitness = fitness
            model.precision = precision
        
        await db.commit()
        
        return {"stored": True, "model_id": model_id}
