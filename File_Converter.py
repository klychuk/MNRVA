import os
import XML_Parse as parse
import Branch_Number_per_Skeleton as bn
import Apical_Basal_Classification as abclass

import pandas as pd
import numpy as np
import matplotlib as plt

#######################################################################################################################

# Data Management Functions:

def parent_node_dict(root):
    """The purpose of this function is to create a dictionary with the node as the key and its parent node as the value"""

    # Creating list of the parent nodes and target nodes:
    parent_list = parse.start_node(root)
    target_node = parse.end_node(root)
    # Creating a dictionary in which the keys are the node and the parent nodes are the value:
    node_parent = dict(zip(target_node, parent_list))

    return node_parent

def node_structure(root):
    """Function that classifies each node within a skeleton as either apical, basal, soma, fork point, end point, or undefined"""

    # Classifying node soma:
    soma_key = parse.find_soma(root)
    soma_dict = {i : 1 for i in soma_key}
    # Classifying endpoints:
    end_point_keys = parse.end_points(root)
    end_point_dict = {i : 6 for i in end_point_keys}
    # Classifying forkpoints:
    fork_pts_list = bn.branch_points_per_skeleton(root)
    fork_pts_dict = {i : 5 for i in fork_pts_list}
    # Classifying Apical and Basal Dendrites based on the position of the Soma's branches:
    ab_class_dict = abclass.nodes_from_soma_dict(root)
    ab_class_dict_int = {str(key): value for key, value in ab_class_dict.items()}
    for key, value in ab_class_dict_int.items():
        if value is 'Apical':
            ab_class_dict_int[key] = 4
        if value is 'Basal':
            ab_class_dict_int[key] = 3
        if value is 'Uncategorized':
            continue
    # Classifying middle nodes as dendrites:
    node_dict = {}
    node_ID_list = parse.node_id(root)
    # node_ID_int = [int(i) for i in node_ID_list]
    for i in node_ID_list:
        node_dict[i] = 0
    # node_dict[node_ID_list] = 0
    # Creating one final dictionary with all of the information:
    structure_dict = {}
    # structure_dict.update(parse.mergeDict(node_dict, end_point_dict))
    # structure_dict.update(parse.mergeDict(fork_pts_dict, ab_class_dict))
    structure_dict.update(node_dict)
    structure_dict.update(end_point_dict)
    structure_dict.update(fork_pts_dict)
    structure_dict.update(ab_class_dict_int)
    structure_dict.update(soma_dict)

    return structure_dict

#######################################################################################################################

def swc_file_format(root):
    """The purpose of this function is to output a csv file in the appropriate format to save as a .swc file, see the README file for what this looks like"""

    # Parsing through XML for required information and saving it as a dictionary:

    # Creating a dataframe to house the information:
    node_info_dict = parse.node_information_dict(root)
    node_df = pd.DataFrame.from_dict(node_info_dict, orient='index', columns=[ 'x', 'y', 'z', 'radius' ])

    # Creating one dictionary to house the information for each node per skeleton:
    node_parent_dict = parent_node_dict(root)
    node_parent_df = pd.DataFrame.from_dict(node_parent_dict, orient='index', columns=['Parent Sample'])
    node_structure_dict = node_structure(root)
    node_structure_df = pd.DataFrame.from_dict(node_structure_dict, orient='index', columns=['Structure Identifier'])

    # Merging it all together:
    final_df = pd.concat([node_structure_df, node_df, node_parent_df], axis=1)
    final_df.reset_index()

    return final_df

#######################################################################################################################