import os, sys
from datetime import datetime

import XML_Parse as xparse
import Apical_Basal_Classification as classify
import Branch_Number_per_Skeleton as bnps
import Euclidean_Distance as ed
import Skeleton_Visualization as sv
import File_Converter as sw

import pandas as pd

#######################################################################################################################

# Setting user input to select which analyses user wants run:

parsing_option = input("Excel file with all object information? (Y or N): ")
parsing_option.islower()
if parsing_option is 'y':
    horizontal_orientation = input("Would you like node information to be separate columns as a horizontal output? WARNING: do not use with large data sets (Y or N): ")
    horizontal_orientation.islower()
branch_class_option = input("Run Branch Classification (Apical vs. Basal) Analysis? (Y or N): ")
branch_class_option.islower()
branch_number_option = input("Run Branch Number per Skeleton Analysis? (Y or N): ")
branch_number_option.islower()
euclidean_distance_option = input("Calculate dendritic distance? (Y or N): ")
euclidean_distance_option.islower()
if euclidean_distance_option is 'y':
    total_eu_option = input("Do you want the total euclidean distance per skeleton? (Y or N): ")
    total_eu_option.islower()
    node_eu_option = input("Do you want the euclidean distance per node? (Y or N): ")
    node_eu_option.islower()
visualization_option = input("Skeleton reference? (Y or N): ")
visualization_option.islower()
swc_option = input("Convert XML to SWC file format? This will output a .csv file with the correct format for neuromorph files (Y or N): ")
swc_option.islower()

if swc_option is 'y':
    orientation_option = input("Which X,Y,Z plane is North? This will be used as orientation for determining apical vs basal branches (please input x,y, or z): ")

print("\n")

#######################################################################################################################

# Following section will run the analyses as input above:

# Parsed Excel Sheet
starttime_xml = datetime.now()

if parsing_option is 'y':

    XML_final_df = pd.DataFrame()
    for thing in xparse.root.iter('thing'):
        XML_final_df = XML_final_df.append(xparse.skeleton_information(thing), ignore_index=True)
    xparse.save_csv_df(XML_final_df, 'skeleton_information.csv')

    XML_time_n = datetime.now() - starttime_xml
    print("XML Parsing Completion Time: ", XML_time_n)

    if horizontal_orientation is 'y':
        final_df = xparse.XML_info_node_rows(xparse.root)
        xparse.save_csv_df(final_df, 'skeleton_information_horizontal.csv')
        print(final_df)

        XML_time = datetime.now() - starttime_xml
        print("XML Parsing Completion Time: ", XML_time)

# Branch Classification (Apical vs. Basal)
starttime_bc = datetime.now()
if branch_class_option is 'y':
    endpoints_position_df = pd.DataFrame()
    for thing in xparse.root.iter('thing'):
        endpoints_position_df = endpoints_position_df.append(classify.apical_basal_classifier(thing), ignore_index=True)
    xparse.save_node_csv_df(endpoints_position_df, 'branch_classification.csv')
    classify.ab_barchart(xparse.root)
    classify.overlaid_histogram(xparse.root)

    classify_time = datetime.now() - starttime_bc
    print("Branch Classification Completion Time: ", classify_time)

# Branch Number per Skeleton Analysis:
starttime_bn = datetime.now()
if branch_number_option is 'y':
    skeleton_branches_df = pd.DataFrame()
    for thing in xparse.root.iter('thing'):
        skeleton_branches_df = skeleton_branches_df.append(bnps.branch_number_per_skeleton(thing), ignore_index=True)
    xparse.save_csv_df(skeleton_branches_df, 'total_branches_per_skeleton.csv')
    bnps.skeleton_branch_number_histogram('total_branches_per_skeleton.csv')

    bnps_time = datetime.now() - starttime_bn
    print("Branch Number Completion Time: ", bnps_time)

# Euclidean Distance Analysis:
starttime_ed = datetime.now()
if euclidean_distance_option is 'y':
    if total_eu_option is 'y':
        ed_per_skeleton_df = pd.DataFrame()
        for thing in xparse.root.iter('thing'):
            ed_per_skeleton_df = ed_per_skeleton_df.append(ed.ed_per_skeleton(thing), ignore_index=True)
        xparse.save_csv_df(ed_per_skeleton_df, 'euclidean_distance_per_skeleton.csv')
        ed.ed_histogram('euclidean_distance_per_skeleton.csv')
    if node_eu_option is 'y':
        ed_per_node_df = pd.DataFrame()
        for thing in xparse.root.iter('thing'):
            ed_per_node_df = ed_per_node_df.append(ed.ed_per_node(thing), ignore_index=True)
        xparse.save_csv_df(ed_per_node_df, 'euclidean_distance_per_node.csv')
        # ed.ed_histogram('euclidean_distance_per_node.csv')

    ed_time = datetime.now() - starttime_ed
    print("Euclidean Distance Completion Time: ", ed_time)

# Skeleton Visualization:
starttime_sv = datetime.now()
if visualization_option is 'y':
    sv.network_graph_go(xparse.root)

    sv_time = datetime.now() - starttime_sv
    print("Visualization Time: ", sv_time)

# Convert to SWC:
if swc_option is 'y':
    # Creating a directory within the user defined output directory to save all swc files:
    if os.path.exists("SWCFileFormats"):
        print("SWCFileFormats already exists, please check directory or delete to continue.")
    else:
        os.mkdir("SWCFileFormats")
        os.chdir("SWCFileFormats")

    final_df = pd.DataFrame()

    for thing in xparse.root.iter('thing'):
        skeleton_df = sw.swc_file_format(thing)
        final_df = final_df.append(skeleton_df, ignore_index=False)
        # Saving the individual skeletons
        filename = str(xparse.skeleton_id(thing))
        skeleton_df.to_csv(filename + '.csv')
    # Saving a final CSV with all the information
    final_df['Sample Number'] = final_df.index
    ordered_final_df = final_df[ [ 'Sample Number', 'Structure Identifier', 'x', 'y', 'z', 'radius', 'Parent Sample' ] ]
    xparse.save_csv_df(ordered_final_df, 'SWC_Format.csv')

# Finalization:

print('\nCompleted Analysis: ', xparse.output_file, '\n')

#######################################################################################################################

