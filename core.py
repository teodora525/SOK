"""
Platform - jezgro aplikacije
Upravlja grafovima, pluginima, search/filter operacijama
"""
from typing import Dict, List, Optional, Tuple
from api.models.graph import Graph
from api.plugins.base import DataSourcePlugin, VisualizerPlugin
from api.operations.search_filter import GraphSearch, GraphFilter


class Workspace:
    """Predstavlja jedan workspace - graf sa aktivnim filterima/pretragama"""

    def __init__(self, workspace_id: str, original_graph: Graph):
        self.workspace_id = workspace_id
        self.original_graph = original_graph
        self.current_graph = original_graph
        self.search_history: List[str] = []
        self.filter_history: List[str] = []

    def apply_search(self, query: str) -> None:
        """Primeni search na trenutni graf"""
        self.current_graph = GraphSearch.search(self.current_graph, query)
        self.search_history.append(query)

    def apply_filter(self, filter_expr: str) -> None:
        """Primeni filter na trenutni graf"""
        self.current_graph = GraphFilter.filter(self.current_graph, filter_expr)
        self.filter_history.append(filter_expr)

    def reset_to_original(self) -> None:
        """Vrati se na originalni graf"""
        self.current_graph = self.original_graph
        self.search_history = []
        self.filter_history = []

    def get_current_graph(self) -> Graph:
        """Uzmi trenutni graf"""
        return self.current_graph


class GraphManager:
    """Upravlja grafovima i workspacima"""

    def __init__(self):
        self.workspaces: Dict[str, Workspace] = {}
        self.active_workspace: Optional[str] = None

    def create_workspace(self, workspace_id: str, graph: Graph) -> Workspace:
        """Kreiraj novi workspace"""
        if workspace_id in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} already exists")

        workspace = Workspace(workspace_id, graph)
        self.workspaces[workspace_id] = workspace

        # Prvo kreirani workspace je aktivan
        if self.active_workspace is None:
            self.active_workspace = workspace_id

        return workspace

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Uzmi workspace po ID-u"""
        return self.workspaces.get(workspace_id)

    def get_active_workspace(self) -> Optional[Workspace]:
        """Uzmi aktivni workspace"""
        if self.active_workspace:
            return self.workspaces.get(self.active_workspace)
        return None

    def set_active_workspace(self, workspace_id: str) -> None:
        """Postavi aktivni workspace"""
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")
        self.active_workspace = workspace_id

    def get_all_workspaces(self) -> Dict[str, Workspace]:
        """Uzmi sve workspaces"""
        return self.workspaces.copy()

    def delete_workspace(self, workspace_id: str) -> None:
        """Obriši workspace"""
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace {workspace_id} not found")

        del self.workspaces[workspace_id]

        if self.active_workspace == workspace_id:
            self.active_workspace = None


class PluginManager:
    """Upravlja pluginima - detekcija i učitavanje"""

    def __init__(self):
        self.data_source_plugins: Dict[str, DataSourcePlugin] = {}
        self.visualizer_plugins: Dict[str, VisualizerPlugin] = {}

    def register_data_source_plugin(self, plugin_name: str, plugin: DataSourcePlugin) -> None:
        """Registruj Data Source plugin"""
        if plugin_name not in self.data_source_plugins:  # ← DODAJ OVO!
            self.data_source_plugins[plugin_name] = plugin

    def register_visualizer_plugin(self, plugin_name: str, plugin: VisualizerPlugin) -> None:
        """Registruj Visualizer plugin"""
        if plugin_name not in self.visualizer_plugins:  # ← DODAJ OVO!
            self.visualizer_plugins[plugin_name] = plugin
    def get_data_source_plugin(self, plugin_name: str) -> Optional[DataSourcePlugin]:
        """Uzmi Data Source plugin"""
        return self.data_source_plugins.get(plugin_name)

    def get_visualizer_plugin(self, plugin_name: str) -> Optional[VisualizerPlugin]:
        """Uzmi Visualizer plugin"""
        return self.visualizer_plugins.get(plugin_name)

    def get_all_data_source_plugins(self) -> Dict[str, DataSourcePlugin]:
        """Uzmi sve Data Source plugine"""
        return self.data_source_plugins.copy()

    def get_all_visualizer_plugins(self) -> Dict[str, VisualizerPlugin]:
        """Uzmi sve Visualizer plugine"""
        return self.visualizer_plugins.copy()


class Platform:
    """Glavna Platform klasa - orkestrira sve"""

    def __init__(self):
        self.graph_manager = GraphManager()
        self.plugin_manager = PluginManager()

    def create_graph_from_source(
            self,
            workspace_id: str,
            data_source_plugin_name: str,
            **plugin_params
    ) -> Graph:
        """Kreiraj graf iz data source plugina"""
        plugin = self.plugin_manager.get_data_source_plugin(data_source_plugin_name)

        if not plugin:
            raise ValueError(f"Plugin {data_source_plugin_name} not found")

        # Parsiraj podatke
        graph = plugin.parse(**plugin_params)

        # Kreiraj workspace
        self.graph_manager.create_workspace(workspace_id, graph)

        return graph

    def visualize_current_graph(self, visualizer_plugin_name: str) -> str:
        """Vizuelizuj aktivni graf"""
        workspace = self.graph_manager.get_active_workspace()

        if not workspace:
            raise ValueError("No active workspace")

        plugin = self.plugin_manager.get_visualizer_plugin(visualizer_plugin_name)

        if not plugin:
            raise ValueError(f"Plugin {visualizer_plugin_name} not found")

        graph = workspace.get_current_graph()
        return plugin.visualize(graph)

    def search_in_active_workspace(self, query: str) -> None:
        """Pretraži u aktivnom workspaceu"""
        workspace = self.graph_manager.get_active_workspace()

        if not workspace:
            raise ValueError("No active workspace")

        workspace.apply_search(query)

    def filter_in_active_workspace(self, filter_expr: str) -> None:
        """Filtriraj u aktivnom workspaceu"""
        workspace = self.graph_manager.get_active_workspace()

        if not workspace:
            raise ValueError("No active workspace")

        workspace.apply_filter(filter_expr)

    def reset_active_workspace(self) -> None:
        """Resetuj aktivni workspace"""
        workspace = self.graph_manager.get_active_workspace()

        if not workspace:
            raise ValueError("No active workspace")

        workspace.reset_to_original()