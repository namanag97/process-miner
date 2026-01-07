"""Model Import Service - Import reference models from PNML, BPMN, etc.

Implements Phase 11.1 - Reference Model Management.
Allows importing external process models for conformance checking.
"""

import xml.etree.ElementTree as ET

import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.petri_net.obj import Marking, PetriNet

from src.features.process_mining.enums import ModelFormat
from src.infra.core.exceptions import ValidationError
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


class ModelImporter:
    """Service for importing process models from various formats."""

    def import_pnml(self, pnml_content: str) -> tuple[PetriNet, Marking, Marking]:
        """Import a Petri net from PNML XML format.

        Args:
            pnml_content: PNML XML string

        Returns:
            Tuple of (net, initial_marking, final_marking)

        Raises:
            ValidationError: If PNML is invalid or cannot be parsed
        """
        logger.info("pnml_import_started", content_length=len(pnml_content))

        try:
            # PM4Py can import PNML from file or string
            import tempfile
            from pathlib import Path

            # Write to temp file for PM4Py
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".pnml", delete=False, encoding="utf-8"
            ) as f:
                f.write(pnml_content)
                temp_path = f.name

            try:
                # Import using PM4Py
                net, initial_marking, final_marking = pm4py.read_pnml(temp_path)

                # Validate the imported model
                self._validate_petri_net(net, initial_marking, final_marking)

                logger.info(
                    "pnml_import_success",
                    places=len(net.places),
                    transitions=len(net.transitions),
                    arcs=len(net.arcs),
                )

                return net, initial_marking, final_marking

            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error("pnml_import_failed", error=str(e))
            raise ValidationError(
                f"Failed to import PNML: {e!s}. Ensure the file is valid PNML format."
            ) from e

    def import_bpmn(self, bpmn_content: str) -> BPMN:
        """Import a BPMN model from BPMN 2.0 XML format.

        Args:
            bpmn_content: BPMN XML string

        Returns:
            BPMN object

        Raises:
            ValidationError: If BPMN is invalid or cannot be parsed
        """
        logger.info("bpmn_import_started", content_length=len(bpmn_content))

        try:
            import tempfile
            from pathlib import Path

            # Write to temp file for PM4Py
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".bpmn", delete=False, encoding="utf-8"
            ) as f:
                f.write(bpmn_content)
                temp_path = f.name

            try:
                # Import using PM4Py
                bpmn_graph = pm4py.read_bpmn(temp_path)

                # Validate the BPMN
                self._validate_bpmn(bpmn_graph)

                logger.info(
                    "bpmn_import_success",
                    nodes=len(bpmn_graph.get_nodes()) if hasattr(bpmn_graph, "get_nodes") else 0,
                    flows=len(bpmn_graph.get_flows()) if hasattr(bpmn_graph, "get_flows") else 0,
                )

                return bpmn_graph

            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error("bpmn_import_failed", error=str(e))
            raise ValidationError(
                f"Failed to import BPMN: {e!s}. Ensure the file is valid BPMN 2.0 format."
            ) from e

    def bpmn_to_petri_net(self, bpmn: BPMN) -> tuple[PetriNet, Marking, Marking]:
        """Convert BPMN to Petri net.

        Args:
            bpmn: BPMN object

        Returns:
            Tuple of (net, initial_marking, final_marking)

        Raises:
            ValidationError: If conversion fails
        """
        logger.info("bpmn_conversion_started")

        try:
            # PM4Py converts BPMN to Petri net
            net, initial_marking, final_marking = pm4py.convert_to_petri_net(bpmn)

            # Validate the converted model
            self._validate_petri_net(net, initial_marking, final_marking)

            logger.info(
                "bpmn_conversion_success",
                places=len(net.places),
                transitions=len(net.transitions),
            )

            return net, initial_marking, final_marking

        except Exception as e:
            logger.error("bpmn_conversion_failed", error=str(e))
            raise ValidationError(f"Failed to convert BPMN to Petri net: {e!s}") from e

    def import_and_convert_bpmn(self, bpmn_content: str) -> tuple[PetriNet, Marking, Marking]:
        """Import BPMN and convert to Petri net in one step.

        Args:
            bpmn_content: BPMN XML string

        Returns:
            Tuple of (net, initial_marking, final_marking)
        """
        bpmn = self.import_bpmn(bpmn_content)
        return self.bpmn_to_petri_net(bpmn)

    def serialize_petri_net(self, net: PetriNet, im: Marking, fm: Marking) -> bytes:
        """Serialize a Petri net to bytes using joblib.

        Args:
            net: Petri net
            im: Initial marking
            fm: Final marking

        Returns:
            Serialized bytes
        """
        import io

        import joblib

        buffer = io.BytesIO()
        joblib.dump((net, im, fm), buffer)
        return buffer.getvalue()

    def validate_model_format(self, content: str) -> ModelFormat:
        """Auto-detect model format from XML content.

        Args:
            content: XML string

        Returns:
            ModelFormat enum value

        Raises:
            ValidationError: If format cannot be detected
        """
        try:
            root = ET.fromstring(content)
            tag_lower = root.tag.lower()

            # Check for PNML
            if "pnml" in tag_lower or root.tag.endswith("pnml"):
                return ModelFormat.PETRI_NET

            # Check for BPMN
            if "bpmn" in tag_lower or "definitions" in tag_lower:
                return ModelFormat.BPMN

            raise ValidationError(
                f"Unknown model format. Root tag: {root.tag}. Expected PNML or BPMN."
            )

        except ET.ParseError as e:
            raise ValidationError(f"Invalid XML: {e!s}") from e

    def _validate_petri_net(
        self, net: PetriNet, initial_marking: Marking, final_marking: Marking
    ) -> None:
        """Validate a Petri net.

        Args:
            net: Petri net
            initial_marking: Initial marking
            final_marking: Final marking

        Raises:
            ValidationError: If validation fails
        """
        # Check basic structure
        if not net.places:
            raise ValidationError("Petri net has no places")

        if not net.transitions:
            raise ValidationError("Petri net has no transitions")

        # Check markings reference valid places
        if initial_marking:
            invalid_places = [p for p in initial_marking if p not in net.places]
            if invalid_places:
                raise ValidationError(
                    f"Initial marking references invalid places: {invalid_places}"
                )

        if final_marking:
            invalid_places = [p for p in final_marking if p not in net.places]
            if invalid_places:
                raise ValidationError(f"Final marking references invalid places: {invalid_places}")

        logger.info(
            "petri_net_validation_passed",
            places=len(net.places),
            transitions=len(net.transitions),
            arcs=len(net.arcs),
        )

    def _validate_bpmn(self, bpmn: BPMN) -> None:
        """Validate a BPMN model.

        Args:
            bpmn: BPMN object

        Raises:
            ValidationError: If validation fails
        """
        # Basic validation - check it has nodes
        if hasattr(bpmn, "get_nodes"):
            nodes = bpmn.get_nodes()
            if not nodes:
                raise ValidationError("BPMN model has no nodes")

        logger.info("bpmn_validation_passed")


# Singleton instance
model_importer = ModelImporter()
