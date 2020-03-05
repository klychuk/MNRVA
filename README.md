# About

This project seeks to address data analysis through the
development of a series of comparative analysis tools for connectomic data in an effort to make a
foundational basis of analysis for all researchers in connectomics. These scripts include total dendritic branch number per neuron (dendritic density), and Euclidean distance.
This work will function as a base line for further analytical tools that will be developed for similar data.
To encourage reproducibility and collaboration, all scripts are available open source through GitHub
and Google Colab.

Currently this analysis package is designed for Knossos XML files containing traced skeletons.

Google Colab Link: *Coming Soon* 

Please see the Kasthuri Lab for more information: https://microbiome.uchicago.edu/directory/bobby-kasthuri

### Instructions for Download:

Please see below for running this package on Linux, Mac, and Windows OS.

#### Linux / Mac

Once the package has been downloaded from Github, extract the file in the directory you would like the analyses scripts
to be saved. Using command line, change the directory so your working directory is the same as the extracted analyses 
folder. 

From here you can input the following command in the terminal to run the script. Please change the first input to the
path to the XML file you wish to run analyses on, and the second input to the folder you would like to save the analysis
output. 

```shell script
python Analysis_EXE.py /home/user/where/is/XML_file.xml /home/user/where/you/want/saved
```

Once you run this, you will get an output on your console similar to the following: 
```
Run Branch Number per Skeleton Analysis? (Y or N): y
Run Euclidean Distance per Skeleton Analysis? (Y or N): y
```
Please enter either Y or N and each of the selected analyses will run. Hit enter. When the analyses are down you will 
find the .csv files in the output directory you input. 

#### Windows

After downloading package from github, extract the file to the directory you would like the analyses scripts to be saved. 
Then open a cmd terminal (can search "cmd" in windows toollbar if unsure). Change the directory to where you extracted 
analysis folder using the command below:

```
cd\ C:\directory\where\analysis\is\saved
``` 

From here, input the following command in the terminal to run the script. Please change the first input to the
path to the XML file you wish to run analyses on, and the second input to the folder you would like to save the analysis
output. 

```
py Analysis_EXE.py \C:\\User\where\is\XML_file.xml \C:\\User\where\you\want\saved
```

Once you run this, you will get an output on your console similar to the following: 
```
Run Branch Number per Skeleton Analysis? (Y or N): y
Run Euclidean Distance per Skeleton Analysis? (Y or N): y
```
Please type y for analyses you would like to run and then hit enter. When the analyses are down you will find the .csv 
files in the output directory you input. 

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

### Visualization

There is an option to create a visualization of the KNOSSOS skeletons for reference. This requires two additional packages: 
plotly and igraph. There are additional installation steps for Windows users that are outlined more in depth at the 
following links given below:

Plotly: https://plot.ly/python/getting-started/ 

Igraph: https://igraph.org/python/

### Analyses:

This section discusses each of the analyses and their required input. 

##### Terminology Reference:

Skeleton: A traced object in KNOSSOS, parent object in .xml that contains node and edge information (denoted as 'thing' within KNOSSOS
annotation .xml file)

__Node__: marked point within skeleton object, child of skeleton object in .xml (denoted as 'node' within KNOSSOS annotation file)

__Edge__: line between two nodes, determined by 'source' and 'target' nodes as given by KNOSSOS annotation file

__.csv file format__: a tab delimited file format that can be opened with Microsoft Excel or Libre Sheets

__.swc file format__: tab delimited file format used for neuromorph data

#### XML Parse:

The purpose of this script is to parse through the KNOSSOS .xml file input by the user. This contains all of the functions
to organize and clean the given data prior to running the analyses. 

When running the analysis the user will be asked if they want an "Excel file with all object information". This will produce
a .csv file ('skeleton_information.csv') containing all of the node and skeleton information in the following format:

| Skeleton ID | Skeleton Comments | Node ID | Node Radius | X | Y | Z | Node Comment |
|-------------|-------------------|---------|-------------|---|---|---|--------------|
|1            |comment 1          |10       |radius 1     |x1 |y1 |z1 | comment      |

Should the user than answer 'yes' to this, they will be prompted "would you like node information to be separate columns
as a horizontal output?". Answering yes to this prompt will create a .csv file with each node and its associated information 
as a **separate column**. This is not recommended for larger data sets with a multitude of nodes per skeleton and is at 
this time limited to three nodes per skeleton. *Please keep this in mind when using this analysis.* The output is demonstrated
below:
 
| Skeleton ID | Skeleton Comments | Node_1 ID | Node_1 Radius | X_1 | Y_1 | Z_1 | Node_1 Comment | Node_2 ID | Node_2 Radius | X_2 | Y_2 | Z_2 | Node_2 Comment | Node_3 ID | Node_3 Radius | X_3 | Y_3 | Z_3 | Node_3 Comment |
|-------------|-------------------|-----------|---------------|-----|-----|-----|----------------|-----------|---------------|-----|-----|-----|----------------|-----------|---------------|-----|-----|-----|----------------|
|1            |comment 1          |10         |radius 1       | x1  |y1   |z1   | comment        |20         |radius 2       | x2  |y2   |z2   | comment        |30         |radius 3       | x3  |y3   |z3   | comment        |

Should the skeleton contain less than 3 nodes the columns for the unfilled node information will be blank in the .csv file.

#### Branch Number

The Branch Number analysis will output the total number of branches and branch points within each individual skeleton 
object as a csv file in the format below:

|Skeleton ID | Soma ID | Total Number of Branches | Total Number of Branch Points|
|------------|---------|--------------------------|------------------------------|
|1           |63       |value                     |value2                        |
|2           |98       |value3                    |value4                        |

The script will also output a histogram with the x-axis being the total number of branches and the y-axis as the number
of neurons.

*Skeleton ID*:

The skeleton ID is determined from the given name of the traced object within KNOSSOS.

*Soma ID*:

The soma ID is the node that was either marked as soma within the comments section of the KNOSSOS tracing file, or if 
that was not marked it is the node with the largest radius. <span style="red"> If neither of these are true </font> it 
will through an error. 

*Total Number of Branches:*

This column gives the total number of branches per skeleton based on the number of end nodes in a skeleton object.

*Total Number of Branch Points:* 

This column gives the number of branch points per skeleton based on the number of nodes that are have two or more target 
nodes. 

#### Branch Classification

The purpose of this analysis is to classify branches as either apical or basal based on their endpoint position. If the 
branch ends with a greater "y" corrdinate than the Soma it will be counted as apical, if the branch ends with a lesser "Y"
coordinate than the Soma it will be counted as basal. Should the "y" coordinate for the Soma and branch end point be the
same then it will count the branch as uncategorized. 

Therefore it is important to note that this analysis will only work properly if the Soma of each neuron are clearly marked
as "Soma" in the original KNOSSOS annotation file, or are the node with the largest radius. 

#### Euclidean Distance

The Euclidean distance analysis will either output a csv file with the Skeleton ID and the total length of all its branches,
or a csv file with the distance between all of the individual nodes. The user has the option to select which output they
want. The format for the csv with the total euclidean distance per skeleton is demonstrated below: 

|Skeleton ID | Total Euclidean Distance|
|------------|-------------------------|
|1           |value                    |
|2           |value2                   |

Additionally, the total euclidean distance analysis will output a histogram with the x-axis being the total euclidean distance and the y-axis 
being the number of neurons.

*Skeleton ID*:

The skeleton ID is determined from the given name of the traced object within KNOSSOS.

*Total Euclidean Distance* 

To determine the distance, the x,y,z coordinates of the source node and target node and applies the Euclidean distance
formula (sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)). Then each of the distances between nodes are summed together to get 
the total length per neuron. 

### File Format:
#### Saving KNOSSOS .xml to .swc File

Running this will save convert the KNOSSOS .xml file format to the required .swc tab delineated input. This is seen below:

|Data Type  | Sample Number | Structure Identifier | x position | y position | z position | Radius | Parent Sample |
|-----------|---------------|----------------------|------------|------------|------------|--------|---------------|
|data value |integer value, |0 - undefined         |            |            |            |        |Sample number, | 
|           |generally      |1 - soma              |            |            |            |        |connectivity   |    
|           |continuous     |2 - axon              |            |            |            |        |expressed with |
|           |               |3 - basal dendrite    |            |            |            |        |this value.    |
|           |               |4 - apical dendrite   |            |            |            |        |Parent samples |
|           |               |5 - fork point        |            |            |            |        |should appear  |
|           |               |6 - end point         |            |            |            |        |before child.  |
|           |               |7 - custom            |            |            |            |        |               |  