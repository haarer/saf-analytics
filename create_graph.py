#!/usr/bin/env python3
"""
create_graph.py
--------------
Create a graph from viewpoint, stakeholder, and concern files using NetworkX.
The script resolves relationships using UIDs.
"""

import argparse
import json
from pathlib import Path

import networkx as nx


def load_json_file(filepath: Path) -> dict:
    """Load a JSON file and return its contents as a dictionary."""
    with filepath.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data


def create_graph(viewpoints_data, stakeholders_data, concerns_data):
    """Create a directed graph from viewpoint, stakeholder, and concern data."""
    graph = nx.DiGraph()

    # Add viewpoints to the graph
    for viewpoint in viewpoints_data:
        viewpoint_id = viewpoint.get("ID", "")
        viewpoint_name = viewpoint.get("Name", "")
        if viewpoint_id:
            graph.add_node(viewpoint_id, type="viewpoint", name=viewpoint_name)

    # Add stakeholders to the graph
    for stakeholder in stakeholders_data:
        stakeholder_id = stakeholder.get("ID", "")
        stakeholder_name = stakeholder.get("Name", "")
        if stakeholder_id:
            graph.add_node(stakeholder_id, type="stakeholder", name=stakeholder_name)

    # Add concerns to the graph
    for concern in concerns_data:
        concern_id = concern.get("ID", "")
        concern_name = concern.get("Name", "")
        if concern_id:
            graph.add_node(concern_id, type="concern", name=concern_name)

    # Resolve relationships using UIDs
    for viewpoint in viewpoints_data:
        viewpoint_id = viewpoint.get("ID", "")
        stakeholders = viewpoint.get("Stakeholders", [])
        concerns = viewpoint.get("Concern", [])

        if viewpoint_id:
            # Connect viewpoint to stakeholders
            for stakeholder_uid in stakeholders:
                if stakeholder_uid in graph.nodes:
                    graph.add_edge(viewpoint_id, stakeholder_uid, relationship="has_stakeholder")

            # Connect viewpoint to concerns
            for concern_uid in concerns:
                if concern_uid in graph.nodes:
                    graph.add_edge(viewpoint_id, concern_uid, relationship="has_concern")

    return graph


def save_graph(graph, output_path: Path):
    """Save the graph to a file."""
    nx.write_gexf(graph, output_path)
    print(f"Graph saved to {output_path}")


def visualize_with_pyvis(graph, output_dir: Path):
    """Visualize the graph using PyVis and save as an HTML file."""
    try:
        from pyvis.network import Network
        # Create a PyVis network
        net = Network(notebook=True, directed=True, cdn_resources="in_line")

        # Add nodes with their attributes
        for node in graph.nodes(data=True):
            net.add_node(node[0], label=node[1].get("name", ""), title=str(node[1]))

        # Add edges with their relationships
        for edge in graph.edges(data=True):
            net.add_edge(edge[0], edge[1], title=edge[2].get("relationship", ""))

        # Save the visualization to an HTML file
        html_path = output_dir / "graph_visualization.html"
        net.save_graph(str(html_path))  # Convert Path to string to avoid the error
    except ImportError:
        print("PyVis is not installed. Skipping visualization.")
        return

    # Create a PyVis network
    net = Network(notebook=False, directed=True, cdn_resources="remote")

    # Add nodes and edges to the network
    for node in graph.nodes(data=True):
        node_id, data = node
        node_type = data.get("type", "unknown")
        node_name = data.get("name", node_id)
        color = "#FF6B6B" if node_type == "viewpoint" else ("#4ECDC4" if node_type == "stakeholder" else "#FFE66D")
        net.add_node(node_id, label=node_name, title=f"Type: {node_type}", color=color)

    for edge in graph.edges(data=True):
        source, target, data = edge
        relationship = data.get("relationship", "unknown")
        net.add_edge(source, target, title=relationship)

    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save the visualization to an HTML file
    output_file = output_dir / "graph_visualization.html"
    net.save_graph(str(output_file))
    print(f"Graph visualization saved to {output_file}")


def main():
    # Default paths for input files
    viewpoints_path = Path("../SAF-Specification/src/_data/viewpoints.json")
    stakeholders_path = Path("../SAF-Specification/src/_data/stakeholders.json")
    concerns_path = Path("../SAF-Specification/src/_data/concerns.json")

    # Load data from files
    viewpoints_data = load_json_file(viewpoints_path)
    stakeholders_data = load_json_file(stakeholders_path)
    concerns_data = load_json_file(concerns_path)

    # Create graph
    graph = create_graph(viewpoints_data, stakeholders_data, concerns_data)

    # Save graph to default output file
    output_path = Path("graph.gexf")
    save_graph(graph, output_path)

    # Visualize the graph using PyVis and save to a subdirectory
    webvis_dir = Path("webvis")
    visualize_with_pyvis(graph, webvis_dir)

    print(f"Graph created with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")


if __name__ == "__main__":
    main()