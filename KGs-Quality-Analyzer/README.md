# KGs Quality Analyzer
This tool allows you to analyze the quality of all Knowledge Graphs automatically recoverable from [Linked Open data Cloud (LODC)](https://lod-cloud.net) and [DataHub](https://old.datahub.io/) (the tool can easily be extended to include other KGs aggregators).
- [KGs Quality Analyzer](#kgs-quality-analyzer)
    - [Repository structure](#repository-structure)
    - [Quality metrics covered](#quality-metrics-covered)
    - [Examples](#examples)
    - [Test](#test)
    - [Performance](#performance)
    - [License](#license)

- [How to use KGs Quality Analyzer?](#how-to-use-lod-cloud-quality-analyzer)
    - [Dependencies](#dependencies)
    - [Input configuration](#input-configuration)
    - [Results](#results)
    - [Look directly the quality](#look-directly-the-quality)
- [How include a new quality metric?](#how-include-a-new-quality-metric)

## Repository structure
```
KGs Quality Analyzer
    | - Analysis results/       Directory with KGs data quality obtained from measurement.
        |- YYYY-MM-DD.csv     
    | - API/                   
        |- AGAPI                Interface to KnowledgeGraph search engine.
        |- Aggregator.py        Brings together all the metadata for the KG from the various services used.
        |- DataHubAPI.py        Module to retrieve KGs metadata from DataHub.
        |- LODCloudAPI.py       Module to retrieve KGs metadata from LODCloud.
        |- LOVAPI.py            Module used to retrieve standard vocabularies and terms from LOV.
    | - examples/               Contains example on how to use KGs Quality Analyzer
    | - QualityDimensions       All classes representing the measured quality dimensions.
        |- AmountOfData.py
        |- Availability.py
        |- Believability.py
        ...
        ...
        ...
    | - test/                   Folder containing files and scripts relating to the test
        |- analyses_test.py     Script to run the test 
        |- SPARQLES_APIS.py     Module used as interface to the SPARQLES API.
        |- test_output.txt      File containing the result of the test performed.
    | - analyses.py             Module that calculates all quality metrics.
    | - bloomfilter.py          Class used to istantiate the Bloom-Filter structure.
    | - Configuration.py        Module used to create the configration.json file if isn't available.
    | - ExternalLink.py         Class used to model the external links of a KG.
    | - Graph.py  Module        Used to build the graph with all the KGs and to calculate all the interlinking dimension metric.
    | - InputValidator.py       Abstract class to validate the input.
    | - JsonValidator.py        Class that implements the validation of JSON files in input.
    | - KnowledgeGraph.py       Class that contains the quality data of for the KG.
    | - manager.py              Module responsible for orchestrating the application and calling the various modules for analysis.
    | - MetricsOutput.py        Abstract class to return output from the application.
    | - OutputCSV.py            Class used to shape the output in CSV format.
    | - query.py                Contains all the queries needed to calculate quality metrics.
    | - Resources.py            Class used to aggregate all resources available for the analyzed KG.
    | - score.py                Class that calculates the score for each quality dimension analyzed and the total score
    | - Sources.py              Class with all info related to the KG sources.
    | - utils.py                Aggregates all useful functions for calculating quality metrics.
    | - VoIDAnalyses.py         Module used for parsing and extracting all useful information from the VoID file

```
![architecture](./architecture.png)

## Quality metrics covered
Below is a graph showing the quality dimensions covered by KGs Quality Analyzer and the percentage of metrics measured in each of them.

![Quality metrics covered by KGs Quality Analyzer](quality_metrics.png)


The following figure shows the percentage of sizes and categories covered by KGs Quality Analyzer.
![Quality category and quality dimensions covered by LOD Cloud Analyzer](./img/dimension_and_metrics_coverage.png)

## Test
The test was performed by comparing KGs Quality Analyzer with [SPARQLES](https://sparqles.demo.openlinksw.com/). For more info about the test and the result go to the [test readme](./test/README.md).

## Performance
At the end of the analysis execution, in the [Analysis results](./Analysis%20results/) directory there will be a ```performance-yyyy-yy-yy.txt``` file, which will contain various information on the time taken for the analysis of each KG (with the time for the calculation of each metric) and the time of the analysis in total. The performance data that we illustrate below, and the file provided in the repository, refer to the analysis of all the KGs automatically discoverable carried out on 2023/12/24.

|Total KGs analyzed|Total time (hours)| Average time for the analysis of one KGs (minutes)| Standard deviation (minutes) |
|---|---|---|----|
|1882|89.40 ~ 4 days|2.82|21.24|

The KG that required the longest time for analysis was **B3Kat - Library Union Catalogues of Bavaria, Berlin and Brandenburg**, the total time was: ~6.77 hours. The quality metric that took the longest time to analyze was *Intrinsic Category -> Consistency -> Undefined classes*, with ~5 hours to complete the calculation, this is mainly due to the large amount of triples that are present in this KG (1.022.898.443 of triples).
The box plot illustred below shows the times for calculating the quality for each KGs. ![Quality-Analysis-Time](./kgs_analysis_time.png)

## License
KGs Quality Analyzer is licensed under the [MIT License](https://opensource.org/license/mit/).

# How to Use KGs Quality Analyzer 
This section provides an overview about the use of KGs Quality Analyzer and how it can be extended.

## Dependencies
For the execution of the project it is recommended to create a Python Virtual Environment.

First of all, install all dependencies from the project root:
```
pip install -r requirements.txt
```
## Input configuration
From the [KG-quality-analysis/configuration.json](configuration.json) file, you can choose the Knowledge Graph to analyze. You can analyze it by using a list of keywords or ids. In the example below, all the Knowledge Graphs that have the keywords *"museum"* will be analyzed.
```
{"name": ["museum"], "id": []}
```
Or, by a list of ids like this:
```
{"name": [], "id": ["dbpedia","taxref-ld"]}
```
If instead, you want to analyze all the Knowledge Graphs automatically discoverable from [LODCloud](https://lod-cloud.net/) and [DataHub](https://old.datahub.io/):
<a name="all-kgs-conf"></a>
```
{"name": [], "id": []}
```
After the input configuration, to execute the analysis simply launch form the main directory of the project:
```
python3 manager.py
```
## Results
The results of the analysis will be inserted in a .csv file in the *"Analysis results"* directory, along with a .log file containing any errors that occurred during the measurement. Each line of the csv file representa a KG, and on the columns we find the different quality metrics analyzed.

## How include a new quality metric?
If you want to include a new quality metric, you need to include the calculation inside the [analyses.py](analyses.py) module. If this new metric requires the use of a new query on the SPARQL endpoint, you can add a new query in the [query.py](query.py) module and call it from the [analyses.py](analyses.py) module .Then, based on the quality dimension to which it belongs, modify the related class in the [QualityDimensions](/QualityDimensions/) folder, or create a new class if this belongs to a new dimension. If you created a new dimension for the new metric, it must be included in the [KnowledgeGraph.py](KnowledgeGraph.py) class. Then instantiate the classes in the [analyses.py](analyses.py) to assign the value obtained from the new quality metric. If you want also to see this new metric in the csv file given in output, you need to edit the [OutputCSV.py](OutputCSV.py) module appropriately. Essentially you have to include a new header, having as name the name of the new metric and then recall the value of the metric from the [KnowledgeGraph.py](KnowledgeGraph.py) object appropriately constructed in the [analyses.py](analyses.py) module.
