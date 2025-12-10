#!/usr/bin/env python
"""
CLI runner - pokreće Graph CLI terminal
"""
import os
import sys

# Dodaj trenutni direktorijum u Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Django setup (potrebno da bi radili importi)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graph_explorer.settings')
import django

django.setup()

# Sada možeš importovati
from graph_platform.core import Platform
from graph_platform.cli import GraphCLI
from plugins.data_source_json_plugin import JSONDataSourcePlugin
from plugins.data_source_xml_plugin import XMLDataSourcePlugin
from plugins.simple_visualizer_plugin import SimpleVisualizerPlugin
from plugins.block_visualizer_plugin import BlockVisualizerPlugin


def main():
    """Pokreni CLI"""
    # Inicijalizuj platform
    platform = Platform()

    # Registruj plugine
    platform.plugin_manager.register_data_source_plugin(
        'JSON Parser',
        JSONDataSourcePlugin()
    )
    platform.plugin_manager.register_data_source_plugin(
        'XML Parser',
        XMLDataSourcePlugin()
    )
    platform.plugin_manager.register_visualizer_plugin(
        'Simple Visualizer',
        SimpleVisualizerPlugin()
    )
    platform.plugin_manager.register_visualizer_plugin(
        'Block Visualizer',
        BlockVisualizerPlugin()
    )

    # Opciono: učitaj neki test graf
    try:
        from django.conf import settings
        test_file = os.path.join(settings.TEST_DATA_DIR, 'family_tree.json')

        if os.path.exists(test_file):
            print(f"📂 Loading test graph from {test_file}...")
            platform.create_graph_from_source(
                workspace_id='cli_workspace',
                data_source_plugin_name='JSON Parser',
                file_path=test_file
            )
            print("✓ Test graph loaded!\n")
        else:
            print("⚠️  No test graph found. You'll start with an empty workspace.\n")
            # Kreiraj prazan workspace
            from api.models.graph import Graph
            empty_graph = Graph('empty_graph')
            platform.graph_manager.create_workspace('cli_workspace', empty_graph)

    except Exception as e:
        print(f"⚠️  Could not load test graph: {e}")
        print("Starting with empty workspace...\n")
        from api.models.graph import Graph
        empty_graph = Graph('empty_graph')
        platform.graph_manager.create_workspace('cli_workspace', empty_graph)

    # Pokreni CLI
    cli = GraphCLI(platform)
    cli.start()


if __name__ == '__main__':
    main()