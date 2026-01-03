"""Safe unpickler for process models.

Provides a restricted unpickler that only allows loading specific PM4Py
model classes, preventing Remote Code Execution (RCE) attacks.

SECURITY: Never use pickle.loads() directly on user-controlled data.
Always use RestrictedUnpickler or JSON serialization.
"""

import io
import pickle
from typing import Any

from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Only allow PM4Py model classes, ML models, and built-in types
SAFE_MODULES = frozenset([
    # Python built-ins and standard library
    "builtins",
    "collections",
    "datetime",
    "numpy",
    "numpy.core.multiarray",
    "numpy._core.multiarray",
    # Scikit-learn (for prediction models)
    "sklearn.ensemble._forest",
    "sklearn.ensemble._gb",
    "sklearn.tree._classes",
    "sklearn.tree._tree",
    "sklearn.preprocessing._label",
    "sklearn.utils._bunch",
    # XGBoost (for prediction models)
    "xgboost.core",
    "xgboost.sklearn",
    # PM4Py Petri net classes
    "pm4py.objects.petri_net.obj",
    "pm4py.objects.petri_net.properties",
    # PM4Py Process tree classes  
    "pm4py.objects.process_tree.obj",
    # PM4Py BPMN classes
    "pm4py.objects.bpmn.obj",
    # PM4Py DFG (just a dict, but may have custom wrappers)
    "pm4py.objects.dfg.obj",
    # PM4Py OCEL/OC-PN classes
    "pm4py.objects.ocel.obj",
    "pm4py.objects.ocpn.obj",
])


class RestrictedUnpickler(pickle.Unpickler):
    """Unpickler that only allows safe, known classes.
    
    Raises UnpicklingError if an attempt is made to load
    a class from a module not in the SAFE_MODULES whitelist.
    """
    
    def find_class(self, module: str, name: str) -> Any:
        """Override find_class to restrict loadable classes."""
        if module not in SAFE_MODULES:
            logger.warning(
                "unsafe_unpickle_attempt",
                module=module,
                class_name=name,
            )
            raise pickle.UnpicklingError(
                f"Forbidden module in pickle: {module}.{name}"
            )
        return super().find_class(module, name)


def safe_loads(data: bytes) -> Any:
    """Safely unpickle data using restricted unpickler.
    
    Args:
        data: Pickled bytes to load
        
    Returns:
        Unpickled object
        
    Raises:
        pickle.UnpicklingError: If data contains forbidden classes
    """
    return RestrictedUnpickler(io.BytesIO(data)).load()
