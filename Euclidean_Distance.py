import os
import XML_Parse as parse

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#######################################################################################################################

# Analysis Functions

def euclidean_distance_formula(x1,y1,z1,x2,y2,z2):
    """The purpose of this script is to apply the euclidean distance formula to a set of x,y,z coordinates"""

    edt = np.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)
    return edt

def ed_per_node(root):
    """The purpose of this function is to find the distance between each source and target node within a skeleton"""

    # Creating dataframe with skeleton ID:
    skeleton_id_df = pd.DataFrame(parse.skeleton_id(root), columns=['Skeleton ID'])

    # Converting the lists to one pandas dataframe that will contain source node, its position, target node, and its position:
    source_target_df = parse.source_target_pos_df(root)
    # Applying EDT formula:
    edt_list = euclidean_distance_formula(source_target_df['x_x'],source_target_df['y_x'],source_target_df['z_x'],source_target_df['x_y'],source_target_df['y_y'],source_target_df['z_y'])
    source_target_df['Euclidean Distance'] = edt_list
    # Adding a column to the dataframe for skeleton ID
    source_target_df_final = pd.concat([skeleton_id_df, source_target_df], axis=1)

    return source_target_df_final

def ed_per_skeleton(root):
    """Function to find the total distance between source and target nodes per skeleton, this will sum the distance ouput of the previous function (ed_per_node)"""

    # Creating the pandas dataframe with source/target node euclidean distance and positions:
    source_target_pos_df = ed_per_node(root)

    # Summing the Euclidean Distance per skeleton and creating a separate dataframe with the new information:
    ed_total = [source_target_pos_df['Euclidean Distance'].sum()]
    # Creation of Final Data Frame with skeleton ID:
    ed_per_skeleton_df = pd.DataFrame(parse.skeleton_id(root), columns=['Skeleton ID'])
    ed_per_skeleton_df['Total Euclidean Distance'] = ed_total

    return ed_per_skeleton_df

def ed_histogram(file):
    """Function to create a matplotlib histogram of the distribution of the total euclidean distance of each skeleton"""

    # Opening the total branches per skeleton csv as a pandas dataframe:
    branch_data = pd.read_csv(file)

    # Creating a histogram from the previous data:
    branch_data.hist(column = 'Total Euclidean Distance', grid = False, color = '#86bf91', zorder = 2, rwidth = 0.9)
    plt.xlabel("Euclidean Distance Sum per Skeleton")
    plt.ylabel("Number of Neurons")

    # Saving the histogram as an .eps file:
    plt.savefig('euclidean_distance_per_skeleton.pdf')

#######################################################################################################################


