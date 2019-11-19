import os
import XML_Parse as parse

from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#######################################################################################################################

# Branch Number Analysis required functions:

def branch_count_per_node(root):
    """Function to determine the number of branches per node, middle nodes will have 1 branch and end nodes will be marked as blank as they will not have branches"""

    edge_source = parse.start_node(root)
    branch_count_per_node_dict = Counter(edge_source)

    return branch_count_per_node_dict

def branch_points_per_skeleton(root):
    """Function that returns the number of branch points per skeleton as a list"""

    # Creating a dictionary that contains node ID as a key and the number of times it appears as a source as its value:
    branch_num_per_node_dict = branch_count_per_node(root)

    # Creating a dictionary of node IDs that appear 2 or more times as an edge source as these nodes are branching nodes:
    branch_point_dict = {k:v for k,v in branch_num_per_node_dict.items() if v >=2}

    # Returning a list of branch points, or nodes that branch into two or more processes:
    branch_points = [i for i in branch_point_dict.keys()]

    return branch_points

def branch_number_per_skeleton(root):
    """Purpose of function is to save a csv with the skeleton ID, soma ID, total branch number per skeleton and the total branch points per skeleton"""

    # Finding the number of end nodes based on nodes that appear as a target node but not as a source node, the length of this list will be used as the total branch number
    end_nodes_list = parse.end_points(root)
    # Determing the number of end nodes for each skeleton which is the number of branches per skeleton:
    total_branches_per_skeleton = [len(end_nodes_list)]

    # Finding the Soma based on the node with the maximum radius:
    soma = parse.find_soma(root)

    # Finding the total number of branch points in the skeleton, based on the number of branching nodes:
    branching_points = branch_points_per_skeleton(root)
    total_branching_points = [len(branching_points)]

    # Creating a pandas dataframe as an output:
    skeleton_branches_df = pd.DataFrame(list(zip(parse.skeleton_id(root), soma, total_branches_per_skeleton, total_branching_points)), columns = ['Skeleton ID', 'Soma ID', 'Total Number of Branches', 'Total Number of Branch Points'])

    return skeleton_branches_df

def skeleton_branch_number_histogram(file):
    """Function to create a matplotlib histogram of the distribution of branch numbers"""

    # Opening the total branches per skeleton csv as a pandas dataframe:
    branch_data = pd.read_csv(file)

    # Creating a histogram from the previous data:
    branch_data.hist(column = 'Total Number of Branches', grid = False, color = '#86bf91', zorder = 2, rwidth = 0.9)
    plt.xlabel("Total Number of Branches")
    plt.ylabel("Number of Neurons")

    # Saving the histogram as an .eps file:
    plt.savefig('branch_number_per_skeleton.pdf')

#######################################################################################################################


