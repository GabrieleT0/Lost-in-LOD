from quality_evaluation_over_time import QualityEvaluationOT
from punctual_quality_evaluation import PunctualQualityEvaluation

#Load all csv with quality data into pandas df. Results are stored as CSV in the ./evaluation_results/over_time
analysis_over_time = QualityEvaluationOT('./filtered','./evaluation_results/over_time')

#Extract only KGs in the LOD Cloud from the the quality analysis results. 
analysis_over_time.extract_only_lodc('./quality_data')

#Load csv with the most recent quality analysis avilable. Results are stored as CSV in the ./evaluation_results/punctual
punctual_analysis = PunctualQualityEvaluation('./filtered/2024-09-08.csv')

#Evaluate the Availability of the SPARQL endpoint / VoID file / RDF dump
punctual_analysis.accessibility_stats()

#Counts the number of KGs that are accessible and have an open license
punctual_analysis.get_kgs_available_with_license()

#Calculates the occurrences of the different licenses indicated in the KG metadata
punctual_analysis.group_by_value("License machine redeable (metadata)")

#Calculates the occurrences of the different serialization formats indicated in the KG metadata
punctual_analysis.count_elements_by_type('metadata-media-type')
