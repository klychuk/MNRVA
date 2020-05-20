import os, sys
from datetime import datetime
import XML_Parse as parse
import Apical_Basal_Classification as AB
import itertools
from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from treelib import Node, Tree

#######################################################################################################################

## Import necessary variables and dataframes from other files:

starttime_bc = datetime.now()
root = parse.root

# Dataframe with the end points and their positions:
endpoints_position_df = AB.end_pt_df(root)

# Dataframe with source and target node IDs and coordinates:
source_target_df = parse.source_target_pos_df(root)
#source_target_df.to_csv('Source_Targets.csv', index = False)

#######################################################################################################################

## Creating New Node ID to contain Skeleton ID:

# Make an empty data frame to store skeleton information:
XML_final_df = pd.DataFrame()

# Iterate through skeleton information to append information to data frame:
for thing in parse.root.iter("thing"):
    XML_final_df = XML_final_df.append(parse.skeleton_information(thing), ignore_index=True)

# Rename columns to have no spaces in names:
XML_final_df.rename(columns = {"Skeleton ID": "Skeleton_ID", "Skeleton Comment":"Skeleton_Comment", "Node ID":"Node_ID", "Node Comment":"Node_Comment"}, inplace = True)

# Fill empty cells in Skeleton ID column to have last filled value:
XML_final_df.fillna(method = "ffill")
XML_final_df.Skeleton_ID = XML_final_df.Skeleton_ID.ffill()

# Create new column containing new Node IDs
XML_final_df["New_Node_ID"] = XML_final_df["Skeleton_ID"] + "_" + XML_final_df["Node_ID"]

# Create soma data frame:
soma_df = XML_final_df[XML_final_df["Node_Comment"].str.contains("soma|First Node")]

# Save to csv:
soma_df.to_csv("Soma.csv", index = False)
XML_final_df.to_csv("Skeleton information-updated.csv", index = False)

#######################################################################################################################

## Data Organization and Management for Apical Basal Reclassification:

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

#print(XML_final_df)
#print(soma_df)

#######################################################################################################################
#creation of classes from the DFs
##We can probably remove this section

#Add (self, soma_ID)
class Neuron:
    def __init__(self):
        self.SK_ID = 0
        self.radius = 0
        self.euc_dist = 0
        self.classif = ""

    def get_N_euc(self, inp):
        #return self.euc_dist
        pass

    def set_classif(self, inp):
        self.classif = inp

class Node(Neuron):
    def __init__(self, SK_ID):
        self.soma_ID = SK_ID
        self.node_ID = 0
        self.parent_ID = 0
        self.children = []
        self.end = False
        self.branch = False
        self.from_soma = False
        self.radius = 0

    #this will tell if its an end node or a branching point
    def classify_node(self):
        if len(self.children) == 0:
            self.end = True
        if len(self.children) > 1:
            self.branch = True

    #This is a direct branching from the soma can use to name branches?
    def set_direct(self):
        if self.parent_ID == self.soma_ID:
            self.from_soma = True

#Then create loops to set each variable with calculation like the one below :) 

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
#final_classification_df.to_csv('Apical Basal Reclassification.csv', index = False)

# Print time it took for above analysis:
analysis_time = datetime.now() - starttime_bc
#print("Analysis Completion Time: ", analysis_time)

#######################################################################################################################

## Data Management and Organization for Tree Structure Creation:

#Make list of soma node IDs:
soma_list = list(soma_df["Node_ID"])

#Make list of node IDs and skeleton IDs:
node_list = list(XML_final_df["Node_ID"])
skeleton_list = list(XML_final_df["Skeleton_ID"])

#Make lists of sources and targets:
source_list = list(source_target_df["Source ID"])
target_list = list(source_target_df["Target ID"])

#Make all nodes integers:
for i in range(len(soma_list)):
    soma_list[i] = int(soma_list[i])

for i in range(len(node_list)):
    node_list[i] = int(node_list[i])

for i in range(len(skeleton_list)):
    skeleton_list[i] = int(skeleton_list[i])

for i in range(len(source_list)):
    source_list[i] = int(source_list[i])

for i in range(len(target_list)):
    target_list[i] = int(target_list[i])

#Make dictionary from nodes and associated skeletons:
skeleton_dict = {node_list[i]: skeleton_list[i] for i in range(len(node_list))}

#Find sources in skeleton dictionary and make new list of associated skeletons:
skeletons = []
for source in source_list:
    if source in skeleton_dict.keys():
        skeletons.append(skeleton_dict[source])

#Add new column with skeleton ID to the source target data frame:
source_target_df["Skeleton_ID"] = skeletons

#Split full data frame into list of data frames for each skeleton:
skeleton_info_list = []
for skeleton, source_target_df in source_target_df.groupby("Skeleton_ID"):
    skeleton_info_list.append(source_target_df)

#Create dictionary for somas within skeleton:
somas_dict_list = []
for soma in soma_list:
    soma_dict = {soma: {"parent": None}}
    somas_dict_list.append(soma_dict)

#Iterate through skeletons to store parent information:
all_parents_dict_list = []
for df in skeleton_info_list:
    source_list_indiv = list(df["Source ID"])
    target_list_indiv = list(df["Target ID"])
    source_target_dict_indiv = {target_list_indiv[i]: source_list_indiv[i] for i in range(len(target_list_indiv))}
    #Create separate dictionaries for nodes within each skeleton:
    parents_dict = {}
    for key, value in source_target_dict_indiv.items():
        source = key
        target = value
        parent_dict = {source: {"parent": target}}
        parents_dict.update(parent_dict)
    #Create final list of dictionaries with parent information for each skeleton:
    all_parents_dict_list.append(parents_dict)

#Add soma parent information to each associated skeleton parent information:
for i in range(len(somas_dict_list)):
    all_parents_dict_list[i].update(somas_dict_list[i])

#Remove errors in source target lines for index 6, 10, 25, 26, 30, 42, 47, 50, 53:
no_error_list_1 = all_parents_dict_list[0:6]
no_error_list_2 = all_parents_dict_list[7:10]
no_error_list_3 = all_parents_dict_list[11:25]
no_error_list_4 = all_parents_dict_list[27:30]
no_error_list_5 = all_parents_dict_list[31:42]
no_error_list_6 = all_parents_dict_list[43:47]
no_error_list_7 = all_parents_dict_list[48:50]
no_error_list_8 = all_parents_dict_list[51:53]
no_error_list_9 = all_parents_dict_list[54:57]

#Make final list of skeletons without errors:
final_no_error_list = no_error_list_1 + no_error_list_2 + no_error_list_3 + no_error_list_4 + no_error_list_5 + no_error_list_6 + no_error_list_7 + no_error_list_8 + no_error_list_9

#######################################################################################################################

## Tree Structure Creation:

#Create tree structures for skeletons:
tree_list = []
for node in final_no_error_list:
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

#Save tree structures to text file:
for tree in tree_list:
    tree.save2file('All_trees_no_errors.txt')
