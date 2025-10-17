"""
Graph model - kompletan model grafa.
Podrška za directed/undirected, cyclic/acyclic grafove.
"""
from typing import Dict, List, Set, Optional, Tuple
from copy import deepcopy
from api.models.node import Node
from api.models.edge import Edge, EdgeDirection


class Graph:
    """
    Klasa za reprezentaciju grafa.
    Podržava directed, undirected, cyclic, acyclic grafove.
    """

    def __init__(self, graph_id: str):
        """
        Inicijalizuj graf.

        Args:
            graph_id: Jedinstveni identifikator grafa
        """
        self.graph_id = graph_id
        self.nodes: Dict[str, Node] = {}  # node_id -> Node
        self.edges: Dict[str, Edge] = {}  # edge_id -> Edge
        self._adjacency_list: Dict[str, List[Edge]] = {}  # node_id -> [Edges]

    def add_node(self, node: Node) -> None:
        """Dodaj čvor u graf"""
        if node.node_id in self.nodes:
            raise ValueError(f"Node with id {node.node_id} already exists")

        self.nodes[node.node_id] = node
        self._adjacency_list[node.node_id] = []

    def add_edge(self, edge: Edge) -> None:
        """Dodaj granu u graf"""
        # Provera da li postoje oba čvora
        if edge.source_node.node_id not in self.nodes:
            raise ValueError(f"Source node {edge.source_node.node_id} not in graph")
        if edge.target_node.node_id not in self.nodes:
            raise ValueError(f"Target node {edge.target_node.node_id} not in graph")

        if edge.edge_id in self.edges:
            raise ValueError(f"Edge with id {edge.edge_id} already exists")

        self.edges[edge.edge_id] = edge

        # Dodaj u adjacency list
        self._adjacency_list[edge.source_node.node_id].append(edge)

        if edge.direction == EdgeDirection.UNDIRECTED:
            self._adjacency_list[edge.target_node.node_id].append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        """Uzmi čvor po ID-u"""
        return self.nodes.get(node_id)

    def get_edge(self, edge_id: str) -> Optional[Edge]:
        """Uzmi granu po ID-u"""
        return self.edges.get(edge_id)

    def get_all_nodes(self) -> List[Node]:
        """Uzmi sve čvorove"""
        return list(self.nodes.values())

    def get_all_edges(self) -> List[Edge]:
        """Uzmi sve grane"""
        return list(self.edges.values())

    def get_neighbors(self, node: Node) -> List[Node]:
        """Uzmi sve susedne čvorove"""
        neighbors = set()
        for edge in self._adjacency_list.get(node.node_id, []):
            if edge.source_node == node:
                neighbors.add(edge.target_node)
            else:
                neighbors.add(edge.source_node)
        return list(neighbors)

    def get_outgoing_edges(self, node: Node) -> List[Edge]:
        """Uzmi sve odlazne grane iz čvora"""
        return [
            edge for edge in self._adjacency_list.get(node.node_id, [])
            if edge.source_node == node
        ]

    def get_incoming_edges(self, node: Node) -> List[Edge]:
        """Uzmi sve dolazne grane u čvor"""
        return [
            edge for edge in self._adjacency_list.get(node.node_id, [])
            if edge.target_node == node
        ]

    def remove_node(self, node_id: str) -> None:
        """
        Obriši čvor iz grafa.
        Prvo brišu sve grane vezane za čvor.
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not in graph")

        node = self.nodes[node_id]

        # Obriši sve grane vezane za čvor
        edges_to_delete = []
        for edge in self._adjacency_list.get(node_id, []):
            edges_to_delete.append(edge.edge_id)

        # Ako je grana neusmeren, obriši je iz oba čvora
        for edge_id in edges_to_delete:
            edge = self.edges[edge_id]
            other_node_id = None
            if edge.source_node.node_id == node_id:
                other_node_id = edge.target_node.node_id
            else:
                other_node_id = edge.source_node.node_id

            del self.edges[edge_id]
            if node_id in self._adjacency_list:
                self._adjacency_list[node_id] = [
                    e for e in self._adjacency_list[node_id] if e.edge_id != edge_id
                ]
            if other_node_id in self._adjacency_list:
                self._adjacency_list[other_node_id] = [
                    e for e in self._adjacency_list[other_node_id] if e.edge_id != edge_id
                ]

        # Obriši čvor
        del self.nodes[node_id]
        del self._adjacency_list[node_id]

    def remove_edge(self, edge_id: str) -> None:
        """Obriši granu iz grafa"""
        if edge_id not in self.edges:
            raise ValueError(f"Edge {edge_id} not in graph")

        edge = self.edges[edge_id]

        # Obriši iz adjacency liste
        source_id = edge.source_node.node_id
        target_id = edge.target_node.node_id

        self._adjacency_list[source_id] = [
            e for e in self._adjacency_list[source_id] if e.edge_id != edge_id
        ]
        self._adjacency_list[target_id] = [
            e for e in self._adjacency_list[target_id] if e.edge_id != edge_id
        ]

        del self.edges[edge_id]

    def has_cycle(self) -> bool:
        """Provera da li graf ima ciklus"""
        visited = set()
        rec_stack = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            node = self.nodes[node_id]
            for edge in self.get_outgoing_edges(node):
                neighbor_id = edge.target_node.node_id

                if neighbor_id not in visited:
                    if dfs(neighbor_id):
                        return True
                elif neighbor_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if dfs(node_id):
                    return True

        return False

    def get_subgraph_by_nodes(self, node_ids: Set[str]) -> 'Graph':
        """
        Kreiraj podgraf sa specificiranim čvorovima.
        Grane su uključene samo ako oba čvora postoje u podgrafu.
        """
        subgraph = Graph(f"{self.graph_id}_sub")

        # Dodaj čvorove
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph.add_node(self.nodes[node_id])

        # Dodaj grane
        for edge in self.edges.values():
            if edge.source_node.node_id in node_ids and \
                    edge.target_node.node_id in node_ids:
                subgraph.add_edge(edge)

        return subgraph

    def get_number_of_nodes(self) -> int:
        """Broj čvorova"""
        return len(self.nodes)

    def get_number_of_edges(self) -> int:
        """Broj grana"""
        return len(self.edges)

    def __repr__(self) -> str:
        """String reprezentacija grafa"""
        return f"Graph({self.graph_id}, nodes={len(self.nodes)}, edges={len(self.edges)})"

    def to_dict(self) -> Dict:
        """Konvertuj graf u rečnik"""
        return {
            'id': self.graph_id,
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges.values()]
        }