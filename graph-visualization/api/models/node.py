"""
Node model - reprezentacija čvora u grafu.
"""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from api.types import ValueType, TypeValidator


class Node(ABC):
    """
    Apstraktna klasa za čvor u grafu.
    Svaki čvor ima ID i proizvoljne atribute.
    """

    def __init__(self, node_id: str, **attributes):
        """
        Inicijalizuj čvor.

        Args:
            node_id: Jedinstveni identifikator čvora
            **attributes: Proizvoljni atributi čvora
        """
        self.node_id = node_id
        self.attributes: Dict[str, Any] = {}
        self.attribute_types: Dict[str, ValueType] = {}

        # Dodaj atribute sa type detektovanjem
        for key, value in attributes.items():
            self.set_attribute(key, value)

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Postavi atribut čvora sa type detektovanjem.

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
        """Uzmi vrednost atributa"""
        return self.attributes.get(key)

    def update_attribute(self, key: str, value: Any) -> None:
        """Ažuriraj atribut novom vrednošću"""
        self.set_attribute(key, value)

    def delete_attribute(self, key: str) -> None:
        """Obriši atribut"""
        if key in self.attributes:
            del self.attributes[key]
            del self.attribute_types[key]

    def get_attribute_type(self, key: str) -> Optional[ValueType]:
        """Uzmi tip atributa"""
        return self.attribute_types.get(key)

    def get_all_attributes(self) -> Dict[str, Any]:
        """Uzmi sve atribute"""
        return self.attributes.copy()

    def contains_in_attributes(self, query: str) -> bool:
        """
        Proverava da li query postoji u nazivu atributa ili vrednosti.
        Case-insensitive search.
        """
        query_lower = query.lower()

        # Pretraga u nazivima atributa
        if any(query_lower in key.lower() for key in self.attributes.keys()):
            return True

        # Pretraga u vrednostima atributa
        for value in self.attributes.values():
            if value is None:
                continue
            if query_lower in str(value).lower():
                return True

        return False

    def __repr__(self) -> str:
        """String reprezentacija čvora"""
        attrs = ", ".join(f"{k}={v}" for k, v in self.attributes.items())
        return f"Node({self.node_id}, {attrs})"

    def __eq__(self, other) -> bool:
        """Dva čvora su ista ako imaju isti ID"""
        if not isinstance(other, Node):
            return False
        return self.node_id == other.node_id

    def __hash__(self) -> int:
        """Hash čvora po ID-u"""
        return hash(self.node_id)

    def to_dict(self) -> Dict[str, Any]:
        """Konvertuj čvor u rečnik"""
        return {
            'id': self.node_id,
            'attributes': self.attributes.copy(),
            'types': {k: v.value for k, v in self.attribute_types.items()}
        }