import os
import XML_Parse as parse

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

#######################################################################################################################

# Data Management and Organization:

def end_pt_df(root):
    """Function to create a dataframe of the coordinates of the end points within a skeleton"""

    # Creating a dataframe of the each node coordinates and their ID:
    node_position_df = parse.node_pos_df(root)

    # Filtering the dataframe to only include endpoints and associated coordinates (the end nodes will be used to deterine if branch is apical or basal):
    end_nodes_list = parse.end_points(root)
    endpoints = node_position_df['Node ID'].isin(end_nodes_list)
    endpoints_position_df = node_position_df[endpoints]

    return endpoints_position_df

#######################################################################################################################

# Data Analysis:

def apical_basal_classifier(root):
    """Function to classify skeleton branches as either apical or basal based on the position of the branches end node in comparison to the soma"""

    # Creating a dataframe of the each node coordinates and their ID:
    endpoints_position_df = end_pt_df(root)
    # Determining the Soma of each skeleton and creating a dataframe with its position:
    soma_df = parse.soma_df(root)

    # Creating an empty list that will contain whether each end node is apical or basal and two variables to represent the y positions of soma and end nodes:
    class_list = []
    endpts_y = endpoints_position_df.loc[:, ('y')]
    soma_y = soma_df.loc[:, ('y')]
    # Comparing the position of the end node and the soma to determine if the branch is apical or basal
    for value in endpts_y:
        for soma in soma_y:
            if value > soma:
                class_list.append('Apical')
            if value < soma:
                class_list.append('Basal')
            if value == soma:
                class_list.append('Uncategorized')
    # Creating one final dataframe containing the positions and classifications:
    endpoints_position_df['Classification'] = class_list
    skeleton_df = pd.DataFrame(parse.skeleton_id(root), columns=['Skeleton ID'])
    endpoints_position_df.reset_index(drop=True, inplace=True)
    classification_df = pd.concat([endpoints_position_df, skeleton_df], axis=1)

    return classification_df

def nodes_from_soma(root):
    """Function to determine the nodes coming directly off of the soma"""

    # Determining the Soma of the skeleton:
    soma_id = parse.find_soma(root)

    # Creating a dataframe with all of the nodes and their connections, this will be used to find what the soma is connected to:
    source_target_df = parse.source_target_pos_df(root)
    soma_df = source_target_df.loc[source_target_df['Source ID'].isin(soma_id)]
    # Determining which of the nodes are apical and basal depending on their 'y' position:
    class_list = []
    soma = soma_df.loc[0, 'y_x']
    branch_nodes = soma_df.drop(['Source ID', 'x_x', 'y_x', 'z_x'], axis=1)
    bny_columns = list(branch_nodes.loc[:, 'y_y'])
    for value in bny_columns:
        if value > soma:
            class_list.append('Apical')
        if value < soma:
            class_list.append('Basal')
        if value == soma:
            class_list.append('Uncategorized')

    # Creating one final dataframe containing the new information:
    soma_df['Classification'] = class_list
    skeleton_df = pd.DataFrame(parse.skeleton_id(root), columns=['Skeleton ID'])
    soma_df.reset_index(drop=True, inplace=True)
    classification_df = pd.concat([soma_df, skeleton_df], axis=1)

    return classification_df

def nodes_from_soma_dict(root):
    """Purpose to create a dict of the soma's target node and its apical/basal classification"""

    ab_class_node = nodes_from_soma(root)
    ab_class_dict = dict(zip(ab_class_node.loc[:, 'Target ID'], ab_class_node.loc[:, 'Classification']))

    return ab_class_dict

#######################################################################################################################

# Visualization

def ab_barchart(root):
    """Purpose of the function is to create a plotly bar chart of the distribution of apical/basal dendrites"""

    # Getting the number of apical/basal branches per skeleton:
    apical_list = []
    basal_list = []
    skeleton_list_int = parse.skeleton_id(parse.root)
    skeleton_list = []
    for i in skeleton_list_int:
        i_string = 'ID ' + str(i)
        skeleton_list.append(i_string)
    for thing in parse.root.iter('thing'):
        # Creating lists to count the number of time Apical and Basal appears within each Skeleton
        skeleton_class_df = apical_basal_classifier(thing)
        classes = skeleton_class_df['Classification'].tolist()
        # Counting how many Apical / Basal branches appear:
        apical_count = classes.count('Apical')
        basal_count = classes.count('Basal')
        # Appending the total counts:
        apical_list.append(apical_count)
        basal_list.append(basal_count)

    # Configuring the bar chart:
    classification_fig = go.Figure(data=[
        go.Bar(name='Apical', x=skeleton_list, y=apical_list),
        go.Bar(name='Basal', x=skeleton_list, y=basal_list)
    ])
    # Changing labels and chart:
    classification_fig.update_layout(barmode='stack')
    classification_fig.update_layout(
        title="Number of Apical and Basal Branches per Neuron",
        xaxis_title='Skeleton ID',
        yaxis_title='Total Number of Branches'
    )

    classification_fig.show()

def overlaid_histogram(root):
    """creates a histogram of the distribution of apical and basal branches within a data set"""
    # Getting the number of apical/basal branches per skeleton:
    apical_list = []
    basal_list = []
    for thing in parse.root.iter('thing'):
        # Creating lists to count the number of time Apical and Basal appears within each Skeleton
        skeleton_class_df = apical_basal_classifier(thing)
        classes = skeleton_class_df['Classification'].tolist()
        # Counting how many Apical / Basal branches appear:
        apical_count = classes.count('Apical')
        basal_count = classes.count('Basal')
        # Appending the total counts:
        apical_list.append(apical_count)
        basal_list.append(basal_count)

    class_histo = go.Figure()
    class_histo.add_trace(go.Histogram(x=apical_list, name='Apical'))
    class_histo.add_trace(go.Histogram(x=basal_list, name='Basal'))

    # Overlay both histograms
    class_histo.update_layout(barmode='overlay')
    # Reduce opacity to see both histograms
    class_histo.update_traces(opacity=0.50)

    class_histo.update_layout(
        title="Apical and Basal Branch Frequency",
        xaxis_title='Number of Neurons',
        yaxis_title='Frequency of Branch Type'
    )

    class_histo.show()

#######################################################################################################################