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

    print(f"Graph created with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")


if __name__ == "__main__":
    main()