"""
Block Visualizer Plugin
Prikazuje čvorove kao pravougaonike sa atributima
"""
from typing import Dict
from api import VisualizerPlugin, Graph


class BlockVisualizerPlugin(VisualizerPlugin):
    """Plugin za vizuelizaciju grafa sa blokovima"""

    def get_plugin_name(self) -> str:
        return "Block Visualizer"

    def get_required_static_files(self) -> Dict[str, str]:
        return {
            'css': 'block_visualizer/static/css/block.css',
            'js': 'block_visualizer/static/js/block.js'
        }

    def visualize(self, graph: Graph) -> str:
        """Generiši HTML za graf"""

        nodes = []
        for node in graph.get_all_nodes():
            node_label = node.get_attribute('name') or node.get_attribute('id') or node.node_id
            attributes_html = "<br>".join(
                f"<small>{k}: {v}</small>"
                for k, v in node.get_all_attributes().items()
                if k not in ['name', 'id']
            )

            nodes.append({
                'id': node.node_id,
                'label': str(node_label),
                'attributes': attributes_html,
                'type': 'node'
            })

        links = []
        for edge in graph.get_all_edges():
            links.append({
                'source': edge.source_node.node_id,
                'target': edge.target_node.node_id,
                'type': 'link'
            })

        html = f"""
        <div id="block-visualizer" class="visualizer-container" style="width: 100%; height: 100%;">
            <svg id="block-svg" width="100%" height="100%"></svg>
        </div>

        <script>
            (function() {{
                const oldSvg = document.querySelector('#block-svg');
                if (oldSvg) {{
                    oldSvg.innerHTML = '';
                }}
                
                const graphData = {{
                    nodes: {nodes},
                    links: {links}
                }};

                const width = document.getElementById('block-svg').clientWidth;
                const height = document.getElementById('block-svg').clientHeight;

                const simulation = d3.forceSimulation(graphData.nodes)
                    .force('link', d3.forceLink(graphData.links)
                        .id(d => d.id)
                        .distance(200))
                    .force('charge', d3.forceManyBody().strength(-500))
                    .force('center', d3.forceCenter(width / 2, height / 2))
                    .force('collision', d3.forceCollide().radius(100));

                const svg = d3.select('#block-svg');
                const g = svg.append('g');

                svg.append('defs')
                    .append('marker')
                    .attr('id', 'arrowhead')
                    .attr('markerWidth', 10)
                    .attr('markerHeight', 10)
                    .attr('refX', 85)
                    .attr('refY', 3)
                    .attr('orient', 'auto')
                    .append('polygon')
                    .attr('points', '0 0, 10 3, 0 6')
                    .attr('fill', '#999');

                const links = g.selectAll('.link')
                    .data(graphData.links)
                    .enter()
                    .append('line')
                    .attr('class', 'link')
                    .attr('stroke', '#999')
                    .attr('stroke-width', 2)
                    .attr('marker-end', 'url(#arrowhead)');

                const nodeGroups = g.selectAll('.node-group')
                    .data(graphData.nodes)
                    .enter()
                    .append('g')
                    .attr('class', 'node-group')
                    .style('cursor', 'pointer')
                    .call(d3.drag()
                        .on('start', dragstarted)
                        .on('drag', dragged)
                        .on('end', dragended))
                    .on('click', function(event, d) {{
                        event.stopPropagation();
                        if (typeof selectNode === 'function') {{
                            selectNode(d.id);
                        }}
                    }})
                    .on('mouseover', function() {{
                        const rect = d3.select(this).select('rect');
                        const isSelected = rect.node().classList.contains('node-rect-selected');
                        if (!isSelected) {{
                            rect.attr('stroke', '#667eea').attr('stroke-width', 3);
                        }}
                    }})
                    .on('mouseout', function(event, d) {{
                        const rect = d3.select(this).select('rect');
                        const isSelected = rect.node().classList.contains('node-rect-selected');
                        if (!isSelected) {{
                            rect.attr('stroke', '#333').attr('stroke-width', 2);
                        }}
                    }});

                nodeGroups.append('rect')
                    .attr('class', 'node-rect')
                    .attr('width', 160)
                    .attr('height', 90)
                    .attr('x', -80)
                    .attr('y', -45)
                    .attr('rx', 5)
                    .attr('fill', '#fff')
                    .attr('stroke', '#333')
                    .attr('stroke-width', 2);

                nodeGroups.append('text')
                    .attr('class', 'node-label')
                    .attr('text-anchor', 'middle')
                    .attr('dy', '-25')
                    .style('font-weight', 'bold')
                    .style('font-size', '14px')
                    .text(d => d.label);

                nodeGroups.append('foreignObject')
                    .attr('x', -75)
                    .attr('y', -15)
                    .attr('width', 150)
                    .attr('height', 55)
                    .append('xhtml:div')
                    .style('font-size', '11px')
                    .style('color', '#666')
                    .style('overflow', 'hidden')
                    .html(d => d.attributes);

                simulation.on('tick', () => {{
                    links
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);

                    nodeGroups
                        .attr('transform', d => `translate(${{d.x}},${{d.y}})`);
                }});

                function dragstarted(event, d) {{
                    if (!event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }}

                function dragged(event, d) {{
                    d.fx = event.x;
                    d.fy = event.y;
                }}

                function dragended(event, d) {{
                    if (!event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }}

                svg.call(d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on('zoom', (event) => {{
                        g.attr('transform', event.transform);
                    }}));
            }})();
        </script>
        """

        return html