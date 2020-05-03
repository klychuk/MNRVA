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

#######################################################################################################################

## Creating New Node ID to contain Skeleton ID:

# Make data frame with skeleton information:
XML_final_df = pd.DataFrame()
#prints empty dataframe
#print(XML_final_df)

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


#print(XML_final_df)
#print(soma_df)

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

#print(XML_final_df)
#print(soma_df)
#######################################################################################################################
#creation of classes from the DFs

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

    def set_classif(self,inp):
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
        if len(self.children) < 1:
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
final_classification_df.to_csv('Apical Basal Reclassification.csv', index = False)

# Print time it took for above analysis:
analysis_time = datetime.now() - starttime_bc
#print("Analysis Completion Time: ", analysis_time)


objects = final_classification_df['Node_ID']

plt.bar(objects, final_ed_list, align='center')
plt.ylabel('ED')
plt.title('Distribution of ED')


#displays the plot upon running
#commented for testing
plt.show()



























