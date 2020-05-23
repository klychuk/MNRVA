import os, sys
from datetime import datetime
import XML_Parse as parse
import Apical_Basal_Classification as AB
#import Node_Renaming as NR
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

#source_target_df.to_csv('Source_Target.csv', index = False)

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

# Create soma data frame:
soma_df = XML_final_df[XML_final_df["Node_Comment"].str.contains("soma|First Node")]

# Save to csv:
#XML_final_df.to_csv("Skeleton information-updated.csv", index = False)

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
skeleton_source_target_list = list(source_target_df["Skeleton_ID"])

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

#Make dictionary from source nodes and associated skeletons:
source_skeleton_dict = {source_list[i]: skeleton_source_target_list[i] for i in range(len(source_list))}

#Subset data frame to find instances where Source ID is greater than Target ID (tracing error #1):
errors = source_target_df[source_target_df["Source ID"] > source_target_df["Target ID"]]

#Make list of skeletons with errors and remove duplicates:
skeleton_errors_list = errors["Skeleton_ID"]
skeleton_errors_list = list(dict.fromkeys(skeleton_errors_list))

#Split full data frame into list of data frames for each skeleton:
skeleton_info_list = []
for skeleton, source_target_df in source_target_df.groupby("Skeleton_ID"):
    skeleton_info_list.append(source_target_df)

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
    print("Errors arise from missing or incomplete tracing information.")
    print("The program will proceed with processing the remaining " +  str(len(soma_list)-len(skeleton_errors_list)) + " skeletons.")
else:
    print("The program will proceed with processing " + str(len(soma_list)) + " skeletons.")



























