import os, sys
import XML_Parse as parse
import Euclidean_Distance as ed

import operator
import numpy as np
import pandas as pd
import networkx as nx
import plotly as py
import plotly.graph_objs as go

import igraph as ig
import matplotlib.pyplot as plt

#######################################################################################################################

# Data Management for Visualization

def xy_node_position_dict(root):
    """Parses through the XML file to create a dictionary of nodes (keys) and their X, Y coordinates (values)"""

    position = {}
    for thing in root.iter("node"):
        x = int(thing.attrib['x'])
        y = int(thing.attrib['y'])
        node_id = int(thing.attrib['id'])
        position[node_id] = (x, y)
    return position

#######################################################################################################################

# Functions for visualization using Networkx and Plotly:

def network_graph_nx(root):
    """Purpose of this function is to create a Network graph for visualization of each individual object given in the KNOSSOS XML input file"""

    # Need to iterate over each of the objects in the XML file to add individual skeletons to the Networkx graph:
    final_nx_graph = nx.Graph()
    position_labels = xy_node_position_dict(root)

    for thing in parse.root.iter('thing'):
        # Creating the dataframe with node information as input:
        node_df = ed.ed_per_node(thing)

        # Designating the nodes to be used in the Network graph, using if statement to add nodes as part of separate object:
        network_graph_nx = nx.Graph()
        if nx.is_empty(network_graph_nx):
            network_graph_first = nx.from_pandas_edgelist(node_df, 'Source ID', 'Target ID', edge_attr='Euclidean Distance')
            network_graph_nx.add_edges_from(network_graph_first.edges())
            network_graph_nx.add_nodes_from(network_graph_first.nodes())
        else:
            network_graph_add = nx.from_pandas_edgelist(node_df, 'Source ID', 'Target ID', edge_attr='Euclidean Distance')
            network_graph_nx.update(network_graph_add)

        # Appending the final networkx graph and saving it as a .graphml file type:
        final_nx_graph.update(network_graph_nx)

    # Adding node attributes such as position and skeleton group:
    # positions = nx.spring_layout(final_nx_graph, dim=3, k=None, pos=position_labels, fixed=None, iterations=50, weight='weight', scale=1.0)
    nx.set_node_attributes(final_nx_graph, position_labels, name='Position')

    return final_nx_graph

def network_graph_go(root):
    """The purpose of this function is to create a Network Graph visualization with plotly"""

    # Reading in the graph created with Networkx:
    skeleton_graph = network_graph_nx(root)
    # Defining edges and edge properties:
    traced_edges = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.75, color='#888'),
        hoverinfo='none', # It appears you can change the hover information here (this would be where the distance goes)
        mode='lines')
    # Defining the position of the nodes:
    for edge in skeleton_graph.edges():
        x0, y0 = skeleton_graph.node[edge[0]]['Position']
        x1, y1 = skeleton_graph.node[edge[1]]['Position']
        traced_edges['x'] += tuple([x0, x1, None])
        traced_edges['y'] += tuple([y0, y1, None])
    # Defining the attributes of the nodes:
    traced_nodes = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2)))
    # Adding the nodes to the graph:
    for node in skeleton_graph.nodes():
        x, y = skeleton_graph.node[node]['Position']
        traced_nodes['x'] += tuple([x])
        traced_nodes['y'] += tuple([y])
    # Adding node information and color:
    for node, adjacencies in enumerate(skeleton_graph.adjacency()):
        traced_nodes['marker']['color'] += tuple([len(adjacencies[1])])
        node_id = str(node)
        node_information = 'Node ID: ' + str(node_id), '# of connections: ' + str(len(adjacencies[1])) # Thinking that this where you can add information such as node ID as well
        traced_nodes['text'] += tuple([node_information]) # Create additional variable for node id and add here
    # Creating the Network Graph visualization from the settings established above:
    skeleton_map = go.Figure(data=[traced_edges, traced_nodes],
                             layout=go.Layout(
                             title='<br>Network graph of KNOSSOS Skeletons',
                             titlefont=dict(size=16),
                             showlegend=False,
                             hovermode='closest',
                             margin=dict(b=20, l=5, r=5, t=40),
                             annotations=[dict(
                                 text="Input File: " + parse.args.in_file,
                                 showarrow=False,
                                 xref="paper", yref="paper",
                                 x=0.005, y=-0.002)], # Check how this may need to be changed in the future
                             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    skeleton_map.show()

#######################################################################################################################
