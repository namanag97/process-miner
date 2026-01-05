"""Process Visualization Service - Generate visualizations for process models.

Contains SVG generation for Petri nets, DFGs, and other model types.
"""

from typing import Any

import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer

from src.platform.core.enums import ModelFormat
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class VisualizationService:
    """Generates visualizations for process models."""

    def visualize_petri_net(
        self,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> bytes:
        """Generate SVG visualization of Petri net.

        Args:
            net: PM4Py PetriNet object
            im: Initial marking
            fm: Final marking

        Returns:
            SVG bytes
        """
        gviz = pn_visualizer.apply(net, im, fm)
        return pn_visualizer.serialize(gviz)

    def visualize_dfg(
        self,
        dfg: dict,
        start_activities: dict,
        end_activities: dict,
    ) -> bytes:
        """Generate SVG visualization of DFG.

        Args:
            dfg: Directly-follows graph dict
            start_activities: Start activity frequencies
            end_activities: End activity frequencies

        Returns:
            SVG bytes
        """
        gviz = dfg_visualizer.apply(dfg, activities_count=start_activities)
        return dfg_visualizer.serialize(gviz)

    def visualize_model(
        self,
        model_data: Any,
        model_format: ModelFormat,
    ) -> bytes:
        """Generate visualization for any model type.

        Args:
            model_data: The model data from discovery
            model_format: The format of the model

        Returns:
            SVG bytes

        Raises:
            ValueError: If visualization not supported for format
        """
        if model_format == ModelFormat.PETRI_NET:
            net, im, fm = model_data
            return self.visualize_petri_net(net, im, fm)

        if model_format == ModelFormat.PROCESS_TREE:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
            return self.visualize_petri_net(net, im, fm)

        if model_format == ModelFormat.DFG:
            dfg, start, end = model_data
            return self.visualize_dfg(dfg, start, end)

        raise ValueError(f"Visualization not supported for: {model_format}")


# Singleton instance
visualization_service = VisualizationService()
