import os, sys
from datetime import datetime
import XML_Parse as parse
import Apical_Basal_Classification as AB
from treelib import Node, Tree
import itertools

import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

#######################################################################################################################

# Data Management and Organization:
starttime_bc = datetime.now()
root = parse.root

# Dataframe with the end points and their positions:
endpoints_position_df = AB.end_pt_df(root)

# Make dataframe with source target information:
source_target_df = pd.DataFrame()

for thing in parse.root.iter("thing"):
    source_target_df = source_target_df.append(parse.source_target_pos_df(thing), ignore_index=True)

# Rename columns to have no spaces in names:
source_target_df.rename(columns = {"Skeleton ID": "Skeleton_ID", "Skeleton Comment":"Skeleton_Comment"}, inplace = True)

# Fill empty cells in Skeleton ID column to have last filled value:
source_target_df.fillna(method = "ffill")
source_target_df.Skeleton_ID = source_target_df.Skeleton_ID.ffill()

source_target_df_temp = source_target_df
source_target_df.to_csv('Source_Target.csv', index = False)

#######################################################################################################################

## Creating New Node ID to contain Skeleton ID:

# Make data frame with skeleton information:
XML_final_df = pd.DataFrame()

for thing in parse.root.iter("thing"):
    XML_final_df = XML_final_df.append(parse.skeleton_information(thing), ignore_index=True)

# Rename columns to have no spaces in names:
XML_final_df.rename(columns = {"Skeleton ID": "Skeleton_ID", "Skeleton Comment":"Skeleton_Comment", "Node ID":"Node_ID", "Node Comment":"Node_Comment"}, inplace = True)

# Fill empty cells in Skeleton ID column to have last filled value:
XML_final_df.fillna(method = "ffill")
XML_final_df.Skeleton_ID = XML_final_df.Skeleton_ID.ffill()

# Create new column containing new Node IDs
XML_final_df["New_Node_ID"] = XML_final_df["Skeleton_ID"] + "_" + XML_final_df["Node_ID"]

# Make all node comments lowercase:
XML_final_df["Node_Comment"] = XML_final_df["Node_Comment"].str.lower()

# Create soma data frame:
soma_df = XML_final_df[XML_final_df["Node_Comment"].str.contains("soma|first node")]

# Save to csv:
#XML_final_df.to_csv("Skeleton information.csv", index = False)
soma_df.to_csv("Soma.csv", index = False)

#######################################################################################################################

## Data Frame Management and Organization:

# Merge endpoints and XML data frames:
endpoints_position_df.rename(columns={"Node ID": "Node_ID", "x":"X", "y":"Y", "z":"Z"},inplace = True)
endpoints_position_df["Node_ID"] = endpoints_position_df["Node_ID"].astype(str)
endpoints_position_df["X"] = endpoints_position_df["X"].astype(str)
endpoints_position_df["Y"] = endpoints_position_df["Y"].astype(str)
endpoints_position_df["Z"] = endpoints_position_df["Z"].astype(str)
merged_endpoints_df = pd.merge(XML_final_df, endpoints_position_df, on=["Node_ID", "X", "Y", "Z"], how="inner")

# Create data frame with soma and end point information:
frames = [soma_df, merged_endpoints_df]
merged_endpoints_soma_df = pd.concat(frames)

# Make sure coordinates are numerical values:
merged_endpoints_soma_df["X"] = merged_endpoints_soma_df["X"].astype(int)
merged_endpoints_soma_df["Y"] = merged_endpoints_soma_df["Y"].astype(int)
merged_endpoints_soma_df["Z"] = merged_endpoints_soma_df["Z"].astype(int)

# Create new data frames grouped by skeleton ID and store in dictionary:
skeletons = {}
for Skeleton_ID, merged_endpoints_soma_df in merged_endpoints_soma_df.groupby("Skeleton_ID"):
    skeletons.update({'skeleton_' + Skeleton_ID : merged_endpoints_soma_df.reset_index(drop=True)})

# Create list of each skeleton data frame:
skeleton_list_df = [skeletons[x] for x in skeletons]

#######################################################################################################################

## Apical Basal Reclassification Analysis:

final_ed_list = []
final_class_list = []

# Iterate through end points to assign variables:
for skeleton in skeleton_list_df:
    ed_lists = []
    class_lists = []
    for i in range(len(skeleton)):
        x1 = skeleton.iloc[0,3]
        y1 = skeleton.iloc[0,4]
        z1 = skeleton.iloc[0,5]
        x2 = skeleton.iloc[i]['X']
        y2 = skeleton.iloc[i]['Y']
        z2 = skeleton.iloc[i]['Z']
        # Run Euclidean Distance formula:
        ed1 = (x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2
        ed2 = np.sqrt(ed1)
        ed_lists.append(ed2)
    # Find average Euclidean Distance for each skeleton:
    avg_ED = int(sum(ed_lists) / len(ed_lists))
    # Classify based on average Euclidean Distance:
    for row in ed_lists:
        if row > avg_ED:
            class_lists.append("Apical")
        elif row == 0:
            class_lists.append("Soma")
        elif row < avg_ED:
            class_lists.append("Basal")
        else:
            class_lists.append("Unclassified")
    # Merge Euclidean Distance lists for each skeleton into one list:
    for ed in ed_lists:
        final_ed_list.append(ed)
    # Merge Classification lists for each skeleton into one list:
    for lists in class_lists:
        final_class_list.append(lists)

# Re-combine skeleton data frames into on data frame:
final_classification_df = pd.concat(skeletons.values(), ignore_index=True)

# Append Euclidean Distance and Classification values to columns in data frame:
final_classification_df['Euclidean_Distance_From_Soma'] = final_ed_list
final_classification_df['Classification'] = final_class_list

# Save to csv:
final_classification_df.to_csv('Apical Basal Reclassification.csv', index = False)

#######################################################################################################################

## Data Management and Organization for Tree Structure Creation:

# NOT SURE WHY I NEED THESE IN HERE TO PROCESS!!
source_target_df = pd.read_csv("Source_Target.csv")
soma_df = pd.read_csv("Soma.csv")

source_target_df_temp = source_target_df

#Make list of soma node IDs:
soma_list = list(soma_df["Node_ID"])

#Make list of node IDs and skeleton IDs:
node_list = list(XML_final_df["Node_ID"])
skeleton_list = list(XML_final_df["Skeleton_ID"])

#Make lists of sources and targets:
source_list = list(source_target_df["Source ID"])
target_list = list(source_target_df["Target ID"])
skeleton_source_target_list = list(source_target_df["Skeleton_ID"])

# Function to make all nodes integers:
def make_int(your_list):
    for i in range(len(your_list)):
        your_list[i] = int(your_list[i])

# Make all nodes integers in specified lists:
make_int(soma_list)
make_int(node_list)
make_int(skeleton_list)
make_int(source_list)
make_int(target_list)

#Make dictionary from nodes and associated skeletons:
skeleton_dict = {node_list[i]: skeleton_list[i] for i in range(len(node_list))}

#Make dictionary from source nodes and associated skeletons:
source_skeleton_dict = {source_list[i]: skeleton_source_target_list[i] for i in range(len(source_list))}

#Subset data frame to find instances where Source ID is greater than Target ID (tracing error #1):
errors = source_target_df[source_target_df["Source ID"] > source_target_df["Target ID"]]

#Make list of skeletons with errors and remove duplicates:
skeleton_errors_list = errors["Skeleton_ID"]
skeleton_errors_list = list(dict.fromkeys(skeleton_errors_list))

#Find source nodes that are never target nodes (tracing error #2):
missing_nodes = []
for node in source_list:
    if node not in target_list:
        missing = node
        missing_nodes.append(missing)

#Remove missing nodes if they are the soma:
final_missing_nodes = []
for node in missing_nodes:
    if node not in soma_list:
        final_missing = node
        final_missing_nodes.append(final_missing)

#Remove duplicated nodes in list:
final_missing_nodes = list(dict.fromkeys(final_missing_nodes))

#Find skeleton ID asssocialted with missing nodes:
for key, value in source_skeleton_dict.items():
    if key in final_missing_nodes:
        error = value
        skeleton_errors_list.append(error)

#Remove duplicate nodes in list:
skeleton_errors_list = list(dict.fromkeys(skeleton_errors_list))

#Provide user with number of errors:
if len(skeleton_errors_list) > 0:
    print("There were " + str(len(skeleton_errors_list)) + " skeletons that could not be processed." )
    print("Skeleton information for these " + str(len(skeleton_errors_list)) + " skeletons will be output to a file named 'Unprocessed_Skeleton_Information.csv'.")
    print("\nThe program will proceed with processing the remaining " +  str(len(soma_list)-len(skeleton_errors_list)) + " skeletons.")
else:
    print("The program will proceed with processing " + str(len(soma_list)) + " skeletons.")

# Make new soma data frame without problematic skeletons:
soma_df_new = soma_df[~soma_df['Skeleton_ID'].isin(skeleton_errors_list)]
soma_list_new = list(soma_df_new["Node_ID"])

source_target_df = source_target_df_temp

# Make new source target data frame without problematic skeletons:
source_target_df_new = source_target_df[~source_target_df['Skeleton_ID'].isin(skeleton_errors_list)]

# Make source target data frame with problematic skeletons and write to csv:
source_target_df_errors = source_target_df[source_target_df['Skeleton_ID'].isin(skeleton_errors_list)]
source_target_df_errors.to_csv('Unprocessed_Skeleton_Information.csv', index=False)

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
    source_list_indiv = list(df["Source ID"])
    target_list_indiv = list(df["Target ID"])
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

# Make tree structures:
#from treelib import Node, Tree

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

for tree in tree_list:
    tree.save2file("Processed_Skeleton_Trees.txt")

#######################################################################################################################

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

# plt.figure(figsize=(30, 15))
# plt.bar(key_list, values)
# plt.xticks(fontsize=16, rotation=90)
# plt.yticks(np.arange(min(values), max(values)+1, 1.0), fontsize=20)
# plt.xlabel('Skeleton ID', fontsize=24)
# plt.ylabel('Number of branch nodes', fontsize=28)
# plt.show()

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

# Save to CSV:
merged_final_df.to_csv("Processed_Skeleton_Information.csv", index = False)

analysis_time = datetime.now() - starttime_bc
print("\nAnalysis Completion Time: ", analysis_time)

