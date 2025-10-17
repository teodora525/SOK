"""
Graph Visualization API
Version: 0.1.0

Ova biblioteka sadrži:
- Core modele za graf (Node, Edge, Graph)
- Type system (int, str, float, date)
- Plugin apstrakcije (DataSourcePlugin, VisualizerPlugin)
- Operacije na grafu (Search, Filter)
"""

__version__ = "0.1.0"
__author__ = "Graph Visualization Team"

# Type system
from api.types import ValueType, TypeValidator

# Models
from api.models.node import Node
from api.models.edge import Edge, EdgeDirection
from api.models.graph import Graph

# Plugins
from api.plugins.base import DataSourcePlugin, VisualizerPlugin

# Operations
from api.operations.search_filter import GraphSearch, GraphFilter, FilterCondition

__all__ = [
    # Types
    'ValueType',
    'TypeValidator',
    # Models
    'Node',
    'Edge',
    'EdgeDirection',
    'Graph',
    # Plugins
    'DataSourcePlugin',
    'VisualizerPlugin',
    # Operations
    'GraphSearch',
    'GraphFilter',
    'FilterCondition',
]