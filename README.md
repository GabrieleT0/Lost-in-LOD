# Lost in LOD 

### 🌐 [Website with assessment data calculated over the period from January 1, 2024 to September 29, 2024](https://anonymous.4open.science/w/Lost-in-LOD-45AF/). After clicking on the link, if a 404 screen appears, refresh the page, or use the “Website” button in the upper right corner (this is an issue of anonymous GitHub, the same goes for the other links below in the README)

This repository contains the code to perform the quality evaluation of the KGs registered in the LOD Cloud. The analysis data used for the evaluation are those calculated by [KGs Quality Analyzer](https://anonymous.4open.science/r/Lost-in-LOD-45AF/KGs-Quality-Analyzer/README.md), an open-source knowledge graph quality assessment tool to perform quality analysis on a wide range of freely available knowledge graphs registered on the LOD cloud.

# Table of contents
- [How to reproduce the experiment](#how-to-reproduce-the-experiment-)
    - [Unzip the quality data computed by KGs Quality Analyzer](#unzip-the-quality-data-computed-by-kgs-quality-analyzer-)
    - [Execute the project](#execute-the-project-)
- [Repository structure](#repository-structure-)

# How to reproduce the experiment 🔬
In this section we will illustrate how to perform LOD Cloud evaluation from the quality data computed by KGs Quality Analyzer, so as to obtain the values discussed in the paper submitted to The Web Conference 2025 and illustrated [here](https://anonymous.4open.science/w/Lost-in-LOD-45AF/). Download the quality data from [here](https://drive.google.com/file/d/1AmB9Q67CssUQDzoxaHg3mY1sy33jBzeM/view) (due to the size of the files could not be placed in the GitHub repository). Insert the downloaded zip file into the folder [quality_data](./quality_data/).
*You need a computer with at least **8GB of RAM** and **dual core CPU** to run the project.*
## Unzip the quality data computed by KGs Quality Analyzer 📂 
If you are in Linux environment, run the shell script in the quality data. Then, from the root of the project, run the following commands:
```sh
cd quality_data
sh extract_quality_data.sh
```
In Windows environment, use any zip file extraction software and place the obtained CSV files in the quality data folder.

At the end of the process, the [quality_data](./quality_data/) folder should have the following structure:
```
| - quality_data/
    | - 2024-01-07.csv
    | - 2024-01-14.csv
    ...
    ...
    ...
    | - 2024-09-29.csv
    | - extract_quality_data.sh
    | - quality_data.zip
```
## Execute the project 💻
#### Creates a virtual environment (recommended but not required) and installs all the dependencies
```sh
#Create the virtual environment
python<version> -m venv <virtual-environment-name>

#Activation of the environment
source <virtual-environment-name>/bin/activate 
# or for Windows users
<virtual-environment-name>/Scripts/activate.bat //In CMD
<virtual-environment-name>/Scripts/Activate.ps1 //In Powershel

#Install all the dependencies
pip install -r requirements.txt
```
#### Execute the main.py script from the root directory of the project
```sh
python main.py
```
As first, the script will take the CSVs files in the [quality_data](./quality_data/) directory and create new CSVs in the [filtered](./filtered/) directory that will contain only KGs that are indexed in the LOD Cloud. 
If you have already run the script, and have the data already filtered, you can skip this step by running the ```main.py``` script with the ```-j``` option, as shown below:
```sh
python main.py -j
```

Automatically the script will now populate the [evaluation_results](./evaluation_results/) folder with the CSV files containing the evaluation data, while the [charts](./charts/) folder will contain the boxplots generated from the evaluation data obtained (look at the next section that shows the [structure of the repository](#repository-structure-) to understand where the resulting files are placed).

If, on the other hand, you have already generated all the evaluation results data and only want to generate the charts (in case changes have been made to the ```generate_charts.py``` module), you can generate only the charts by running the ```main.py``` script with the ```-c``` option, as shown below:
```sh
python main.py -c
```


# Repository structure 🌳
```
Lost in LOD
    | - charts/                      Folder in which boxplots generated after quality assessment are placed
        | - over_time/               Folder with graphs related to evaluation on multiple points over time
            | - by_category          Boxplot with assessment data broken down by quality category
            | - by_dimension         Boxplot with assessment data broken down by quality dimension
        | - punctual/                Folder with graphs related to the evaluation on a single point of analysis
    | - docs/                        Contains file related to the documentation.
    | - evaluation_results/          Contains CSV files with the result of the evaluation divided into evaluation done on multiple points in time and punctual evaluation on a single analysis.
        | - manually_refined_files/  Contains All CSVs that have been manually parsed and annotated to extract useful information about the availability, license, and media type used for KG.
        | - over_time/               Contains CSV files with evaluation results over time broken down by quality categories, quality dimensions and quality metrics.
            | - by_category
            | - by_dimension
            | - by_metric
        | - punctual/                Contains CSV files with all the results of evaluations performed on a single quality analysis.
    | - filtered/                    In this folder, the script inserts all CSV files containing the results of the qualitative analysis of only those KGs indexed in the LOD Cloud.
    | - quality_data                 The quality analysis results provided as output by KGs Quality Analyzer should be placed in this folder in order to run this script.
    | - generate_charts.py           Python class that reads the CSV file containing the quality assessment and generates charts (Boxplot and Bubble chart for now)
    | - main.py                      Script to run the evaluation
    | - punctual_quality_evaluation  Python class that allows you to create CSV files with quality assessment on a single analysis file.
    |- quality_evaluation_over_time  Python class that allows you to create CSV files with quality assessment on multiple analysis files (quality analysis performed at different times).
    
```