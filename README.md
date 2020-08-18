# About

MNRVA is a connectomics automated analysis program that aims to reduce the barrier between data assembly and analysis. MNRVA stores relationships between nodes in the neural skeleton and performs basic dendrite calculations and classifications. This project seeks to establish a foundation for connectomic data analysis. Currently this analysis package is designed for Knossos XML files containing traced skeleton information. This work will function as a baseline for further analytical tools that will be developed for similar data. To encourage reproducibility and collaboration, all scripts are available open source through GitHub. This is a continuation of the work that was originally done by Katrina Norwood, and the beta version of the program can be accessed here: https://github.com/knorwood0/MNRVA.


Please see the Kasthuri Lab for more information: https://microbiome.uchicago.edu/directory/bobby-kasthuri


### Installation and Use:

Please see below for running this package on Linux, Mac, and Windows OS.

Once the package has been downloaded from Github, extract the file in the directory you would like the analyses scripts to be saved. Using command line  or command terminal, change the directory so your working directory is the same as the extracted analyses folder.

From here you can input the following command in the terminal to run the script. After -input, please change the first input to the path to the XML file you wish to run analyses on. After -out_dir, put the path to the folder where you would like to save the analysis output. Finally, after -run_name, choose the folder name for the output results to be saved to.

```shell script
python Combined_Analyses.py -input /home/user/location/of/XML_file.xml -out_dir /home/user/location/to/save -run_name folder
```


### Module Dependencies:

There are a few additional packages used for visualization and data management that are required to run this analysis module.
It is recommended that you install with Anaconda and create a separate conda environment.
Follow the instructions given in the links for download. The list is given below:

* Python 3.7.3
* Pandas 0.25.0 (https://pandas.pydata.org/pandas-docs/stable/install.html)
* Numpy 1.17.2
* Matplotlib 3.1.1
* Igraph 0.7.1 (https://igraph.org/python/)
* Plotly 4.4.1 (https://plot.ly/python/getting-started/)
* NetworkX 2.4 (https://networkx.github.io/)
* Treelib 1.5.5 (https://treelib.readthedocs.io/en/latest/treelib.html)


### Knossos Annotation Dependencies

A tree structure cannot be generated from the tracing information if any of the links are missing or inaccurate. MRNVA attempts to take into account variable user annotation and labeling methods, however, inconsistencies within the annotation and labeling may result in errors. Because of this, we propose that to use MNRVA at its full capacity, users should follow a numerical system for annotating and labeling nodes, such that no target node has an ID value lesser than that of its source node. 

### Terminology Reference

__Skeleton__: A traced object in KNOSSOS, parent object in .xml that contains node and edge information (denoted as 'thing' within KNOSSOS
annotation .xml file)

__Node__: marked point within skeleton object, child of skeleton object in .xml (denoted as 'node' within KNOSSOS annotation file)

__Edge__: line between two nodes, determined by 'source' and 'target' nodes as given by KNOSSOS annotation file


### Visualization

There is an option to create a two-dimensional visualization of the Knossos skeletons for reference. The user can hover over each node to see its associated properties within the skeletons, which include its ID and number of branches from that point. This requires two additional packages: plotly and igraph. There are additional installation steps for Windows users that are outlined more in depth at the following links given below:

Plotly: https://plot.ly/python/getting-started/ 
Igraph: https://igraph.org/python/

### Analyses

This section discusses each of the analyses and their required input. 

##### XML Parsing and Error Handling:
Relevant information is parsed from the annotated XML file and stored in comma-separated values (CSV) files for further analysis. To handle possible tracing or annotation errors, skeletons with errors are saved to a separate CSV file called "Unprocessed_Skeleton_Information". The user is notified of the number of skeletons with tracing errors in addition to their unique identification number to allow for troubleshooting. 

#### Tree Structure:
MNRVA creates a data structure to store relationships between nodes in each neuronal skeleton using the package treelib for Python 3. 

#### Euclidean Distance:
To determine the Euclidean distance, the x,y,z coordinates of the source node and target node and applies the Euclidean distance formula (sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)). 
Then each of the distances between nodes are summed together to provide the total length of each dendrite. 

#### Sholl Analysis:
Sholl analysis is used to classify dendrites as either apical or basal. The average Euclidean distance from the soma plus one standard deviation is used to categorize the end nodes within each skeleton. Any dendrites with Euclidean distances higher than this value are classified as apical, while any that are lower are classified as basal. Each corresponding node along the dendritic branch is then classified likewise. 
 
 #### Node Classifications:
 The treelib package is used for the identification and classification of end nodes and branch nodes, and the dendritic levels are classified based on the degrees of separation from the soma.

