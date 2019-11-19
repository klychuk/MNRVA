import os
from collections import Counter
from xml.etree import ElementTree as ET

import operator
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#######################################################################################################################
# Provide the path to the annotation XML file in the following line within the (" ")

tree = ET.parse("/media/Nova/data_katrina/test_space/mouse_annotation.xml")
root = tree.getroot()

#######################################################################################################################

# Required Functions:

def merge(start_node, end_node):
    merged_list = []
    for i in range(max((len(start_node), len(end_node)))):

        while True:
            try:
                tup = (start_node[i], end_node[i])
            except IndexError:
                if len(star_node) > len(end_node):
                    end_node.append('')
                    tup = (start_node[i], end_node[i])
                elif len(start_node) < len(end_node):
                    edges.append('')
                    tup = (start_node[i], end_node[i])
                continue

            merged_list.append(tup)
            break
    return merged_list

def dict_search(myDict, comment):
    """The purpose of this function is to take the input item_search and return that value's key from a dictionary"""

    for key, value in myDict.items():
        if comment in value:
            return key

#######################################################################################################################

# Parsing through XML file for skeleton information:

def skeleton_id(root):
    skeleton_ids = [thing.attrib['id'] for thing in root.iter('thing')]
    return skeleton_ids

#######################################################################################################################

# Parsing through XML file for node information:

def node_id(root):
    node_id = [thing.attrib['id'] for thing in root.iter('node')]
    return node_id

def node_radius(root):
    node_radius = [float(i) for i in [thing.attrib['radius'] for thing in root.iter('node')]]
    return node_radius

def node_position_dict(root):
    position = {}
    for thing in root.iter("node"):
        x = int(thing.attrib['x'])
        y = int(thing.attrib['y'])
        z = int(thing.attrib['z'])
        node_id = int(thing.attrib['id'])
        position[node_id] = (x, y, z)
    return position

def comments(root):
    comments = []
    for node in root.iter('node'):
        try:
            if node.attrib['comment']:
                comments.append(node.attrib['comment'])
        except(KeyError):
            comments.append('.')
            continue
    return comments

#######################################################################################################################

# Parsing through XML file for edge information:

def start_node(root):
    start_node_vector = [thing.attrib['source'] for thing in root.iter('edge')]
    return start_node_vector

def end_node(root):
    end_node_vector = [thing.attrib['target'] for thing in root.iter('edge')]
    return end_node_vector

def edge_connect(root):
    edge_connect_vector = ((merge(start_node, end_node)) for thing in root.iter('edge'))
    return edge_connect_vector

def find_soma(root):

    # Creating a list of node IDs:
    node_ids = node_id(root)

    # Creating a dictionary of each node and its associated radius from the node ID list and radius list:
    node_radius_list = node_radius(root)
    node_radius_dict = dict(zip(node_ids, node_radius_list))

    # Creating a dictionary of each node and it associated comments from the node ID list and comment list:
    node_comments = comments(root)
    comments_lowercase = [x.lower() for x in node_comments]
    node_comments_dict = dict(zip(node_ids, comments_lowercase))

    # Finding the Soma ID by searching through the comments
    soma_ID = []
    soma_ID.append(dict_search(node_comments_dict, 'soma'))
    for x in soma_ID:
        if x is None:
            soma_ID.remove(x)
            soma_ID.append(max(node_radius_dict, key = node_radius_dict.get))

    return soma_ID

#######################################################################################################################

# Branch Number Analysis:

def branch_number_per_node(root):

    # Counting the number of branches per skeleton above 2 branches (a node with 1 branch is counted as a middle node, not branching node):
    edge_source = start_node(root)
    branch_count_per_node = Counter(edge_source)

    # Finding the Soma based on the node with the maximum radius:
    soma = find_soma(root)

    # Creating a pandas dataframe as an output:
    skeleton_id_df = pd.DataFrame(skeleton_id(root), columns = ['Skeleton ID'])
    node_branches = pd.DataFrame(branch_count_per_node.items(), columns = ['Node ID', 'Number of Branches'])
    node_branches_df = pd.merge(skeleton_id_df, node_branches, how = 'outer', left_index = True, right_index=True)

    # Change the path of the desired operating directory (or the folder you want the csv file to be saved in)
    os.chdir('/media/Nova/data_katrina/test_space')
    filename = 'branches_per_node.csv'

    if os.path.exists(filename):
        data = pd.read_csv(filename)
        concat_data = pd.concat([data, node_branches_df], axis=1)
        concat_data.to_csv('branches_per_node.csv', index=None, header=True)
    else:
        node_branches_df.to_csv("branches_per_node.csv", index=None, header=True)

    # Printing pandas dataframe for review:
    print("Branch Number per node: ", "\n", node_branches_df)

#######################################################################################################################

print("Soma ID and Branch Number: ")
for thing in root.iter('thing'):
    print("\nSKELETON: ", thing.attrib['id'])
    branch_number_per_node(thing)
