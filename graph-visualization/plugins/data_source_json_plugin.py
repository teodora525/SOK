"""
JSON Data Source Plugin
Parsira JSON podatke i kreira graf
"""
import json
import uuid
from typing import Dict, Any, Set
from api import DataSourcePlugin, Graph, Node, Edge, EdgeDirection


class JSONNode(Node):
    """Konkretna implementacija Node klase"""
    pass


class JSONDataSourcePlugin(DataSourcePlugin):
    """Plugin za parsiranje JSON podataka"""

    def get_plugin_name(self) -> str:
        return "JSON Parser"

    def get_required_parameters(self) -> Dict[str, str]:
        return {
            'file_path': 'Path to JSON file',
            'id_field': 'Field name for node ID (default: id)',
            'children_field': 'Field name for children/references (default: children)'
        }

    def parse(self, **kwargs) -> Graph:
        """
        Parsiraj JSON fajl i kreiraj graf

        JSON format:
        {
            "id": "1",
            "name": "John",
            "age": 30,
            "children": [
                {"id": "2", "name": "Jane", ...}
            ]
        }
        """
        file_path = kwargs.get('file_path')
        id_field = kwargs.get('id_field', 'id')
        children_field = kwargs.get('children_field', 'children')

        if not file_path:
            raise ValueError("file_path is required")

        # Učitaj JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Kreiraj graf
        graph = Graph("json_graph")
        processed_ids: Set[str] = set()

        # Prvo prosledi - kreiraj čvorove
        self._create_nodes_first_pass(
            data if isinstance(data, list) else [data],
            graph,
            processed_ids,
            id_field,
            children_field
        )

        # Drugo prosledi - kreiraj grane
        self._create_edges_second_pass(
            data if isinstance(data, list) else [data],
            graph,
            id_field,
            children_field,
            None  # Početni parent_id je None
        )

        # DEBUG
        print(f"✓ Parsed JSON graph: {graph.get_number_of_nodes()} nodes, {graph.get_number_of_edges()} edges")

        return graph

    def _create_nodes_first_pass(
            self,
            items: list,
            graph: Graph,
            processed_ids: Set[str],
            id_field: str,
            children_field: str
    ) -> None:
        """Prvo prosledi - kreiraj čvorove"""
        for item in items:
            if not isinstance(item, dict):
                continue

            node_id = str(item.get(id_field, str(uuid.uuid4())))

            if node_id in processed_ids:
                continue

            processed_ids.add(node_id)

            # Kreiraj čvor sa svim atributima osim children
            attributes = {
                k: v for k, v in item.items()
                if k != children_field and not isinstance(v, (dict, list))
            }

            node = JSONNode(node_id, **attributes)
            graph.add_node(node)

            # Rekurzivno procesuiraj decu
            if children_field in item and isinstance(item[children_field], list):
                self._create_nodes_first_pass(
                    item[children_field],
                    graph,
                    processed_ids,
                    id_field,
                    children_field
                )

    def _create_edges_second_pass(
            self,
            items: list,
            graph: Graph,
            id_field: str,
            children_field: str,
            parent_id: str = None
    ) -> None:
        """Drugo prosledi - kreiraj grane"""
        for item in items:
            if not isinstance(item, dict):
                continue

            node_id = str(item.get(id_field, ""))

            # Kreiraj granu od roditelja ka detetu
            if parent_id and parent_id != node_id:
                source_node = graph.get_node(parent_id)
                target_node = graph.get_node(node_id)

                if source_node and target_node:
                    try:
                        edge = Edge(
                            str(uuid.uuid4()),
                            source_node,
                            target_node,
                            EdgeDirection.DIRECTED
                        )
                        graph.add_edge(edge)
                        print(f"✓ Created edge: {parent_id} -> {node_id}")
                    except Exception as e:
                        print(f"✗ Error adding edge {parent_id} -> {node_id}: {e}")

            # Rekurzivno procesuiraj decu - VAŽNO: prosleđujem node_id kao parent!
            if children_field in item and isinstance(item[children_field], list):
                self._create_edges_second_pass(
                    item[children_field],
                    graph,
                    id_field,
                    children_field,
                    node_id  # ← OVAJ node_id postaje parent za njegovu decu!
                )