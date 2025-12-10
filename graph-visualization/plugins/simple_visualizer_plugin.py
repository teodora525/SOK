"""
Simple Visualizer Plugin
Prikazuje čvorove kao jednostavne krugove sa D3.js
"""
from typing import Dict
from api import VisualizerPlugin, Graph


class SimpleVisualizerPlugin(VisualizerPlugin):
    """Plugin za jednostavnu vizuelizaciju grafa"""

    def get_plugin_name(self) -> str:
        return "Simple Visualizer"

    def get_required_static_files(self) -> Dict[str, str]:
        return {
            'css': 'simple_visualizer/static/css/simple.css',
            'js': 'simple_visualizer/static/js/simple.js'
        }

    def visualize(self, graph: Graph) -> str:
        """Generiši HTML za graf"""

        nodes = []
        for node in graph.get_all_nodes():
            node_label = node.get_attribute('name') or node.get_attribute('id') or node.node_id
            nodes.append({
                'id': node.node_id,
                'label': str(node_label),
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
        <div id="simple-visualizer" class="visualizer-container" style="width: 100%; height: 100%;">
            <svg id="simple-svg" width="100%" height="100%"></svg>
        </div>

        <script>
            (function() {{
                const oldSvg = document.querySelector('#simple-svg');
                if (oldSvg) {{
                    oldSvg.innerHTML = '';
                }}

                const graphData = {{
                    nodes: {nodes},
                    links: {links}
                }};

                const width = document.getElementById('simple-svg').clientWidth;
                const height = document.getElementById('simple-svg').clientHeight;

                const simulation = d3.forceSimulation(graphData.nodes)
                    .force('link', d3.forceLink(graphData.links)
                        .id(d => d.id)
                        .distance(100))
                    .force('charge', d3.forceManyBody().strength(-300))
                    .force('center', d3.forceCenter(width / 2, height / 2));

                const svg = d3.select('#simple-svg');

                const links = svg.selectAll('.link')
                    .data(graphData.links)
                    .enter()
                    .append('line')
                    .attr('class', 'link')
                    .attr('stroke', '#999')
                    .attr('stroke-width', 2);

                const nodes = svg.selectAll('.node')
                    .data(graphData.nodes)
                    .enter()
                    .append('circle')
                    .attr('class', 'node')
                    .attr('r', 10)
                    .attr('fill', '#1f77b4')
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
                    .on('mouseover', function(event, d) {{
                        const isSelected = this.classList.contains('node-selected');
                        if (!isSelected) {{
                            d3.select(this).attr('r', 15);
                        }}
                    }})
                    .on('mouseout', function(event, d) {{
                        const isSelected = this.classList.contains('node-selected');
                        if (!isSelected) {{
                            d3.select(this).attr('r', 10);
                        }}
                    }});

                const labels = svg.selectAll('.label')
                    .data(graphData.nodes)
                    .enter()
                    .append('text')
                    .attr('class', 'label')
                    .attr('text-anchor', 'middle')
                    .attr('dy', '1.5em')
                    .style('font-size', '12px')
                    .style('pointer-events', 'none')
                    .text(d => d.label);

                simulation.on('tick', () => {{
                    links
                        .attr('x1', d => d.source.x)
                        .attr('y1', d => d.source.y)
                        .attr('x2', d => d.target.x)
                        .attr('y2', d => d.target.y);

                    nodes
                        .attr('cx', d => d.x)
                        .attr('cy', d => d.y);

                    labels
                        .attr('x', d => d.x)
                        .attr('y', d => d.y);
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

                const g = svg.append('g');
                svg.selectAll('line').each(function() {{
                    g.node().appendChild(this);
                }});
                svg.selectAll('circle').each(function() {{
                    g.node().appendChild(this);
                }});
                svg.selectAll('text').each(function() {{
                    g.node().appendChild(this);
                }});

                svg.call(d3.zoom()
                    .scaleExtent([0.1, 10])
                    .on('zoom', (event) => {{
                        g.attr('transform', event.transform);
                    }}));
            }})();
        </script>
        """

        return html