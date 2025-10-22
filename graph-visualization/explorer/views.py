"""
Django views za graph explorer - koristi Singleton Platform
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from graph_platform.core import Platform
from plugins.data_source_json_plugin import JSONDataSourcePlugin
from plugins.data_source_xml_plugin import XMLDataSourcePlugin
from plugins.simple_visualizer_plugin import SimpleVisualizerPlugin
from plugins.block_visualizer_plugin import BlockVisualizerPlugin

current_visualizer = None


def get_platform():
    """
    Uzmi Platform singleton instancu.
    Automatski registruje plugine pri prvom pozivu.
    """
    platform = Platform()

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

    return platform


def index(request):
    """Prikaži glavnu stranicu"""
    get_platform()
    return render(request, 'index.html')


@require_http_methods(["GET"])
def get_plugins(request):
    """Uzmi sve dostupne plugine"""
    platform = get_platform()

    data_source_plugins = [
        {
            'name': name,
            'plugin_name': plugin.get_plugin_name(),
            'required_parameters': plugin.get_required_parameters()
        }
        for name, plugin in platform.plugin_manager.get_all_data_source_plugins().items()
    ]

    visualizer_plugins = [
        {
            'name': name,
            'plugin_name': plugin.get_plugin_name()
        }
        for name, plugin in platform.plugin_manager.get_all_visualizer_plugins().items()
    ]

    workspaces = [
        {
            'id': ws_id,
            'graph_size': f"Nodes: {ws.get_current_graph().get_number_of_nodes()}, Edges: {ws.get_current_graph().get_number_of_edges()}"
        }
        for ws_id, ws in platform.graph_manager.get_all_workspaces().items()
    ]

    return JsonResponse({
        'data_source_plugins': data_source_plugins,
        'visualizer_plugins': visualizer_plugins,
        'workspaces': workspaces,
        'active_workspace': platform.graph_manager.active_workspace
    })


@require_http_methods(["POST"])
def get_node_details(request):
    """Uzmi detalje o specifičnom čvoru"""
    try:
        data = json.loads(request.body)
        platform = get_platform()

        node_id = data.get('node_id')

        if not node_id:
            return JsonResponse({'success': False, 'error': 'node_id is required'}, status=400)

        workspace = platform.graph_manager.get_active_workspace()
        if not workspace:
            return JsonResponse({'success': False, 'error': 'No active workspace'}, status=400)

        graph = workspace.get_current_graph()
        node = graph.get_node(node_id)

        if not node:
            return JsonResponse({'success': False, 'error': f'Node {node_id} not found'}, status=404)

        # Uzmi susedne čvorove
        neighbors = graph.get_neighbors(node)
        incoming_edges = graph.get_incoming_edges(node)
        outgoing_edges = graph.get_outgoing_edges(node)

        return JsonResponse({
            'success': True,
            'node': {
                'id': node.node_id,
                'attributes': node.get_all_attributes(),
                'neighbors': [n.node_id for n in neighbors],
                'incoming_count': len(incoming_edges),
                'outgoing_count': len(outgoing_edges),
                'degree': len(neighbors)
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
@require_http_methods(["POST"])
def load_graph(request):
    """Učitaj graf iz data source plugina"""
    try:
        data = json.loads(request.body)
        platform = get_platform()

        plugin_name = data.get('plugin_name')
        workspace_id = data.get('workspace_id', 'default')
        plugin_params = data.get('parameters', {})

        if 'file_path' in plugin_params:
            file_path = plugin_params['file_path']
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.TEST_DATA_DIR, file_path)
            plugin_params['file_path'] = file_path

        graph = platform.create_graph_from_source(workspace_id, plugin_name, **plugin_params)

        platform.graph_manager.set_active_workspace(workspace_id)

        return JsonResponse({
            'success': True,
            'workspace_id': workspace_id,
            'graph_info': {
                'nodes': graph.get_number_of_nodes(),
                'edges': graph.get_number_of_edges(),
                'has_cycle': graph.has_cycle()
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


"""
DODAJ OVE DVE FUNKCIJE U explorer/views.py (posle load_graph funkcije)
"""


@require_http_methods(["POST"])
def upload_graph(request):
    """Uploaduj fajl i učitaj graf"""
    try:
        platform = get_platform()

        uploaded_file = request.FILES.get('file')
        plugin_name = request.POST.get('plugin_name')
        workspace_id = request.POST.get('workspace_id', 'default')

        if not uploaded_file:
            return JsonResponse({'success': False, 'error': 'No file uploaded'}, status=400)

        if not plugin_name:
            return JsonResponse({'success': False, 'error': 'No plugin selected'}, status=400)

        # Sačuvaj fajl privremeno
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        try:
            # Učitaj dodatne parametre
            parameters_str = request.POST.get('parameters', '{}')
            plugin_params = json.loads(parameters_str)
            plugin_params['file_path'] = tmp_file_path

            # Kreiraj graf
            graph = platform.create_graph_from_source(workspace_id, plugin_name, **plugin_params)
            platform.graph_manager.set_active_workspace(workspace_id)

            return JsonResponse({
                'success': True,
                'workspace_id': workspace_id,
                'graph_info': {
                    'nodes': graph.get_number_of_nodes(),
                    'edges': graph.get_number_of_edges(),
                    'has_cycle': graph.has_cycle()
                }
            })

        finally:
            # Obriši privremeni fajl
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def switch_workspace(request):
    """Prebaci se na drugi workspace"""
    try:
        data = json.loads(request.body)
        platform = get_platform()

        workspace_id = data.get('workspace_id')

        if not workspace_id:
            return JsonResponse({'success': False, 'error': 'workspace_id is required'}, status=400)

        # Proveri da li workspace postoji
        workspace = platform.graph_manager.get_workspace(workspace_id)
        if not workspace:
            return JsonResponse({'success': False, 'error': f'Workspace {workspace_id} not found'}, status=400)

        # Prebaci se na taj workspace
        platform.graph_manager.set_active_workspace(workspace_id)

        graph = workspace.get_current_graph()

        return JsonResponse({
            'success': True,
            'workspace_id': workspace_id,
            'graph_info': {
                'nodes': graph.get_number_of_nodes(),
                'edges': graph.get_number_of_edges(),
                'has_cycle': graph.has_cycle()
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
@require_http_methods(["POST"])
def visualize(request):
    """Vizuelizuj trenutni graf"""
    try:
        data = json.loads(request.body)
        platform = get_platform()
        global current_visualizer

        visualizer_name = data.get('visualizer_name', 'Simple Visualizer')
        current_visualizer = visualizer_name

        workspace = platform.graph_manager.get_active_workspace()
        if not workspace:
            print("❌ No active workspace!")
            return JsonResponse({'success': False, 'error': 'No active workspace'}, status=400)

        graph = workspace.get_current_graph()
        print(f"🎨 Visualizing {graph.get_number_of_nodes()} nodes with {visualizer_name}")

        if graph.get_number_of_nodes() == 0:
            print("⚠️ Graph is empty!")
            return JsonResponse({'success': False, 'error': 'Graph is empty'}, status=400)

        html = platform.visualize_current_graph(visualizer_name)

        return JsonResponse({
            'success': True,
            'html': html
        })
    except Exception as e:
        print(f"❌ Error in visualize: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def search(request):
    """Pretraži u aktivnom grafu"""
    try:
        data = json.loads(request.body)
        platform = get_platform()

        query = data.get('query', '')

        if not query:
            return JsonResponse({'success': False, 'error': 'Query is required'}, status=400)

        platform.search_in_active_workspace(query)

        workspace = platform.graph_manager.get_active_workspace()
        graph = workspace.get_current_graph()

        html = platform.visualize_current_graph(current_visualizer or 'Simple Visualizer')

        return JsonResponse({
            'success': True,
            'html': html,
            'graph_info': {
                'nodes': graph.get_number_of_nodes(),
                'edges': graph.get_number_of_edges()
            },
            'search_history': workspace.search_history
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

