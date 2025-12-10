"""
Search i Filter operacije na grafu.
"""
import re
from typing import Set, List
from api.models.graph import Graph
from api.models.node import Node
from api.types import TypeValidator, ValueType


class GraphSearch:
    """Pretraga čvorova grafa po tekstualnom upitu"""

    @staticmethod
    def search(graph: Graph, query: str) -> Graph:
        """
        Pretraži čvorove po tekstualnom upitu.
        Vraća podgraf sa čvorovima čiji atributi sadrže upit (case-insensitive).

        Args:
            graph: Graf za pretragu
            query: Tekstualni upit

        Returns:
            Podgraf sa pronađenim čvorovima
        """
        if not query or not query.strip():
            return graph

        matching_nodes = set()

        for node in graph.get_all_nodes():
            if node.contains_in_attributes(query):
                matching_nodes.add(node.node_id)

        return graph.get_subgraph_by_nodes(matching_nodes)


class FilterCondition:
    """Predstavlja jednu filter uslov"""

    def __init__(self, attribute: str, operator: str, value: str):
        """
        Args:
            attribute: Naziv atributa
            operator: Komparator (==, !=, <, <=, >, >=)
            value: Vrednost za poređenje
        """
        self.attribute = attribute
        self.operator = operator
        self.value = value

    def evaluate(self, node: Node) -> bool:
        """Proceni da li čvor zadovoljava uslov"""
        node_value = node.get_attribute(self.attribute)

        if node_value is None:
            return False

        # Konvertuj vrednost u tip čvora za ispravno poređenje
        try:
            node_type = node.get_attribute_type(self.attribute)
            converted_filter_value = TypeValidator.validate_and_convert(
                self.value, node_type
            )
            return TypeValidator.compare(node_value, converted_filter_value, self.operator)
        except (ValueError, TypeError):
            return False


class GraphFilter:
    """Filtriranje čvorova grafa"""

    # Regex za parsiranje filter izraza: attribute operator value
    FILTER_PATTERN = re.compile(r'(\w+)\s*(==|!=|<=|>=|<|>)\s*(.+)')

    @staticmethod
    def parse_filter_expression(expression: str) -> List[FilterCondition]:
        """
        Parsiraj filter izraz.
        Format: attribute operator value
        Primeri: age > 30, name == John

        Args:
            expression: Filter izraz

        Returns:
            Lista FilterCondition objekata
        """
        conditions = []

        # Podeli izraz po '&&' i '||' (za sada samo &&)
        parts = expression.split('&&')

        for part in parts:
            part = part.strip()
            match = GraphFilter.FILTER_PATTERN.match(part)

            if not match:
                raise ValueError(f"Invalid filter expression: {part}")

            attribute, operator, value = match.groups()
            conditions.append(FilterCondition(attribute, operator, value.strip()))

        return conditions

    @staticmethod
    def filter(graph: Graph, filter_expression: str) -> Graph:
        """
        Filtrira čvorove grafa prema izrazu.
        Vraća podgraf sa čvorovima koji zadovoljavaju filter.

        Args:
            graph: Graf za filtriranje
            filter_expression: Filter izraz (npr: "age > 30 && name == John")

        Returns:
            Podgraf sa filtriranim čvorovima
        """
        if not filter_expression or not filter_expression.strip():
            return graph

        try:
            conditions = GraphFilter.parse_filter_expression(filter_expression)
        except ValueError as e:
            raise ValueError(f"Filter error: {str(e)}")

        matching_nodes = set()

        for node in graph.get_all_nodes():
            # Svi uslovi moraju biti ispunjeni (AND logika)
            if all(condition.evaluate(node) for condition in conditions):
                matching_nodes.add(node.node_id)

        return graph.get_subgraph_by_nodes(matching_nodes)