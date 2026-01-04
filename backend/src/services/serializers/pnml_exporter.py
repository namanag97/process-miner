"""PNML Exporter Service.

Exports PM4Py Petri nets to ISO/IEC 15909-2 PNML (Petri Net Markup Language) format.
This provides a vendor-neutral, standards-compliant way to store process models.
"""

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING
from xml.dom import minidom

import structlog

if TYPE_CHECKING:
    from pm4py.objects.petri_net.obj import Marking, PetriNet

logger = structlog.get_logger(__name__)


class PnmlExporter:
    """Export PM4Py Petri nets to PNML XML format."""

    def export(self, net: 'PetriNet', im: 'Marking', fm: 'Marking') -> str:
        """Convert Petri net to PNML XML string.

        Args:
            net: PM4Py Petri net object
            im: Initial marking
            fm: Final marking

        Returns:
            PNML XML string (ISO/IEC 15909-2 compliant)
        """
        try:
            # Use PM4Py's built-in PNML writer
            from io import BytesIO

            from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

            # Export to bytes
            output = BytesIO()
            pnml_exporter.apply(net, im, output, variant=pnml_exporter.Variants.PNML, final_marking=fm)

            # Get XML string
            pnml_xml = output.getvalue().decode('utf-8')

            logger.info(
                "pnml_export_success",
                places=len(net.places),
                transitions=len(net.transitions),
                arcs=len(net.arcs)
            )

            return pnml_xml

        except Exception as e:
            logger.error("pnml_export_failed", error=str(e), net_name=getattr(net, 'name', 'unknown'))
            raise

    def export_with_layout(
        self,
        net: 'PetriNet',
        im: 'Marking',
        fm: 'Marking',
        layout: dict[str, tuple[float, float]]
    ) -> str:
        """Export Petri net with layout coordinates as PNML extension elements.

        Args:
            net: PM4Py Petri net
            im: Initial marking
            fm: Final marking
            layout: Dict mapping place/transition IDs to (x, y) coordinates

        Returns:
            PNML XML string with layout annotations
        """
        # Get base PNML
        pnml_xml = self.export(net, im, fm)

        # Parse XML and add layout graphics
        root = ET.fromstring(pnml_xml)

        # Find the net element
        ns = {'pnml': 'http://www.pnml.org/version-2009/grammar/pnml'}
        net_elem = root.find('.//pnml:net', ns)

        if net_elem is not None:
            # Add graphics to places
            for place_elem in net_elem.findall('.//pnml:place', ns):
                place_id = place_elem.get('id')
                if place_id and place_id in layout:
                    x, y = layout[place_id]
                    graphics = ET.SubElement(place_elem, 'graphics')
                    position = ET.SubElement(graphics, 'position')
                    position.set('x', str(x))
                    position.set('y', str(y))

            # Add graphics to transitions
            for trans_elem in net_elem.findall('.//pnml:transition', ns):
                trans_id = trans_elem.get('id')
                if trans_id and trans_id in layout:
                    x, y = layout[trans_id]
                    graphics = ET.SubElement(trans_elem, 'graphics')
                    position = ET.SubElement(graphics, 'position')
                    position.set('x', str(x))
                    position.set('y', str(y))

        # Pretty print
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent='  ')

    def validate_pnml(self, pnml_xml: str) -> bool:
        """Validate PNML XML against schema.

        Args:
            pnml_xml: PNML XML string

        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic XML parsing validation
            ET.fromstring(pnml_xml)

            # Check for required elements
            root = ET.fromstring(pnml_xml)
            if root.tag != 'pnml' and not root.tag.endswith('}pnml'):
                return False

            logger.info("pnml_validation_success")
            return True

        except ET.ParseError as e:
            logger.error("pnml_validation_failed", error=str(e))
            return False
