import os
from xml.etree import ElementTree as ET
import argparse
from itertools import chain
from collections import defaultdict

import operator
import numpy as np
import pandas as pd
import networkx as nx
import plotly as py
import plotly.graph_objs as go

#######################################################################################################################
#Chunk 1
# Creating argparse requirements for running script through the python terminal:
parser = argparse.ArgumentParser(description='XML Parsing Script for Knossos Annotations')
parser.add_argument('-input', type = str , required = True , help='Path to desired Knossos XML file for analysis')
parser.add_argument('-out_dir', default= '.', help='Directory where you would like analyses saved')
parser.add_argument('-classify', type = bool, default = False, help='True/False if you want the dendrites to be classified as apical or basal')
parser.add_argument('-visual', type = bool, default = False, help='True/False If you want graphical representaions of your neurons')


args = parser.parse_args()

output_file = args.out_dir
os.chdir(output_file)
# Printing given input file path for user confirmation:
print('\nInput file: ', args.input, '\n')


#######################################################################################################################
#Chunk2
# Using Element tree to parse through the give input XML file:

tree = ET.parse(args.input)
root = tree.getroot()

#######################################################################################################################
#Chunk3
# Required Functions for data management and storage:

def merge(start_node, end_node):
    """Function to merge two lists together and output a merged list"""

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

def keep_dict_keys_in_list(dict, list):
    """Function that removes keys from a dictionary that are not present in a separate list"""

    for key in dict.keys():
        if key in list:
            continue
        else:
            dict.pop(key)
            break
    return dict

def dict_value_replace(dict, key_vector, new_value):
    """Parse through dictionary and replace the old value with a new value"""

    for key in dict.keys():
        if key == key_vector:
            dict[ key ] = new_value

def mergeDict(dict1, dict2):
    """Merges two dictionaries together so that the values are appended into a list"""

    dict3 = dict1 + dict2
    for key, value in dict3.items():
        if key in dict1 and key in dict2:
            dict3[ key ] = [ value, dict1[ key ] ]

    return dict3

#######################################################################################################################
#Chunk4
# Parsing through XML file for skeleton information:

def skeleton_id(root):
    """Function to parse through XML file and return a list of skeleton IDs"""

    skeleton_ids = [thing.attrib['id'] for thing in root.iter('thing')]
    return skeleton_ids

def skeleton_comment(root):
    """Function to parse through XML for skeleton comments"""
    skeleton_comments = [ ]
    for thing in root.iter('thing'):
        try:
            if thing.attrib[ 'comment' ]:
                skeleton_comments.append(thing.attrib[ 'comment' ])
        except(KeyError):
            skeleton_comments.append('.')
            continue

    return skeleton_comments

#######################################################################################################################
#chunk5
# Parsing through XML file for node information:

def node_id(root):
    """Function to parse through XML file and return a list of node IDs"""

    node_id = [thing.attrib['id'] for thing in root.iter('node')]
    return node_id

def node_radius(root):
    """Function that returns a list of node radiuses for a skeleton"""

    node_radius = [float(i) for i in [thing.attrib['radius'] for thing in root.iter('node')]]

    return node_radius

def node_position_dict(root):
    """Parses through the XML file to create a dictionary of nodes (keys) and their X, Y, Z coordinates (values)"""

    position = {}
    for thing in root.iter("node"):
        x = int(thing.attrib['x'])
        y = int(thing.attrib['y'])
        z = int(thing.attrib['z'])
        node_id = int(thing.attrib['id'])
        position[node_id] = (x, y, z)
    return position

def node_pos_df(root):
    """Function to create a pandas dataframe with all the node and their x,y,z coordinates"""

    node_positions = node_position_dict(root)
    node_positions_df = pd.DataFrame.from_dict(node_positions, orient='index', columns=['x', 'y', 'z'])
    node_positions_df['Node ID'] = node_positions_df.index
    node_positions_df['Node ID'] = node_positions_df['Node ID'].astype(int)

    return node_positions_df

def comments(root):
    """Function to parse through XML and return a list of node comments for each skeleton, should there be no comment, the function appends a '.' for the node"""

    comments = []
    for node in root.iter('node'):
        try:
            if node.attrib['comment']:
                comments.append(node.attrib['comment'])
        except(KeyError):
            comments.append('.')
            continue

    return comments

def comment_dict(root):
    """Function to create a dictionary of node and associated comments"""

    comments_dict = {}
    for node in root.iter('node'):
        node_id = (node.attrib['id'])
        commentstr = comments(root)
        comments_dict[node_id] = (commentstr)

    return comments_dict

def node_information_dict(root):
    """Parses through the XML file to create a dictionary of nodes (keys) and their radiuses"""

    information = {}
    for thing in root.iter("node"):
        x = float(thing.attrib['x'])
        y = float(thing.attrib['y'])
        z = float(thing.attrib['z'])
        radius = float(thing.attrib['radius'])
        node_id = (thing.attrib['id'])
        information[node_id] = (x, y, z, radius)

    return information

#######################################################################################################################
#Chunk6
# Parsing through XML file for edge information:

def start_node(root):
    """Function to return a list of source nodes for each skeleton"""

    start_node_vector = [thing.attrib['source'] for thing in root.iter('edge')]
    return start_node_vector

def end_node(root):
    """Function to return a list of target nodes for each skeleton"""

    end_node_vector = [thing.attrib['target'] for thing in root.iter('edge')]
    return end_node_vector

def end_points(root):
    """Creates a list of end points for each skeleton"""

    source_node_list = start_node(root)
    target_node_list = end_node(root)
    end_nodes_list = np.setdiff1d(target_node_list, source_node_list)

    return end_nodes_list

def edge_connect(root):
    """Creates a list of source and attached target nodes for each skeleton"""
    edge_connect_vector = (merge(start_node(thing), end_node(thing)) for thing in root.iter('edge'))
    return edge_connect_vector

#######################################################################################################################
#Chunk 7
# Parsing through XML file for Soma information:

def find_soma(root):
    """Function to determine the soma ID for each skeleton, parses through comments to see if soma was marked, if not identifies soma based on the largest node radius"""

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
    soma_ID = [ ]
    soma_ID.append(dict_search(node_comments_dict, 'soma'))
    for x in soma_ID:
        if x is None:
            soma_ID.remove(x)
            soma_ID.append(max(node_radius_dict, key=node_radius_dict.get))

    return soma_ID

def soma_df(root):
    """Creating a dataframe that contains the Soma information"""

    node_position_df = node_pos_df(root)
    # Determining the Soma of each skeleton and creating a dataframe with its position:
    Soma_ID = find_soma(root)
    soma_position = node_position_df['Node ID'].isin(Soma_ID)
    soma_df = node_position_df[ soma_position ]
    soma_df = soma_df.rename(columns={'Node ID': 'Soma ID'})

    return soma_df

#######################################################################################################################
#chunk 8
# Functions for Data Management

def source_target_pos_df(root):
    """Function to create a pandas dataframe containing the source node and associated position then the target node and associated position"""

    # Creating a list of node sources and targets (connections):
    source_list = start_node(root)
    target_list = end_node(root)
    source_df = pd.DataFrame()
    source_df['Source ID'] = source_list
    source_df['Source ID'] = source_df['Source ID'].astype(int)
    source_position_df = pd.merge(source_df, node_pos_df(root), how='left', left_on='Source ID', right_on='Node ID')
    target_df = pd.DataFrame()
    target_df['Target ID'] = target_list
    target_df['Target ID'] = target_df['Target ID'].astype(int)
    target_position_df = pd.merge(target_df, node_pos_df(root), how='left', left_on='Target ID', right_on='Node ID')
    skeleton_df = pd.DataFrame()
    skeleton_ids = skeleton_id(root)
    skeleton_comments = skeleton_comment(root)
    skeleton_df['Skeleton ID'] = skeleton_ids
    skeleton_df['Skeleton Comment'] = skeleton_comments

    source_target_df_tmp = pd.merge(source_position_df, target_position_df, left_index=True, right_index=True)
    source_target_df = source_target_df_tmp.drop(['Node ID_x', 'Node ID_y'], axis=1)

    # Combining the information into one final dataframe:
    source_target_df = pd.concat([skeleton_df, source_target_df], axis=1)


    # Source Node and position df:
    #source_df = pd.DataFrame(source_list, columns=['Source ID'])
    #source_df['Source ID'] = source_df[ 'Source ID' ].astype(int)
    #source_position_df = pd.merge(source_df, node_pos_df(root), how='left', left_on='Source ID', right_on='Node ID')
    # Target Node and position df:
    #target_df = pd.DataFrame(target_list, columns=[ 'Target ID' ])
    #target_df['Target ID'] = target_df[ 'Target ID' ].astype(int)
    #target_position_df = pd.merge(target_df, node_pos_df(root), how='left', left_on='Target ID', right_on='Node ID')

    # Source and Target final df:
    #source_target_df_tmp = pd.merge(source_position_df, target_position_df, left_index=True, right_index=True)
    #source_target_df = source_target_df_tmp.drop(['Node ID_x', 'Node ID_y'], axis=1)

    return source_target_df

def skeleton_information(root):
    """Creates a dataframe with skeleton and node information"""

    # Creating lists for node ID, radius, x,y,z coordinates, and comments
    node_ids = node_id(root)
    node_radii = node_radius(root)
    node_comments = comments(root)
    node_x = [thing.attrib['x'] for thing in root.iter('node')]
    node_y = [thing.attrib['y'] for thing in root.iter('node')]
    node_z = [thing.attrib['z'] for thing in root.iter('node')]
    # Creating a dataframe of the above created information:
    node_information_df = pd.DataFrame()
    node_information_df['Node ID'] = node_ids
    node_information_df['X'] = node_x
    node_information_df['Y'] = node_y
    node_information_df['Z'] = node_z
    node_information_df['Radius'] = node_radii
    node_information_df['Node Comment'] = node_comments
    # Creating a dataframe with the skeleton information:
    skeleton_ids = skeleton_id(root)
    skeleton_comments = skeleton_comment(root)
    skeleton_df = pd.DataFrame()
    skeleton_df['Skeleton ID'] = skeleton_ids
    skeleton_df['Skeleton Comment'] = skeleton_comments
    # Combining the information into one final dataframe:
    XML_info_df = pd.concat([skeleton_df, node_information_df], axis=1)

    return XML_info_df

def node_horizontal_list(root):
    """Function to create a list of all the node information (id, radius, x, y, z, comment)"""

    node_info = [ ]
    # Parsing through each of the nodes for the required information:
    for node in root.iter('node'):
        node_id_vect = node.attrib['id']
        node_radius_vect = node.attrib['radius']
        x = int(node.attrib['x'])
        y = int(node.attrib['y'])
        z = int(node.attrib['z'])
        node_comment_ls = comments(node)
        # Adding all of the node information to a master nodes list:
        node_info.append(node_id_vect)
        node_info.append(node_radius_vect)
        node_info.append(x)
        node_info.append(y)
        node_info.append(z)
        node_info.extend(node_comment_ls)
    return node_info

def XML_info_node_rows(root):
    """The purpose of this function is to produce a csv file containing all the XML file data with nodes aligned by row rather than by column"""

    # First thing to do is to create a list with the skeleton information:
    final_df = pd.DataFrame()
    for thing in root.iter('thing'):
        skeleton_ids = thing.attrib['id']
        skeleton_comments = skeleton_comment(thing)
        # Creating a list of node information per skeleton:
        node_info = node_horizontal_list(thing)
        # Compiling all of the information into a single final list:
        final_list = [ ]
        final_list.append(skeleton_ids)
        final_list.extend(skeleton_comments)
        final_list.extend(node_info)
        # Compiling the list into a dataframe with each skeleton as a row:
        final_df = final_df.append(pd.Series(final_list), ignore_index=True)
    # Renaming all of the columns within the final dataframe (MAX of 3 nodes in the dataset for this dataframe):
    final_df.columns = ["Skeleton ID", "Skeleton Comments", "Node_1 ID", "Node_1 Radius", "X_1", "Y_1", "Z_1",
                        "Node_1 Comment", "Node_2 ID", "Node_2 Radius", "X_2", "Y_2", "Z_2", "Node_2 Comment",
                        "Node_3 ID", "Node_3 Radius", "X_3", "Y_3", "Z_3", "Node_3 Comment"]
    return final_df

#######################################################################################################################
#chunk9
# Saving Functions

def save_csv_df(dataframe, filename):
    """Function to save created dataframes to csv files"""

    if os.path.exists(filename):
        data = pd.read_csv(filename)
        concat_data = pd.concat([data, dataframe])
        concat_data.to_csv(filename, index=None, header=True)
    else:
        dataframe.to_csv(filename, index=None, header=True)

def save_node_csv_df(dataframe, filename):
    """Function to save created dataframes to csv files - horizontal orientation"""

    if os.path.exists(filename):
        data = pd.read_csv(filename)
        concat_data = pd.concat([data, dataframe], axis=1)
        concat_data.to_csv(filename, index=None, header=True)
    else:
        dataframe.to_csv(filename, index=None, header=True)

#######################################################################################################################
