# Lost in LOD 

### 🌐 [Website with assessment data calculated over the period from January 1, 2024 to September 29, 2024](https://anonymous.4open.science/w/Lost-in-LOD-45AF/)

This repository contains the code to perform the quality evaluation of the KGs registered in the LOD Cloud. The analysis data used for the evaluation are those calculated by KGHeartBeat, a community-shared open-source knowledge graph quality assessment tool to perform quality analysis on a wide range of freely available knowledge graphs registered on the LOD cloud. In order to execute the code of this project, you need to download the quality analysis data collected by [KGHeartBeat](https://github.com/isislab-unisa/KGHeartbeat). 

# Table of contents
- [How to reproduce the experiment](#how-to-reproduce-the-experiment-)
    - [Download quality data computed by KGHeartBeat](#download-quality-data-computed-by-kgheartbeat-)
    - [Execute the project](#execute-the-project-)
- [Repository structure](#repository-structure-)





# How to reproduce the experiment 🔬
In this section we will illustrate how to perform LOD Cloud evaluation from the quality data computed by KGHeartBeat, so as to obtain the values discussed in the paper submitted to The Web Conference 2025 and illustrated in [Placeholder for GitHub pages]()
## Download quality data computed by KGHeartBeat 📂 
This task can be done into two different ways:
1. Download all the data from the [KGHeartBeat Web-App](http://www.isislab.it:12280/kgheartbeat/pages/Download), by selecting the date range of interest, data are put together in a single zip file that contains all quality analyses over the selected period. 
2. Download the files with the analysis results from the following link: [http://isislab.it:12280/kghb_analysis_data/](http://isislab.it:12280/kghb_analysis_data/). Here you can download the quality data as separate zipper files for each available analysis date.

To obtain the evaluation data discussed in the paper submitted to The Web Conference 2025 and those that are viewable on [the GitHub Pages of this project](https://gabrielet0.github.io/LOD-Cloud-Quality-Evaluation/), the quality analyses to be downloaded are all from **2024-01-07** to **2024-09-29**. After you download the quality data, put all the CSV files in the [quality_data](./quality_data/) folder.

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
#### Execute the main.py script
```sh
python main.py
```
As first, the script will take the CSVs files in the [quality_data](./quality_data/) directory and create new CSVs in the [filtered](./filtered/) directory that will contain only KGs that are indexed in the LOD Cloud. 
If you have already run the script, and have the data already filtered, you can skip this step by running the ```main.py``` script with the ```-j True``` option, as shown below:
```sh
python main.py -j True
```
Automatically the script will now populate the evaluation_results folder with the CSV files containing the evaluation data, while the [charts](./charts/) folder will contain the boxplots generated from the evaluation data obtained (look at the next section that shows the [structure of the repository](#repository-structure-) to understand where the resulting files are placed)


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
    | - quality_data                 The quality analysis results provided as output by KGHeartBeat should be placed in this folder in order to run this script.
    | - generate_charts.py           Python class that reads the CSV file containing the quality assessment and generates charts (Boxplot and Bubble chart for now)
    | - main.py                      Script to run the evaluation
    | - punctual_quality_evaluation  Python class that allows you to create CSV files with quality assessment on a single analysis file.
    |- quality_evaluation_over_time  Python class that allows you to create CSV files with quality assessment on multiple analysis files (quality analysis performed at different times).
    
```