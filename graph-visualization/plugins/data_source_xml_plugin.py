"""
XML Data Source Plugin
Parsira XML podatke i kreira graf
"""
import xml.etree.ElementTree as ET
import uuid
from typing import Dict, Set
from api import DataSourcePlugin, Graph, Node, Edge, EdgeDirection


class XMLNode(Node):
    """Konkretna implementacija Node klase"""
    pass


class XMLDataSourcePlugin(DataSourcePlugin):
    """Plugin za parsiranje XML podataka"""

    def get_plugin_name(self) -> str:
        return "XML Parser"

    def get_required_parameters(self) -> Dict[str, str]:
        return {
            'file_path': 'Path to XML file (e.g., company_structure.xml)',
        }

    def parse(self, **kwargs) -> Graph:
        """
        Parsiraj XML fajl i kreiraj graf

        Svaki XML element postaje čvor.
        Parent-child relacije postaju grane.
        """
        file_path = kwargs.get('file_path')

        if not file_path:
            raise ValueError("file_path is required")

        tree = ET.parse(file_path)
        root = tree.getroot()

        print(f"🔍 XML Parser: Processing {root.tag}")

        graph = Graph("xml_graph")
        processed_elements: Set[str] = set()

        # Rekurzivno procesuiraj sve elemente
        self._process_element(root, graph, processed_elements, parent_id=None)

        print(f"✓ Parsed XML graph: {graph.get_number_of_nodes()} nodes, {graph.get_number_of_edges()} edges")

        return graph

    def _process_element(self, element, graph, processed, parent_id=None):
        """Rekurzivno procesuiraj XML element i njegovu decu"""

        # Generiši unique ID za element
        element_id = element.get('id')
        if not element_id:
            element_id = f"{element.tag}_{str(uuid.uuid4())[:8]}"

        element_id = str(element_id)

        # Kreiraj čvor ako već ne postoji
        if element_id not in processed:
            processed.add(element_id)

            # Pripremi atribute
            attributes = {'tag': element.tag}
            attributes.update(dict(element.attrib))

            # Dodaj text sadržaj ako postoji
            if element.text and element.text.strip():
                attributes['text'] = element.text.strip()

            # Dodaj child text vrednosti (ako nemaju svoju decu)
            for child in element:
                if len(list(child)) == 0 and child.text and child.text.strip():
                    attributes[child.tag] = child.text.strip()

            # Kreiraj čvor
            node = XMLNode(element_id, **attributes)
            graph.add_node(node)

            # Kreiraj granu od parent-a
            if parent_id:
                parent_node = graph.get_node(parent_id)
                child_node = graph.get_node(element_id)

                if parent_node and child_node:
                    edge = Edge(
                        str(uuid.uuid4()),
                        parent_node,
                        child_node,
                        EdgeDirection.DIRECTED
                    )
                    graph.add_edge(edge)

        # Rekurzivno procesuiraj svu decu koja imaju svoju decu (strukture)
        for child in element:
            # Samo procesuiraj elemente koji imaju decu ili atribute (nisu samo text)
            if len(list(child)) > 0 or child.attrib:
                self._process_element(child, graph, processed, parent_id=element_id)