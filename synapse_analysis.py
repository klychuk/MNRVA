import os
import XML_Parse as parse
import Branch_Number_per_Skeleton as bnpn
import Euclidean_Distance as eud

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#######################################################################################################################

# Data Manipulation & Management

# First Identify the soma
# Then determine the nodes that branch off directly from the soma
# For each of the dendrites coming off of the soma:
    # List all of the nodes within that dendrite

def dendrite_tracing(root):
    """The purpose of this function is to trace out a single dendrite"""

    source_list = parse.start_node(root)
    target_list = parse.end_node(root)
    merged_list = parse.merge(source_list, target_list)

    # Finding nodes with 2 or more branches:
    branch_pts = bnpn.branch_count_per_node(root)
    two_or_more_branches = [k for k, v in branch_pts.items() if v >= 2]

    dendrite_node_list = []
    test = []
    for item in merged_list:
        for x in merged_list:
            if item[0] in two_or_more_branches:
                test.append(x)
            else:
                if item[0] == x[1]:
                    dendrite_node_list.append(item)

    print(dendrite_node_list)

def identify_dendrites(root):
    """The purpose of this function is to create a dataframe with all of the primary dendrites and their associated nodes and node information"""

# Attempt to separate the dendrites out by the intial node that comes off of the soma

    # Determining the Soma ID to then identify the nodes coming directly off the soma:
    Soma_ID = parse.find_soma(root)
    # Listing all the nodes within the dendrite:
    source_list = parse.start_node(root)
    target_list = parse.end_node(root)
    merged_list = parse.merge(source_list, target_list)
    # Should be able to identify the primary and secondary start of branches based on the number of source and target nodes.
        # Still not sure how to identify tertiary dendrites or so on, would need to account for higher number.


    print(merged_list)

def source_target_data_management(root):
    """The purpose of this function is to set up and organize a dataframe with source and target node information as well as the associated euclidean distance"""

    # First creates a data frame with the source and target nodes, their positions, and neuron ID:
    source_target_df_draft = eud.ed_per_node(root)
    source_target_df = source_target_df_draft.ffill(axis=0)
    # Creating node comment dictionary and adding it as a column to the source_target_df:
    comment_dict = {}
    for node in root.iter('node'):
        comments_node_dict = parse.comment_dict(node)
        comment_dict.update((comments_node_dict))
    # Setting up and organizing the comments dataframe to be merged with euclidean distance dataframe:
    comment_df = pd.DataFrame.from_dict(comment_dict, orient='index')
    comments_df = comment_df.reset_index()
    comments_df.rename(columns={'index': 'Source ID'}, inplace=True)
    comments_df.rename(columns={0: 'Source Node Comment'}, inplace=True)
    comments_df['Source ID'] = comments_df['Source ID'].astype(int)
    source_comment_final_df = source_target_df.join(comments_df.set_index('Source ID'), on='Source ID', how='inner')
    comments_df.rename(columns={'Source ID': 'Target ID'}, inplace=True)
    comments_df.rename(columns={'Source Node Comment': 'Target Node Comment'}, inplace=True)
    target_source_comment_final_df = source_comment_final_df.join(comments_df.set_index('Target ID'), on='Target ID', how='inner')
    # Adjusting column order:
    target_source_comment_final_df = target_source_comment_final_df[['Skeleton ID', 'Source ID', 'Source Node Comment',
                                                                     'x_x', 'y_x', 'z_x', 'Target ID', 'Target Node Comment',
                                                                     'x_y', 'y_y', 'z_y', 'Euclidean Distance']]

    return target_source_comment_final_df

def spine_identification(root):
    """Function to identify intermediary spine nodes based on target node comments"""

    # Setting up dataframe with all the necessary information:
    target_source_df = source_target_data_management(root)
    target_source_indexlen = target_source_df.index.size
    target_source_columns = list(target_source_df.columns)

    # Finding intermediary spine nodes that will be re-commented as spine:
    # So if target node comment contains "spine" then label node with the same target node ID as its source node ID "spine" unless that node has two or more target nodes
    # 1. Create a list of nodes with two or more target nodes:
    branch_pt_list = bnpn.branch_points_per_skeleton(root)
    # 2. find all target nodes with comments including "spine":
    resize_df = pd.DataFrame(np.nan, index=np.arange(target_source_indexlen), columns=target_source_columns)
    spine_df = target_source_df[target_source_df['Target Node Comment'].str.contains('spine', case=False)]
    # spine_reshaped_df = pd.concat([resize_df, spine_df], ignore_index=False, axis=1)
    # spine_final_df = spine_reshaped_df.dropna(how='all', axis=1)
    # 3. Comparing the two dataframes to find and relabel intermediary spine nodes:
    # if target_source_df['Target ID'] == spine_final_df['Source ID']:
    #     target_source_df['Target Node Comment'].replace('.', 'spine')
    # print(target_source_df.isin(spine_final_df))
    spine_list = list(spine_df['Source ID'])

    print(target_source_df['Target ID'].isin(spine_list))
    target_source_df['Spine'] = target_source_df['Target ID'].isin(spine_list)
    # data = target_source_df.replace(to_replace=['.'], value=np.nan)
    data = pd.DataFrame()
    if target_source_df['Spine'] is 'True':
        target_source_df['Source Node Comment'].replace(to_replace=['.'], value='spine')
        # data = data.append(replace_df, ignore_index=True)
    # target_source_df['Spine'] = np.where((target_source_df['Target ID'] in spine_list, 1, np.nan))

    print(target_source_df)
    # print(target_source_df)
    # print(spine_final_df)


#######################################################################################################################

# DELETE THIS WHEN DONE:

for thing in parse.root.iter('thing'):
    spine_identification(thing)

# for thing in parse.root.iter('thing'):
#     final_df = source_target_data_management(thing)
#     parse.save_csv_df(final_df, 'source_target.csv')

