"""
CLI modul - Command Line Interface za manipulaciju grafom
"""
import re
import os
import time
from typing import Optional
from api.models.node import Node
from api.models.edge import Edge, EdgeDirection


class CLICommand:
    """Predstavlja jednu CLI komandu"""

    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description

    def execute(self, *args, **kwargs):
        """Izvrši komandu"""
        raise NotImplementedError


class GraphCLI:
    """Command Line Interface za rad sa grafom"""

    def __init__(self, platform):
        self.platform = platform
        self.running = False

    def start(self):
        """Pokreni CLI terminal"""
        self.running = True
        print("=" * 60)
        print("📊 Graph CLI Terminal")
        print("=" * 60)
        print("Type 'help' for available commands")
        print("Type 'exit' to quit\n")

        while self.running:
            try:
                user_input = input("graph> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == 'exit':
                    self.running = False
                    print("Goodbye!")
                    break

                self.execute_command(user_input)

            except KeyboardInterrupt:
                print("\n\nInterrupted!")
                self.running = False
            except Exception as e:
                print(f"Error: {e}")

    def execute_command(self, command_str: str):
        """Parsiraj i izvrši komandu"""
        parts = command_str.split()

        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:]

        if cmd == 'help':
            self.show_help()
        elif cmd == 'create':
            self.handle_create(args)
        elif cmd == 'edit':
            self.handle_edit(args)
        elif cmd == 'delete':
            self.handle_delete(args)
        elif cmd == 'list':
            self.handle_list(args)
        elif cmd == 'search':
            self.handle_search(command_str)
        elif cmd == 'filter':
            self.handle_filter(command_str)
        elif cmd == 'info':
            self.handle_info()
        elif cmd == 'reset':
            self.handle_reset()
        elif cmd == 'load':
            self.handle_load(args)
        elif cmd == 'switch':
            self.handle_switch(args)
        elif cmd == 'workspaces':
            self.handle_workspaces()
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def show_help(self):
        """Prikaži dostupne komande"""
        help_text = """
Available Commands:
==================

1. CREATE NODE
   create node --id=<id> --property <key>=<value> [--property <key>=<value> ...]
   Example: create node --id=1 --property name=John --property age=30

2. CREATE EDGE
   create edge --id=<id> --from=<source_id> --to=<target_id> [--property <key>=<value> ...]
   Example: create edge --id=e1 --from=1 --to=2 --property relation=friend

3. EDIT NODE
   edit node --id=<id> --property <key>=<value>
   Example: edit node --id=1 --property age=31

4. EDIT EDGE
   edit edge --id=<id> --property <key>=<value>
   Example: edit edge --id=e1 --property weight=5

5. DELETE NODE
   delete node --id=<id>
   Example: delete node --id=1

6. DELETE EDGE
   delete edge --id=<id>
   Example: delete edge --id=e1

7. LIST NODES
   list nodes

8. LIST EDGES
   list edges

9. SEARCH
   search '<query>'
   Example: search 'John'

10. FILTER
    filter '<expression>'
    Example: filter 'age > 30 && name == John'

11. INFO
    info

12. RESET
    reset

13. LOAD GRAPH
    load --file=<filepath> --plugin=<JSON Parser|XML Parser>
    Example: load --file=test_data/family_tree.json --plugin='JSON Parser'

14. SWITCH WORKSPACE
    switch --workspace=<workspace_id>
    Example: switch --workspace=cli_ws_1234567890

15. LIST WORKSPACES
    workspaces

16. EXIT
    exit
        """
        print(help_text)

    def handle_create(self, args):
        """Rukuj 'create' komandom"""
        if not args:
            print("Usage: create node|edge ...")
            return

        entity_type = args[0].lower()

        if entity_type == 'node':
            self._create_node(args[1:])
        elif entity_type == 'edge':
            self._create_edge(args[1:])
        else:
            print(f"Unknown entity type: {entity_type}")

    def _create_node(self, args):
        """Kreiraj čvor"""
        node_id = None
        properties = {}

        i = 0
        while i < len(args):
            if args[i].startswith('--id='):
                node_id = args[i].split('=', 1)[1]
            elif args[i] == '--property':
                i += 1
                if i < len(args) and '=' in args[i]:
                    parts = args[i].split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        properties[key] = value
            i += 1

        if not node_id:
            print("Error: --id is required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph

            if graph.get_node(node_id):
                print(f"Error: Node {node_id} already exists")
                return

            # Kreiraj čvor
            class CLINode(Node):
                pass

            node = CLINode(node_id, **properties)
            graph.add_node(node)

            print(f"✓ Node {node_id} created with properties: {properties}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error creating node: {e}")

    def _create_edge(self, args):
        """Kreiraj granu"""
        edge_id = None
        source_id = None
        target_id = None
        properties = {}

        i = 0
        while i < len(args):
            if args[i].startswith('--id='):
                edge_id = args[i].split('=', 1)[1]
            elif args[i].startswith('--from='):
                source_id = args[i].split('=', 1)[1]
            elif args[i].startswith('--to='):
                target_id = args[i].split('=', 1)[1]
            elif args[i] == '--property':
                i += 1
                if i < len(args) and '=' in args[i]:
                    parts = args[i].split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        properties[key] = value
            i += 1

        if not edge_id or not source_id or not target_id:
            print("Error: --id, --from, and --to are required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph

            source_node = graph.get_node(source_id)
            target_node = graph.get_node(target_id)

            if not source_node or not target_node:
                print(f"Error: Source or target node not found")
                return

            edge = Edge(edge_id, source_node, target_node, EdgeDirection.DIRECTED, **properties)
            graph.add_edge(edge)

            print(f"✓ Edge {edge_id} created from {source_id} to {target_id}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error creating edge: {e}")

    def handle_edit(self, args):
        """Rukuj 'edit' komandom"""
        if not args:
            print("Usage: edit node|edge ...")
            return

        entity_type = args[0].lower()

        if entity_type == 'node':
            self._edit_node(args[1:])
        elif entity_type == 'edge':
            self._edit_edge(args[1:])
        else:
            print(f"Unknown entity type: {entity_type}")

    def _edit_node(self, args):
        """Izmeni čvor"""
        node_id = None
        properties = {}

        i = 0
        while i < len(args):
            if args[i].startswith('--id='):
                node_id = args[i].split('=', 1)[1]
            elif args[i] == '--property':
                i += 1
                if i < len(args) and '=' in args[i]:
                    parts = args[i].split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        properties[key] = value
            i += 1

        if not node_id:
            print("Error: --id is required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph
            node = graph.get_node(node_id)

            if not node:
                print(f"Error: Node {node_id} not found")
                return

            for key, value in properties.items():
                node.update_attribute(key, value)

            print(f"✓ Node {node_id} updated with properties: {properties}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error editing node: {e}")

    def _edit_edge(self, args):
        """Izmeni granu"""
        edge_id = None
        properties = {}

        i = 0
        while i < len(args):
            if args[i].startswith('--id='):
                edge_id = args[i].split('=', 1)[1]
            elif args[i] == '--property':
                i += 1
                if i < len(args) and '=' in args[i]:
                    parts = args[i].split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        properties[key] = value
            i += 1

        if not edge_id:
            print("Error: --id is required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph
            edge = graph.get_edge(edge_id)

            if not edge:
                print(f"Error: Edge {edge_id} not found")
                return

            for key, value in properties.items():
                edge.update_attribute(key, value)

            print(f"✓ Edge {edge_id} updated")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error editing edge: {e}")

    def handle_delete(self, args):
        """Rukuj 'delete' komandom"""
        if not args:
            print("Usage: delete node|edge --id=<id>")
            return

        entity_type = args[0].lower()

        if entity_type == 'node':
            self._delete_node(args[1:])
        elif entity_type == 'edge':
            self._delete_edge(args[1:])
        else:
            print(f"Unknown entity type: {entity_type}")

    def _delete_node(self, args):
        """Obriši čvor"""
        node_id = None

        for arg in args:
            if arg.startswith('--id='):
                node_id = arg.split('=', 1)[1]

        if not node_id:
            print("Error: --id is required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph

            if not graph.get_node(node_id):
                print(f"Error: Node {node_id} not found")
                return

            # Proveri da li čvor ima dolazne grane
            node = graph.get_node(node_id)
            if len(graph.get_incoming_edges(node)) > 0 or len(graph.get_outgoing_edges(node)) > 0:
                print(f"Error: Node {node_id} has edges. Delete edges first.")
                return

            graph.remove_node(node_id)
            print(f"✓ Node {node_id} deleted")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error deleting node: {e}")

    def _delete_edge(self, args):
        """Obriši granu"""
        edge_id = None

        for arg in args:
            if arg.startswith('--id='):
                edge_id = arg.split('=', 1)[1]

        if not edge_id:
            print("Error: --id is required")
            return

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph

            if not graph.get_edge(edge_id):
                print(f"Error: Edge {edge_id} not found")
                return

            graph.remove_edge(edge_id)
            print(f"✓ Edge {edge_id} deleted")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error deleting edge: {e}")

    def handle_list(self, args):
        """Rukuj 'list' komandom"""
        if not args:
            print("Usage: list nodes|edges")
            return

        entity_type = args[0].lower()

        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.current_graph

            if entity_type == 'nodes':
                nodes = graph.get_all_nodes()
                if not nodes:
                    print("No nodes in graph")
                    return
                print(f"\nNodes ({len(nodes)} total):")
                print("-" * 60)
                for node in nodes:
                    print(f"  ID: {node.node_id}")
                    for key, value in node.get_all_attributes().items():
                        print(f"    {key}: {value}")
                    print()

            elif entity_type == 'edges':
                edges = graph.get_all_edges()
                if not edges:
                    print("No edges in graph")
                    return
                print(f"\nEdges ({len(edges)} total):")
                print("-" * 60)
                for edge in edges:
                    print(f"  ID: {edge.edge_id}")
                    print(f"    From: {edge.source_node.node_id}")
                    print(f"    To: {edge.target_node.node_id}")
                    print(f"    Direction: {edge.direction.value}")
                    for key, value in edge.get_all_attributes().items():
                        print(f"    {key}: {value}")
                    print()
            else:
                print(f"Unknown entity type: {entity_type}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error listing: {e}")

    def handle_search(self, command_str: str):
        """Rukuj 'search' komandom"""
        match = re.search(r"search\s+'([^']+)'", command_str)
        if not match:
            print("Usage: search '<query>'")
            return

        query = match.group(1)

        try:
            self.platform.search_in_active_workspace(query)

            workspace = self.platform.graph_manager.get_active_workspace()
            graph = workspace.get_current_graph()

            print(f"✓ Search applied")
            print(f"  Results: {graph.get_number_of_nodes()} nodes matched")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error searching: {e}")

    def handle_filter(self, command_str: str):
        """Rukuj 'filter' komandom"""
        match = re.search(r"filter\s+'([^']+)'", command_str)
        if not match:
            print("Usage: filter '<expression>'")
            return

        filter_expr = match.group(1)

        try:
            self.platform.filter_in_active_workspace(filter_expr)

            workspace = self.platform.graph_manager.get_active_workspace()
            graph = workspace.get_current_graph()

            print(f"✓ Filter applied")
            print(f"  Results: {graph.get_number_of_nodes()} nodes matched")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error filtering: {e}")

    def handle_info(self):
        """Prikaži informacije o grafu"""
        try:
            workspace = self.platform.graph_manager.get_active_workspace()
            if not workspace:
                print("Error: No active workspace")
                return

            graph = workspace.get_current_graph()
            original_graph = workspace.original_graph

            print("\nGraph Information:")
            print("=" * 60)
            print(f"Workspace ID: {workspace.workspace_id}")
            print(f"Current Nodes: {graph.get_number_of_nodes()}")
            print(f"Current Edges: {graph.get_number_of_edges()}")
            print(f"Original Nodes: {original_graph.get_number_of_nodes()}")
            print(f"Original Edges: {original_graph.get_number_of_edges()}")
            print(f"Has Cycle: {original_graph.has_cycle()}")
            print(f"Search History: {workspace.search_history}")
            print(f"Filter History: {workspace.filter_history}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error getting info: {e}")

    def handle_reset(self):
        """Resetuj graf"""
        try:
            self.platform.reset_active_workspace()
            print("✓ Graph reset to original state")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error resetting: {e}")

    def handle_load(self, args):
        """Učitaj novi graf iz fajla"""
        file_path = None
        plugin_identifier = None

        for arg in args:
            if arg.startswith('--file='):
                file_path = arg.split('=', 1)[1]
            elif arg.startswith('--plugin='):
                plugin_identifier = arg.split('=', 1)[1].strip("'\"")

        if not file_path or not plugin_identifier:
            print("Error: --file and --plugin are required")
            print("\nExample:")
            print("  load --file=family_tree.json --plugin=1")
            print("\nAvailable plugins:")
            plugins = list(self.platform.plugin_manager.get_all_data_source_plugins().keys())
            for idx, name in enumerate(plugins, 1):
                print(f"  {idx}. {name}")
            return

        # Automatski dodaj plugins/data/ folder ako korisnik unese samo ime fajla
        if not os.path.isabs(file_path) and not file_path.startswith('plugins/data/'):
            file_path = os.path.join('plugins', 'data', file_path)

        if not os.path.exists(file_path):
            print(f"Error: File not found: {file_path}")
            print(f"Make sure the file exists in: plugins/data/")
            return

        # Odredi plugin name
        plugins = list(self.platform.plugin_manager.get_all_data_source_plugins().keys())

        # Ako je broj, uzmi plugin po indexu
        if plugin_identifier.isdigit():
            plugin_index = int(plugin_identifier)
            if 1 <= plugin_index <= len(plugins):
                plugin_name = plugins[plugin_index - 1]
            else:
                print(f"Error: Invalid plugin number. Choose 1-{len(plugins)}")
                return
        else:
            # Pokušaj naći plugin po imenu (case-insensitive partial match)
            plugin_name = None
            search_term = plugin_identifier.lower()
            for p in plugins:
                if search_term in p.lower():
                    plugin_name = p
                    break

            if not plugin_name:
                print(f"Error: Plugin '{plugin_identifier}' not found")
                print("Available plugins:")
                for idx, name in enumerate(plugins, 1):
                    print(f"  {idx}. {name}")
                return

        try:
            # Generiši novi workspace ID
            workspace_id = f'cli_ws_{int(time.time())}'

            # Učitaj graf
            print(f"📂 Loading graph from {file_path}...")
            print(f"   Using plugin: {plugin_name}")
            graph = self.platform.create_graph_from_source(
                workspace_id=workspace_id,
                data_source_plugin_name=plugin_name,
                file_path=file_path
            )

            print(f"✓ Graph loaded successfully!")
            print(f"  Workspace: {workspace_id}")
            print(f"  Nodes: {graph.get_number_of_nodes()}")
            print(f"  Edges: {graph.get_number_of_edges()}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading graph: {e}")
    def handle_switch(self, args):
        """Prebaci se na drugi workspace"""
        workspace_id = None

        for arg in args:
            if arg.startswith('--workspace='):
                workspace_id = arg.split('=', 1)[1]

        if not workspace_id:
            print("Error: --workspace is required")
            print("Use 'workspaces' command to see available workspaces")
            return

        try:
            self.platform.graph_manager.set_active_workspace(workspace_id)
            workspace = self.platform.graph_manager.get_active_workspace()
            graph = workspace.get_current_graph()

            print(f"✓ Switched to workspace: {workspace_id}")
            print(f"  Nodes: {graph.get_number_of_nodes()}")
            print(f"  Edges: {graph.get_number_of_edges()}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error switching workspace: {e}")

    def handle_workspaces(self):
        """Prikaži sve workspace-ove"""
        try:
            workspaces = self.platform.graph_manager.get_all_workspaces()
            active_ws = self.platform.graph_manager.active_workspace

            if not workspaces:
                print("No workspaces available")
                return

            print("\nWorkspaces:")
            print("=" * 60)
            for ws_id, ws in workspaces.items():
                active_marker = "→" if ws_id == active_ws else " "
                graph = ws.get_current_graph()
                print(f"{active_marker} {ws_id}")
                print(f"    Nodes: {graph.get_number_of_nodes()}, Edges: {graph.get_number_of_edges()}")
                if ws.search_history:
                    print(f"    Search History: {ws.search_history}")
                if ws.filter_history:
                    print(f"    Filter History: {ws.filter_history}")
                print()

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error listing workspaces: {e}")