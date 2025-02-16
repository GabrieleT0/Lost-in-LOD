from quality_evaluation_over_time import QualityEvaluationOT
from punctual_quality_evaluation import PunctualQualityEvaluation
from generate_charts import GenerateCharts
import argparse


def generate_charts():
    #Chart generation
    #Generates a Boxplot for every quality dimension to see the change in the quality dimension score over time
    chart_generator_over_time_dimensions = GenerateCharts('./evaluation_results/over_time/by_dimension','./charts/over_time/by_dimension')
    chart_generator_over_time_dimensions.generate_boxplots_over_time('A')
    chart_generator_over_time_dimensions.swinging_sparql_bubble_chart('./evaluation_results/over_time/by_metric/percentage_of_availability_sparql.csv')

    chart_generator_over_time_dimensions = GenerateCharts('./evaluation_results/over_time/by_dimension','./charts/over_time/by_dimension')

    #Generates a Boxplot for every quality category to see the change in the quality category score over time
    chart_generator_over_time_category = GenerateCharts('./evaluation_results/over_time/by_metric','./charts/over_time/by_metric')
    chart_generator_over_time_category.generate_boxplots_over_time('A')

    #Generates a boxplot with category quality score data with measurements over time, at 3-month intervals
    chart_generator_over_time_category.generate_combined_boxplot_over_time('A','Quality by category','category_score_over_time_quarterly')

    #Generates a boxplot with data statistics of all quality dimensions, with point data from the last analysis available
    chart_generator_punctual_dimensions = GenerateCharts('./evaluation_results/punctual','./charts/punctual')
    chart_generator_punctual_dimensions.generate_boxplots_punctual('evaluation_results/punctual/dimensions_stats.csv','quality_dimensions')

    #Generates a boxplot with data statistics of all quality categories, with point data from the last analysis available
    chart_generator_punctual_dimensions = GenerateCharts('./evaluation_results/punctual','./charts/punctual')
    chart_generator_punctual_dimensions.generate_boxplots_punctual('evaluation_results/punctual/categories_stats.csv','quality_categories','Category')

def filtering():
    #Extract only KGs in the LOD Cloud from the the quality analysis results.
    analysis_over_time = QualityEvaluationOT('./filtered','./evaluation_results/over_time')
    analysis_over_time.extract_only_lodc('./quality_data')

def evaluation():
    print('Running evaluation...')

    #Load all csv with quality data into pandas df. Results are stored as CSV in the ./evaluation_results/over_time
    analysis_over_time = QualityEvaluationOT('./filtered','./evaluation_results/over_time')

    #Load csv with the most recent quality analysis avilable. Results are stored as CSV in the ./evaluation_results/punctual
    punctual_analysis = PunctualQualityEvaluation('./filtered/2025-01-26.csv')

    #Evaluate the Availability of the SPARQL endpoint / VoID file / RDF dump
    punctual_analysis.accessibility_stats()

    #Counts the number of KGs that are accessible and have an open license
    punctual_analysis.get_kgs_available_with_license()

    '''
    Due to the best-effort nature of LOD Cloud Quality Analyzer, if the license is not found on LOD Cloud, the DataHub license is entered, 
    so in this case we have considered only the metadata from LOD Cloud, so if used this two functions below directly, the data obtained will be different, since the data used in this case are the raw data calculated by the tool
    in the /evaluation_results/manually_refined_files/ directory, we entered the csv file from which we extracted the data for the paper given as output by the tool after editing.

    #Calculates the occurrences of the different licenses indicated in the KG metadata.
    punctual_analysis.group_by_value("License machine redeable (metadata)")

    #Compare the license information from the metadata with the license indicated in the KG
    #punctual_analysis.compare_column(['KG id','License machine redeable (metadata)','License machine redeable (query)'],sparql_av=True)
    '''

    #Calculates the occurrences of the different serialization formats indicated in the KG metadata
    punctual_analysis.count_elements_by_type('metadata-media-type')
    
    #Calculates the min, max, mean, q1, q2 for all the quality dimensions monitored.
    punctual_analysis.generate_stats(['Availability score','Licensing score','Interlinking score','Performance score','Accuracy score','Consistency score','Conciseness score',
                    'Verifiability score','Reputation score','Believability score','Volatility score','Completeness score','Amount of data score','Representational-Consistency score','Representational-Conciseness score',
                    'Understandability score','Interpretability score','Versatility score','Security score'],'dimensions_stats',only_sparql_up=True)

    punctual_analysis.generate_stats(['U1-value','CS2-value','IN3-value','RC1-value','RC2-value','IN4-value'],'metrics_to_compare_with_luzzu',only_sparql_up=True)

    #Extract only the KG with at least SPARQL endpoint, VoID file or RDF dump available and the indication about the license.
    punctual_analysis.get_kgs_available_with_license()

    #Evaluate if there is indication about the KG provenance 
    #(metric used for comparizon with LUZZU, not used in the paper because it was not possible to estimate 
    # the value of this metric from the analyses done by Debattista in 2016 and 2019)
    analysis_over_time.evaluate_provenance_info(only_sparql_up=True)
    analysis_over_time.split_verifiability_and_evaluate_score(only_sparql_up=True)
    analysis_over_time.split_trust_value_score(only_sparql_up=True)

    #Calculates the min, max, mean, q1, q2 for CS1-Entities as member of disjoint class and CS5-Invalid usage of inverse-functional properties, CN2-Extensional conciseness
    #(Used for comparison with LUZZU, along with: U1, CS2, IN3, RC1, RC2, IN4 and CS4 calculated before only on the most recent analysis available)
    analysis_over_time.stats_over_time(['Entities as member of disjoint class','Invalid usage of inverse-functional properties','Deprecated classes/properties used'],'by_metric',only_sparql_up=True)
    analysis_over_time.evaluate_conciseness()

    #Analyze the SPARQL endpoint status over time
    #Classify the KG SPARQL endpoint availability over time i.e., whether for a given KG, it was always online, offline, not indicated, or fluctuated in behavior between the 3 states.
    status_df, status_counts, combined_df  = analysis_over_time.classify_sparql_endpoint_availability()

    #For KGs with fluctuating behavior, estimate as a percentage, how many times it was found UP in the reporting period.
    stats, availability_percentage_by_kgid = analysis_over_time.calculate_percentage_of_availability_swinging_sparql(combined_df,status_df)
    analysis_over_time.group_by_availability_percentage(availability_percentage_by_kgid)

    #KGHearBeat only return a quality score for every dimension, this function allows obtaining 
    #the quality score for each of the 6 quality categories defined in literature (the 6 columns will be added to the CSV file).
    analysis_over_time.add_category_score()

    #Evaluate the quality of each category over time, by calculating the q1, min, median, q3, max.
    #(only KGs with the SPARQL endpoint online are considered)
    analysis_over_time.stats_over_time(['Accessibility score','Contextual score','Dataset dynamicity score','Intrinsic score',
                                        'Representational score','Trust score'],'by_category', only_sparql_up=True)
    
    #Evaluate the quality of each category in the punctual analysis, by calculating the q1, min, median, q3, max.
    punctual_analysis = PunctualQualityEvaluation('./filtered/2025-01-26.csv')
    punctual_analysis.generate_stats(['Accessibility score','Contextual score','Dataset dynamicity score','Intrinsic score',
                                        'Representational score','Trust score'],'categories_stats',only_sparql_up=True)

    #Evaluate the quality of each dimension over time, by calculating the q1, min, median, q3, max
    #(only KGs with the SPARQL endpoint online are considered)
    analysis_over_time.stats_over_time([
        'Availability score','Licensing score','Interlinking score','Performance score','Accuracy score','Consistency score','Conciseness score',
        'Verifiability score','Reputation score','Believability score','Currency score','Volatility score','Completeness score','Amount of data score',
        'Representational-Consistency score','Representational-Conciseness score','Understandability score','Interpretability score','Versatility score','Security score','IN4-value','RC2-value'
    ],'by_dimension', only_sparql_up=True)

    generate_charts()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Script with parameter -j o --jump_filtering")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-j", "--jump_filtering", action="store_true", help="If specified, the quality data from the directory ./quality_data will not be filtered by extracting only KGs from LOD CLoud")
    group.add_argument("-c", "--charts_only", action="store_true", help="If specified, the script will only generate charts and skip other processing steps.")
    
    args = parser.parse_args()
    if(args.jump_filtering == True):
        evaluation()
    if(args.charts_only == True):
        generate_charts()
    if(args.jump_filtering == False and args.charts_only == False):
        filtering()
        evaluation()