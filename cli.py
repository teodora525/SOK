"""
CLI modul - Command Line Interface za manipulaciju grafom
"""
import re
import uuid
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

13. EXIT
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
            elif args[i].startswith('--property'):
                if '=' in args[i]:
                    _, prop = args[i].split('=', 1)
                    key, value = prop.split('=', 1)
                    properties[key] = value
                else:
                    i += 1
                    if i < len(args):
                        key, value = args[i].split('=', 1)
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
            elif args[i].startswith('--property'):
                if '=' in args[i]:
                    _, prop = args[i].split('=', 1)
                    key, value = prop.split('=', 1)
                    properties[key] = value
                else:
                    i += 1
                    if i < len(args):
                        key, value = args[i].split('=', 1)
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
            elif args[i].startswith('--property'):
                if '=' in args[i]:
                    _, prop = args[i].split('=', 1)
                    key, value = prop.split('=', 1)
                    properties[key] = value
                else:
                    i += 1
                    if i < len(args):
                        key, value = args[i].split('=', 1)
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
            print(f"Error editing node: {e}")

    def _edit_edge(self, args):
        """Izmeni granu"""
        edge_id = None
        properties = {}

        i = 0
        while i < len(args):
            if args[i].startswith('--id='):
                edge_id = args[i].split('=', 1)[1]
            elif args[i].startswith('--property'):
                if '=' in args[i]:
                    _, prop = args[i].split('=', 1)
                    key, value = prop.split('=', 1)
                    properties[key] = value
                else:
                    i += 1
                    if i < len(args):
                        key, value = args[i].split('=', 1)
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
            print(f"Error getting info: {e}")

    def handle_reset(self):
        """Resetuj graf"""
        try:
            self.platform.reset_active_workspace()
            print("✓ Graph reset to original state")
        except Exception as e:
            print(f"Error resetting: {e}")