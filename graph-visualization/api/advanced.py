"""
Napredne karakteristike - opciono za maks bodove
"""
from typing import Dict, List, Set, Tuple
from api.models.graph import Graph
from api.models.node import Node


class GraphAnalyzer:
    """Analiza grafova - pronalaženje putanja, ciklusa, komponenti"""

    @staticmethod
    def find_shortest_path(graph: Graph, start_node_id: str, end_node_id: str) -> List[str]:
        """Pronađi najkraću putanju između dva čvora (BFS)"""
        from collections import deque

        visited = set()
        queue = deque([(start_node_id, [start_node_id])])

        while queue:
            current_id, path = queue.popleft()

            if current_id == end_node_id:
                return path

            if current_id in visited:
                continue

            visited.add(current_id)

            current_node = graph.get_node(current_id)
            if current_node:
                for neighbor in graph.get_neighbors(current_node):
                    if neighbor.node_id not in visited:
                        queue.append((neighbor.node_id, path + [neighbor.node_id]))

        return []

    @staticmethod
    def find_all_cycles(graph: Graph) -> List[List[str]]:
        """Pronađi sve cikluse u grafu"""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node_id: str, start_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)

            node = graph.get_node(node_id)
            if node:
                for edge in graph.get_outgoing_edges(node):
                    neighbor_id = edge.target_node.node_id

                    if neighbor_id == start_id and len(path) > 2:
                        cycles.append(path.copy())
                    elif neighbor_id not in visited:
                        dfs(neighbor_id, start_id)

            path.pop()
            rec_stack.remove(node_id)

        for node in graph.get_all_nodes():
            if node.node_id not in visited:
                dfs(node.node_id, node.node_id)

        return cycles

    @staticmethod
    def get_connected_components(graph: Graph) -> List[Set[str]]:
        """Pronađi sve povezane komponente"""
        visited = set()
        components = []

        def dfs(node_id: str, component: Set[str]):
            visited.add(node_id)
            component.add(node_id)

            node = graph.get_node(node_id)
            if node:
                for neighbor in graph.get_neighbors(node):
                    if neighbor.node_id not in visited:
                        dfs(neighbor.node_id, component)

        for node in graph.get_all_nodes():
            if node.node_id not in visited:
                component = set()
                dfs(node.node_id, component)
                components.append(component)

        return components

    @staticmethod
    def get_node_degree(graph: Graph, node_id: str) -> Tuple[int, int]:
        """Uzmi in-degree i out-degree čvora"""
        node = graph.get_node(node_id)
        if not node:
            return 0, 0

        in_degree = len(graph.get_incoming_edges(node))
        out_degree = len(graph.get_outgoing_edges(node))

        return in_degree, out_degree

    @staticmethod
    def get_centrality_nodes(graph: Graph) -> List[Tuple[str, int]]:
        """Pronađi čvorove sa najvećom centralnosti (po broju grana)"""
        centrality = []

        for node in graph.get_all_nodes():
            in_d, out_d = GraphAnalyzer.get_node_degree(graph, node.node_id)
            total_degree = in_d + out_d
            centrality.append((node.node_id, total_degree))

        return sorted(centrality, key=lambda x: x[1], reverse=True)


class GraphExporter:
    """Izvoz grafa u različite formate"""

    @staticmethod
    def to_adjacency_matrix(graph: Graph) -> Tuple[List[List[int]], List[str]]:
        """Konvertuj graf u adjcentnu matricu"""
        nodes = graph.get_all_nodes()
        node_ids = [node.node_id for node in nodes]
        n = len(nodes)

        matrix = [[0] * n for _ in range(n)]

        node_id_to_index = {node_id: i for i, node_id in enumerate(node_ids)}

        for edge in graph.get_all_edges():
            source_idx = node_id_to_index[edge.source_node.node_id]
            target_idx = node_id_to_index[edge.target_node.node_id]
            matrix[source_idx][target_idx] = 1

            if edge.direction.value == 'undirected':
                matrix[target_idx][source_idx] = 1

        return matrix, node_ids

    @staticmethod
    def to_edge_list(graph: Graph) -> str:
        """Konvertuj graf u edge list format"""
        lines = []

        for edge in graph.get_all_edges():
            line = f"{edge.source_node.node_id} {edge.target_node.node_id} {edge.direction.value}"
            lines.append(line)

        return "\n".join(lines)

    @staticmethod
    def to_gexf(graph: Graph) -> str:
        """Konvertuj graf u GEXF format (za Gephi)"""
        gexf = '<?xml version="1.0" encoding="UTF-8"?>\n'
        gexf += '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n'
        gexf += '  <graph mode="static" defaultedgetype="directed">\n'

        # Dodaj čvorove
        gexf += '    <nodes>\n'
        for node in graph.get_all_nodes():
            label = node.get_attribute('name') or node.node_id
            gexf += f'      <node id="{node.node_id}" label="{label}"/>\n'
        gexf += '    </nodes>\n'

        # Dodaj grane
        gexf += '    <edges>\n'
        for i, edge in enumerate(graph.get_all_edges()):
            gexf += f'      <edge id="{i}" source="{edge.source_node.node_id}" target="{edge.target_node.node_id}"/>\n'
        gexf += '    </edges>\n'

        gexf += '  </graph>\n'
        gexf += '</gexf>'

        return gexf


class GraphStatistics:
    """Statistika grafa"""

    @staticmethod
    def get_statistics(graph: Graph) -> Dict:
        """Uzmi sve statistike grafa"""
        nodes = graph.get_all_nodes()
        edges = graph.get_all_edges()

        degrees = [GraphAnalyzer.get_node_degree(graph, n.node_id) for n in nodes]

        avg_degree = sum(in_d + out_d for in_d, out_d in degrees) / len(degrees) if nodes else 0
        max_degree = max((in_d + out_d for in_d, out_d in degrees), default=0)

        components = GraphAnalyzer.get_connected_components(graph)

        return {
            'num_nodes': len(nodes),
            'num_edges': len(edges),
            'num_components': len(components),
            'avg_degree': avg_degree,
            'max_degree': max_degree,
            'is_cyclic': graph.has_cycle(),
            'density': (2 * len(edges)) / (len(nodes) * (len(nodes) - 1)) if len(nodes) > 1 else 0,
        }

    @staticmethod
    def get_attribute_statistics(graph: Graph, attribute: str) -> Dict:
        """Uzmi statistiku za specifičan atribut"""
        values = []

        for node in graph.get_all_nodes():
            val = node.get_attribute(attribute)
            if val is not None:
                try:
                    values.append(float(val) if isinstance(val, (int, float)) else val)
                except (ValueError, TypeError):
                    pass

        if not values:
            return {'count': 0}

        numeric_values = [v for v in values if isinstance(v, (int, float))]

        stats = {
            'count': len(values),
            'unique': len(set(values)),
        }

        if numeric_values:
            stats['min'] = min(numeric_values)
            stats['max'] = max(numeric_values)
            stats['avg'] = sum(numeric_values) / len(numeric_values)

        return stats