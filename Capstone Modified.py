import os, sys
from datetime import datetime
import XML_Parse as parse
from treelib import Node, Tree
import itertools

import matplotlib.pyplot as plt
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np

#######################################################################################################################

## Data Management and Organization:

starttime_bc = datetime.now()
root = parse.root

## Create source target dataframe:
source_target_df = pd.DataFrame()
for thing in parse.root.iter("thing"):
    source_target_df = source_target_df.append(parse.source_target_pos_df(thing), ignore_index=True)

# Rename columns to have no spaces in names:
source_target_df.rename(columns = {"Skeleton ID": "Skeleton_ID", "Skeleton Comment": "Skeleton_Comment",
                                   "Source ID": "Source_ID", "Target ID": "Target_ID"}, inplace = True)

# Fill empty cells in Skeleton ID column to have last filled value:
source_target_df.fillna(method = "ffill")
source_target_df.Skeleton_ID = source_target_df.Skeleton_ID.ffill()

# Make node ID values integers:
source_target_df["Skeleton_ID"] = source_target_df["Skeleton_ID"].astype(str).astype(int)
source_target_df["Source_ID"] = source_target_df["Source_ID"].astype(str).astype(int)
source_target_df["Target_ID"] = source_target_df["Target_ID"].astype(str).astype(int)


## Create skeleton dataframe:
XML_final_df = pd.DataFrame()
for thing in parse.root.iter("thing"):
    XML_final_df = XML_final_df.append(parse.skeleton_information(thing), ignore_index=True)

# Rename columns to have no spaces in names:
XML_final_df.rename(columns = {"Skeleton ID": "Skeleton_ID", "Skeleton Comment":"Skeleton_Comment",
                               "Node ID":"Node_ID", "Node Comment":"Node_Comment"}, inplace = True)

# Fill empty cells in Skeleton ID column to have last filled value:
XML_final_df.fillna(method = "ffill")
XML_final_df.Skeleton_ID = XML_final_df.Skeleton_ID.ffill()

# Make all node comments lowercase:
XML_final_df["Node_Comment"] = XML_final_df["Node_Comment"].str.lower()

# Make node ID values integers:
XML_final_df["Skeleton_ID"] = XML_final_df["Skeleton_ID"].astype(str).astype(int)
XML_final_df["Node_ID"] = XML_final_df["Node_ID"].astype(str).astype(int)


## Create soma dataframe:
soma_df = XML_final_df[XML_final_df["Node_Comment"].str.contains("soma|first node")]

# Make node ID values integers:
soma_df["Skeleton_ID"] = soma_df["Skeleton_ID"].astype(str).astype(int)
soma_df["Node_ID"] = soma_df["Node_ID"].astype(str).astype(int)


## Make lists from dataframes:
soma_list = list(soma_df["Node_ID"])
node_list = list(XML_final_df["Node_ID"])
skeleton_list = list(XML_final_df["Skeleton_ID"])
source_list = list(source_target_df["Source_ID"])
target_list = list(source_target_df["Target_ID"])
skeleton_source_target_list = list(source_target_df["Skeleton_ID"])

## Make dictionaries from lists:
# Make dictionary from nodes and associated skeletons:
skeleton_dict = {node_list[i]: skeleton_list[i] for i in range(len(node_list))}

#Make dictionary from source nodes and associated skeletons:
source_skeleton_dict = {source_list[i]: skeleton_source_target_list[i] for i in range(len(source_list))}


## Find tracing errors:
# Subset data frame to find instances where Source ID is greater than Target ID (tracing error #1):
errors = source_target_df[source_target_df["Source_ID"] > source_target_df["Target_ID"]]

# Make list of skeletons with errors and remove duplicates:
skeleton_errors_list = errors["Skeleton_ID"]
skeleton_errors_list = list(dict.fromkeys(skeleton_errors_list))

# Find source nodes that are never target nodes (tracing error #2):
missing_nodes = []
for node in source_list:
    if node not in target_list:
        missing = node
        missing_nodes.append(missing)

# Remove missing nodes if they are the soma:
final_missing_nodes = []
for node in missing_nodes:
    if node not in soma_list:
        final_missing = node
        final_missing_nodes.append(final_missing)

# Remove duplicated nodes in list:
final_missing_nodes = list(dict.fromkeys(final_missing_nodes))

# Find skeleton ID asssocialted with missing nodes:
for key, value in source_skeleton_dict.items():
    if key in final_missing_nodes:
        error = value
        skeleton_errors_list.append(error)

# Remove duplicate nodes in list:
skeleton_errors_list = list(dict.fromkeys(skeleton_errors_list))

# Provide user with number of errors:
if len(skeleton_errors_list) > 0:
    print("There were " + str(len(skeleton_errors_list)) + " skeletons that could not be processed." )
    print("Skeleton information for these " + str(len(skeleton_errors_list)) + " skeletons will be output to a file named 'Unprocessed_Skeleton_Information.csv'.")
    print("\nThe program will proceed with processing the remaining " +  str(len(soma_list)-len(skeleton_errors_list)) + " skeletons.")
else:
    print("The program will proceed with processing " + str(len(soma_list)) + " skeletons.")


## Make new dataframes without problematic skeltons:
soma_df_new = soma_df[~soma_df['Skeleton_ID'].isin(skeleton_errors_list)]
soma_list_new = list(soma_df_new["Node_ID"])
source_target_df_new = source_target_df[~source_target_df['Skeleton_ID'].isin(skeleton_errors_list)]
source_target_df_errors = source_target_df[source_target_df['Skeleton_ID'].isin(skeleton_errors_list)]

# Save problematic skeletons to CSV file:
source_target_df_errors.to_csv('Unprocessed_Skeleton_Information.csv', index=False)


## Format data for tree structure:
# Split full data frame into list of data frames for each skeleton:
skeleton_info_list = []
for skeleton, source_target_df_new in source_target_df_new.groupby("Skeleton_ID"):
    skeleton_info_list.append(source_target_df_new)

# Create dictionary for somas within skeleton:
somas_dict_list = []
for soma in soma_list_new:
    soma_dict = {soma: {"parent": None}}
    somas_dict_list.append(soma_dict)

# Iterate through skeletons to store parent information:
all_parents_dict_list = []
for df in skeleton_info_list:
    source_list_indiv = list(df["Source_ID"])
    target_list_indiv = list(df["Target_ID"])
    source_target_dict_indiv = {target_list_indiv[i]: source_list_indiv[i] for i in range(len(target_list_indiv))}
    # Create separate dictionaries for nodes within each skeleton:
    parents_dict = {}
    for key, value in source_target_dict_indiv.items():
        source = key
        target = value
        parent_dict = {source: {"parent": target}}
        parents_dict.update(parent_dict)
    # Create final list of dictionaries with parent information for each skeleton:
    all_parents_dict_list.append(parents_dict)

# Add soma parent information to each associated skeleton parent information:
for i in range(len(somas_dict_list)):
    all_parents_dict_list[i].update(somas_dict_list[i])

#######################################################################################################################

## Create Tree Data Structures:

tree_list = []
for node in all_parents_dict_list:
    node_dict = node
    added = set()
    tree = Tree()
    while node_dict:
        for key, value in node_dict.items():
            if value['parent'] in added:
                tree.create_node(key, key, parent=value['parent'])
                added.add(key)
                node_dict.pop(key)
                break
            elif value['parent'] == None:
                tree.create_node(key, key)
                added.add(key)
                node_dict.pop(key)
                break
    tree_list.append(tree)

### Make into flag option
# Save tree structures to text file:
for tree in tree_list:
    tree.save2file("Processed_Skeleton_Trees.txt")

#######################################################################################################################

## Node classification processing:

# Identify end nodes (leaves):
leaf_list = []
for i in range(len(tree_list)):
    tree = tree_list[i]
    leaves = tree.leaves(nid=None)
    for leaf in leaves:
        leaf = leaf.identifier
        leaf_list.append(leaf)

# Identify paths to leaves:
paths_list = []
for i in range(len(tree_list)):
    tree = tree_list[i]
    paths = tree.paths_to_leaves()
    paths_list.append(paths)

# Identify branch points:
branch_list = list(set([x for x in source_list if source_list.count(x) > 1]))

# Remove somas from branch list:
final_branch_list = []
for node in branch_list:
    if node not in soma_list:
        final_branch = node
        final_branch_list.append(final_branch)

# Create classification variable for branch nodes:
branch_node_classifications = []
for node in node_list:
    if node in branch_list:
        classification = "yes"
        branch_node_classifications.append(classification)
    else:
        classification = "no"
        branch_node_classifications.append(classification)

# Add branch node classification column to data frame:
XML_final_df["Branch_node?"] = branch_node_classifications


### Make into flag option
# Count number of branches per skeleton:
skeleton_branch_count = []
for key, value in source_skeleton_dict.items():
    if key in final_branch_list:
        skeleton = value
        skeleton_branch_count.append(skeleton)

# Make dictionary with number of branch nodes per skeleton:
skeleton_branch_count_dict = dict((x, skeleton_branch_count.count(x)) for x in set(skeleton_branch_count))

# Make bar graph to show distribution of number of branch nodes per skeleton:
keys = skeleton_branch_count_dict.keys()
keys_to_sort = []
for key in keys:
    key = int(key)
    keys_to_sort.append(key)

keys_to_sort.sort()

key_list = []
for key in keys_to_sort:
    key = str(key)
    key_list.append(key)

values = skeleton_branch_count_dict.values()

plt.figure(figsize=(30, 15))
plt.bar(key_list, values)
plt.xticks(fontsize=16, rotation=90)
plt.yticks(np.arange(min(values), max(values)+1, 1.0), fontsize=20)
plt.xlabel('Skeleton ID', fontsize=24)
plt.ylabel('Number of branch nodes', fontsize=28)
plt.savefig("Skeleton Branch Count.pdf")

#######################################################################################################################

## Dendrite level classification:

# Create more accessible lists from nested path lists:
paths_list = []
for i in range(len(tree_list)):
    tree = tree_list[i]
    paths = tree.paths_to_leaves()
    paths_list.append(paths)

final_path_list = []
for path in paths_list:
    skel_paths = path
    for skel in skel_paths:
        s = skel
        final_path_list.append(s)

all_levels = []
all_tier_list = []
all_dendrite_level_list = []
for path in paths_list:
    skel_paths = path
    for skel in skel_paths:
        # Count 0 if node is not a branch point and 1 if node is a branch point:
        levels = []
        for node in skel:
            count = 0
            if node in final_branch_list:
                count += 1
            levels.append(count)
        all_levels.append(levels)
        # Keep track of nodes, counting upwards once a branch node is reached:
        tier = 0
        tier_list = []
        for level in levels:
            if level == 0:
                tier = tier
                tier_list.append(tier)
            elif level == 1:
                tier += 1
                tier_list.append(tier)
        all_tier_list.append(tier_list)
        # Classify dendrite levels based on count:
        dendrite_level_list = []
        for tier in tier_list:
            if tier == 0:
                dendrite_level = "primary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 1:
                dendrite_level = "secondary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 2:
                dendrite_level = "tertiary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 3:
                dendrite_level = "quaternary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 4:
                dendrite_level = "quinary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 5:
                dendrite_level = "senary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 6:
                dendrite_level = "septenary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 7:
                dendrite_level = "octonary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 8:
                dendrite_level = "nonary"
                dendrite_level_list.append(dendrite_level)
            elif tier == 9:
                dendrite_level = "denary"
                dendrite_level_list.append(dendrite_level)
            elif tier >= 10:
                dendrite_level = "higher level"
                dendrite_level_list.append(dendrite_level)

        all_dendrite_level_list.append(dendrite_level_list)

# Flatten lists:
flat_final_path_list = [val for sublist in final_path_list for val in sublist]
flat_all_dendrite_level_list = [val for sublist in all_dendrite_level_list for val in sublist]

# Make dictionary from nodes and associated dendrite levels:
level_dict = {flat_final_path_list[i]: flat_all_dendrite_level_list[i] for i in range(len(flat_final_path_list))}

# Make data frame from nodes and levels of seperation:
dendrite_levels_df = pd.DataFrame(level_dict.items(), columns=["Node_ID", "Dendrite_Level"])

# Make new data frame without skeletons with errors:
XML_new = XML_final_df[~XML_final_df["Skeleton_ID"].isin(skeleton_errors_list)]

# Make Node_ID column numeric:
XML_new["Node_ID"] = pd.to_numeric(XML_new["Node_ID"])

# Merge data frames (NOTE: XML_final_df has 9675 lines, while dendrite_levels_df has 7814:
merged_final_df = pd.merge(XML_new, dendrite_levels_df, on=["Node_ID"], how="inner")

# Save processed skeletons to CSV file:
merged_final_df.to_csv("Processed_Skeleton_Information.csv", index = False)

analysis_time = datetime.now() - starttime_bc
print("\nAnalysis Completion Time: ", analysis_time)

