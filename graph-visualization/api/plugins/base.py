"""
Apstraktne klase za plugine.
DataSourcePlugin - parsira podatke i pravi graf
VisualizerPlugin - vizuelizuje graf
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from api.models.graph import Graph


class DataSourcePlugin(ABC):
    """
    Apstraktna klasa za Data Source plugine.
    Zadatak: parsirati podatke iz različitih izvora i formirati graf.
    """

    @abstractmethod
    def get_plugin_name(self) -> str:
        """
        Naziv plugina.
        Primer: "JSON Parser", "XML Parser"
        """
        pass

    @abstractmethod
    def get_required_parameters(self) -> Dict[str, str]:
        """
        Vraća obavezne parametre za plugin.

        Returns:
            Dict sa 'param_name': 'description'
            Primer: {'file_path': 'Path to JSON file'}
        """
        pass

    @abstractmethod
    def parse(self, **kwargs) -> Graph:
        """
        Parsiraj podatke i kreiraj graf.

        Args:
            **kwargs: Parametri specifični za plugin
                     (obavezno sadrže sveRequired parameters)

        Returns:
            Graph: Kreirani graf
        """
        pass

    def validate_parameters(self, **kwargs) -> bool:
        """
        Validacija parametara.
        Proverava da li su svi obavezni parametri prisutni.
        """
        required = self.get_required_parameters()
        for param_name in required.keys():
            if param_name not in kwargs:
                raise ValueError(f"Missing required parameter: {param_name}")
        return True


class VisualizerPlugin(ABC):
    """
    Apstraktna klasa za Visualizer plugine.
    Zadatak: vizuelizovati graf kao HTML string.
    """

    @abstractmethod
    def get_plugin_name(self) -> str:
        """
        Naziv plugina.
        Primer: "Simple Visualizer", "Block Visualizer"
        """
        pass

    @abstractmethod
    def visualize(self, graph: Graph) -> str:
        """
        Vizuelizuj graf kao HTML string.

        Args:
            graph: Graf koji treba vizuelizovati

        Returns:
            str: HTML reprezentacija grafa
        """
        pass

    @abstractmethod
    def get_required_static_files(self) -> Dict[str, str]:
        """
        Vraća putanje do CSS/JS fajlova.

        Returns:
            Dict sa 'type': 'path'
            Primer: {
                'css': 'simple_visualizer/static/css/simple.css',
                'js': 'simple_visualizer/static/js/simple.js'
            }
        """
        pass