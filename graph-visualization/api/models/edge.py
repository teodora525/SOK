"""
Edge model - reprezentacija grane između čvorova.
"""
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from api.types import ValueType, TypeValidator
from api.models.node import Node


class EdgeDirection(Enum):
    """Tip usmeravanja grane"""
    DIRECTED = "directed"
    UNDIRECTED = "undirected"


class Edge:
    """
    Klasa za granu između dva čvora.
    Grana može biti usmeren ili neusmeren.
    """

    def __init__(
            self,
            edge_id: str,
            source_node: Node,
            target_node: Node,
            direction: EdgeDirection = EdgeDirection.DIRECTED,
            **attributes
    ):
        """
        Inicijalizuj granu.

        Args:
            edge_id: Jedinstveni identifikator grane
            source_node: Početni čvor
            target_node: Krajnji čvor
            direction: Tip grane (DIRECTED ili UNDIRECTED)
            **attributes: Proizvoljni atributi grane
        """
        self.edge_id = edge_id
        self.source_node = source_node
        self.target_node = target_node
        self.direction = direction
        self.attributes: Dict[str, Any] = {}
        self.attribute_types: Dict[str, ValueType] = {}

        # Dodaj atribute sa type detektovanjem
        for key, value in attributes.items():  # ✅ DODATO .items()
            self.set_attribute(key, value)

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Postavi atribut grane.

        Args:
            key: Naziv atributa
            value: Vrednost atributa
        """
        if value is None:
            self.attributes[key] = None
            self.attribute_types[key] = ValueType.STR
            return

        detected_type = TypeValidator.detect_type(value)
        converted_value = TypeValidator.validate_and_convert(value, detected_type)

        self.attributes[key] = converted_value
        self.attribute_types[key] = detected_type

    def get_attribute(self, key: str) -> Any:
        """Uzmi vrednost atributa grane"""
        return self.attributes.get(key)

    def update_attribute(self, key: str, value: Any) -> None:
        """Ažuriraj atribut grane"""
        self.set_attribute(key, value)

    def delete_attribute(self, key: str) -> None:
        """Obriši atribut grane"""
        if key in self.attributes:
            del self.attributes[key]
            del self.attribute_types[key]

    def get_all_attributes(self) -> Dict[str, Any]:
        """Uzmi sve atribute grane"""
        return self.attributes.copy()

    def get_source_target(self) -> Tuple[Node, Node]:
        """Uzmi početni i krajnji čvor"""
        return self.source_node, self.target_node

    def get_other_node(self, node: Node) -> Optional[Node]:
        """Ako je grana neusmeren, uzmi drugi kraj grane"""
        if node == self.source_node:
            return self.target_node
        elif node == self.target_node:
            return self.source_node
        return None

    def is_directed(self) -> bool:
        """Provera da li je grana usmeren"""
        return self.direction == EdgeDirection.DIRECTED

    def connects_nodes(self, node1: Node, node2: Node) -> bool:
        """Provera da li grana povezuje dva čvora"""
        if self.direction == EdgeDirection.DIRECTED:
            return self.source_node == node1 and self.target_node == node2
        else:
            return (self.source_node == node1 and self.target_node == node2) or \
                (self.source_node == node2 and self.target_node == node1)

    def __repr__(self) -> str:
        """String reprezentacija grane"""
        arrow = "->" if self.direction == EdgeDirection.DIRECTED else "--"
        return f"Edge({self.source_node.node_id} {arrow} {self.target_node.node_id})"

    def __eq__(self, other) -> bool:
        """Dve grane su iste ako imaju isti ID"""
        if not isinstance(other, Edge):
            return False
        return self.edge_id == other.edge_id

    def __hash__(self) -> int:
        """Hash grane po ID-u"""
        return hash(self.edge_id)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuj granu u rečnik"""
        return {
            'id': self.edge_id,
            'source': self.source_node.node_id,
            'target': self.target_node.node_id,
            'direction': self.direction.value,
            'attributes': self.attributes.copy(),
            'types': {k: v.value for k, v in self.attribute_types.items()}
        }
