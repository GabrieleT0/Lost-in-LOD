import pandas as pd
import os
import requests
import csv
import ast
from collections import Counter
from datetime import datetime
import json
import re

class QualityEvaluationOT:
    def __init__(self,analysis_results_path,output_file='/evaluation_results/over_time'):
        '''
            Creates a list of CSV files that are to be parsed

            :param analysis_results_path: path to the folder that contains the analysis csv files
            :param output_file: Name of the file in which to save the result of the quality assessment
        '''
        self.analysis_results_files = []
        self.output_file = output_file
        # Get all csv filename from the dir
        for filename in os.listdir(analysis_results_path):
            if '.csv' in filename:
                file_path = os.path.join(analysis_results_path, filename)
                self.analysis_results_files.append(file_path)

        self.analysis_results_files = sorted(self.analysis_results_files)

    def load_all_csv_as_one(self,metrics_to_select):
        '''
            Load all csv file in memory as one dataframe.

            :param metrics_to_select: Array of columns to select from the csv fiels.
        '''
        df_list = [pd.read_csv(file, usecols=metrics_to_select) for file in self.analysis_results_files]
        csv_data = pd.concat(df_list, ignore_index=True)
        
        return csv_data
    
    def extract_only_lodc(self,analysis_results_path):
        '''
            Extract only KGs from LODCloud from the csv output from KGs Quality Analyzer.

            :param analysis_results_path: path to csv where to discard the KGs.
        '''
        try:
            response = requests.get("https://lod-cloud.net/versions/latest/lod-data.json")
            kgs = response.json()
        except:
            with open('./lodcloud.json', "r", encoding="utf-8") as file:
                kgs = json.load(file)
       
        identifiers = [data['identifier'] for key, data in kgs.items()]
        # Iterate throught all the csv and create a new csv with only the KGs from LODCloud
        for filename in os.listdir(analysis_results_path):
            if '.csv' in filename:
                file_path = os.path.join(analysis_results_path, filename)
                df = pd.read_csv(file_path)

                identifiers_in_csv = set(df['KG id'].unique())
                missing_identifiers = set(identifiers) - identifiers_in_csv

                print(f"File: {file_path} filtered")

                df['KG id'] = df['KG id'].astype(str).str.strip()
                df_filtered = df[df['KG id'].isin(identifiers)]

                df.drop(df[df['Understandability score'] > 1.0].index, inplace=True)
                #kg_to_mantain = ['nugmyanmar', 'ChimanMaru_Entrepreneur', 'AVsOnto', 'KING', 'orkg', 'ASCDC-Qing-Secret-Societies']
                #df_filtered = df[df['KG id'].isin(kg_to_mantain)]
                print(f"Total number of KG: {df_filtered.shape[0]}")
                only_sparql_up_df = df[(df["Sparql endpoint"] == "Available")] 
                print(f"Total number of KG with SPARQL endpoint Online: {only_sparql_up_df.shape[0]}")
                df_filtered.to_csv(f"filtered/{filename}",index=False)

    def stats_over_time(self, metrics, output_dir,only_sparql_up=True):   
        '''
            For every analysis, calculate the min, max, median, mean, q1, q3 for the specified metrics by considering all KGs in the file.
            Then the data are stored in a csv file.

            :param metrics: string array that contains the exact column name of the csv file for which you want to enter statistics
            :param sparql_availability: boolean if true, consider in statistics, only KGs with an active SPARQL endpoint, if false, all will be considered.
            :param output_dir: path to the directory in which to place the csv files resulting from the evaluation.
        '''
        # loop through every file and calculate data for a boxplot
        for metric in metrics:
            data = []
            print(f"Evaluating the {metric} metric\n")
            data.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])

            # This is necessary for this metric since there was a change to the score calculation after May 5.
            if metric == 'Understandability score':
                start_date = datetime(2024, 5, 5)
                filtered_files = [
                    file for file in self.analysis_results_files
                    if datetime.strptime(file.split('/')[2].split('.')[0], '%Y-%m-%d') > start_date
                ]
            else:
                filtered_files = self.analysis_results_files

            for file_path in filtered_files:
                try:
                    df = pd.read_csv(file_path,usecols=[metric,'Sparql endpoint'])

                    #Exclude KG with SPARQL endpoint offline or not indicated
                    if(only_sparql_up == True):
                        df = df[(df["Sparql endpoint"] == "Available")]

                    df[metric] = pd.to_numeric(df[metric], errors='coerce')
                    min_value = df[metric].min()
                    q1_value = df[metric].quantile(0.25)
                    median_value = df[metric].median()
                    q3_value = df[metric].quantile(0.75)
                    max_value = df[metric].max()
                    mean_value = df[metric].mean()

                    evaluation = [os.path.basename(file_path).split('.')[0],min_value, q1_value, median_value, q3_value, max_value, mean_value]
                    data.append(evaluation)
                except:
                    pass

            here = os.path.dirname(os.path.abspath(__file__))
            if '/' in metric:
                metric = metric.replace('/','-')
            save_path = os.path.join(here,f'{self.output_file}/{output_dir}/{metric}.csv')
            with open(save_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data)
    
    def add_category_score(self):
        """
            Add a the category score in the original CSV returned by KGs Quality Analyzer, the value is calculated as the sum of the dimensions score for that category, divided by the number of dimensions for that category.
        """
        categories = {
            "Intrinsic score" : {
                "Accuracy score" : 0,
                "Interlinking score" : 0,
                "Consistency score" : 0,
                "Conciseness score" : 0,
            },
            "Dataset dynamicity score" : {
                "Currency score" : 0,
                "Volatility score" : 0,
            },
            "Trust score" : {
                "Verifiability score" : 0,
                "Reputation score" : 0,
                "Believability score" : 0,
            },
            "Contextual score" : {
                "Completeness score" : 0,
                "Amount of data score" : 0,
            },
            "Representational score" : {
                "Representational-Consistency score": 0,
                "Representational-Conciseness score" : 0,
                "Interpretability score" : 0,
                "Versatility score" : 0
            },
            "Accessibility score": {
                "Availability score" : 0,
                "Licensing score" : 0,
                "Security score" : 0,
                "Performance score" : 0,
            }
        }

        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)
            for key in categories:
                category = categories[key]
                dimensions_in_cat = category.keys()
                df[key] = df[dimensions_in_cat].sum(axis=1) / len(dimensions_in_cat)
            
            df.to_csv(file_path,index=False)
    
    def evaluate_provenance_info(self,only_sparql_up=True):
        '''
            Evaluate the provenance metrics by checking if an author or a publisher is indicated in the KG.
        '''
        data = []
        data.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)

            if(only_sparql_up == True):
                df = df[(df["Sparql endpoint"] == "Available")]

            df['P1'] = df.apply(lambda row: 1 if (row['Author (metadata)'] != 'False' or (row['Publisher'] != '-' and row['Publisher'] != '[]' and row['Publisher'] != 'absent')) else 0, axis=1)
        
            df['P1'] = pd.to_numeric(df['P1'], errors='coerce')
            min_value = df['P1'].min()
            q1_value = df['P1'].quantile(0.25)
            median_value = df['P1'].median()
            q3_value = df['P1'].quantile(0.75)
            max_value = df['P1'].max()
            mean_value = df['P1'].mean()

            evaluation = [os.path.basename(file_path).split('.')[0],min_value, q1_value, median_value, q3_value, max_value, mean_value]
            data.append(evaluation)

        here = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(here,f'{self.output_file}/by_metric/P1-Provenance_information.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def split_trust_value_score(self, only_sparql_up = True):
        data_description = []
        data_name = []
        data_web = []
        data_description.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_name.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_web.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])

        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)

            if(only_sparql_up == True):
                df = df[(df["Sparql endpoint"] == "Available")]
            
            df[['Web', 'Name', 'Email']] = df['Sources'].apply(self.extract_fields_from_sources)
            df['Web-value'] = df.apply(lambda row: 1 if (row['Web'] != 'absent' and row['Web'] != '' and row['Web'] != 'Absent') else 0, axis=1)
            df['Web-value'] = pd.to_numeric(df['Web-value'], errors='coerce')

            df['Description-value'] = df.apply(lambda row: 1 if (row['Description'] != 'absent' and row['Description'] != '' and row['Description'] != 'False' and row['Description'] != False) else 0, axis=1)
            df['Description-value'] = pd.to_numeric(df['Description-value'], errors='coerce')

            df['Name-value'] = df.apply(lambda row: 1 if (row['KG name'] != 'absent' and row['KG name'] != '' and row['KG name'] != 'False' and row['KG name'] != False) else 0, axis=1)
            df['Name-value'] = pd.to_numeric(df['Name-value'], errors='coerce')

            min_value_description = df['Description-value'].min()
            q1_value_description = df['Description-value'].quantile(0.25)
            median_value_description = df['Description-value'].median()
            q3_value_description = df['Description-value'].quantile(0.75)
            max_value_description = df['Description-value'].max()
            mean_value_description = df['Description-value'].mean()

            evaluation_description = [os.path.basename(file_path).split('.')[0],min_value_description, q1_value_description, median_value_description, q3_value_description, max_value_description, mean_value_description]
            data_description.append(evaluation_description)

            min_value_name = df['Name-value'].min()
            q1_value_name = df['Name-value'].quantile(0.25)
            median_value_name = df['Name-value'].median()
            q3_value_name = df['Name-value'].quantile(0.75)
            max_value_name = df['Name-value'].max()
            mean_value_name = df['Name-value'].mean()

            evaluation_name = [os.path.basename(file_path).split('.')[0],min_value_name, q1_value_name, median_value_name, q3_value_name, max_value_name, mean_value_name]
            data_name.append(evaluation_name)

            min_value_web = df['Web-value'].min()
            q1_value_web = df['Web-value'].quantile(0.25)
            median_value_web = df['Web-value'].median()
            q3_value_web = df['Web-value'].quantile(0.75)
            max_value_web = df['Web-value'].max()
            mean_value_web = df['Web-value'].mean()

            evaluation_web = [os.path.basename(file_path).split('.')[0],min_value_web, q1_value_web, median_value_web, q3_value_web, max_value_web, mean_value_web]
            data_web.append(evaluation_web)
        
        here = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(here,f'{self.output_file}/by_metric/Description-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_description)
        
        save_path = os.path.join(here,f'{self.output_file}/by_metric/Name-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_name)

        save_path = os.path.join(here,f'{self.output_file}/by_metric/Web-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_web)
        
    def split_verifiability_and_evaluate_score(self,only_sparql_up = True):
        data_vocabs = []
        data_authors = []
        data_contributors = []
        data_publishers = []
        data_sign = []
        data_sources = []
        data_vocabs.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_authors.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_contributors.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_publishers.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_sign.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        data_sources.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])

        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)

            if(only_sparql_up == True):
                df = df[(df["Sparql endpoint"] == "Available")]

            df['Vocabs-value'] = df.apply(lambda row: 1 if (row['Vocabularies'] != '-' and row['Vocabularies'] != '[]') else 0, axis=1)
            df['Vocabs-value'] = pd.to_numeric(df['Vocabs-value'], errors='coerce')

            df['Author-value'] = df.apply(lambda row: 1 if ((row['Author (query)'] != '-' and row['Author (query)'] != '[]') or (row['Author (metadata)']) != 'False' and row['Author (metadata)'] != False) else 0, axis=1)
            df['Author-value'] = pd.to_numeric(df['Author-value'], errors='coerce')

            df['Contributors-value'] = df.apply(lambda row: 1 if (row['Contributor'] != '-' and row['Contributor'] != '[]' and row['Contributor'] != 'absent') else 0, axis=1)
            df['Contributors-value'] = pd.to_numeric(df['Contributors-value'], errors='coerce')

            df['Publishers-value'] = df.apply(lambda row: 1 if (row['Publisher'] != '-' and row['Publisher'] != '[]' and row['Publisher'] != 'absent') else 0, axis=1)
            df['Publishers-value'] = pd.to_numeric(df['Publishers-value'], errors='coerce')

            df['Sign-value'] = df.apply(lambda row: 1 if (row['Signed'] == True) else 0, axis=1)
            df['Sign-value'] = pd.to_numeric(df['Sign-value'], errors='coerce')
            
            df[['Web', 'Name', 'Email']] = df['Sources'].apply(self.extract_fields_from_sources)

            df['Sources-value'] = df.apply(lambda row: 1 if ((row['Web'] != 'absent' or row['Name'] != 'absent' or row['Email'] != 'absent') and row['Web'] != '' or row['Name'] != '' or row['Email'] != '') else 0, axis=1)
            df['Sources-value'] = pd.to_numeric(df['Sources-value'], errors='coerce')

            min_value_vocabs = df['Vocabs-value'].min()
            q1_value_vocabs = df['Vocabs-value'].quantile(0.25)
            median_value_vocabs = df['Vocabs-value'].median()
            q3_value_vocabs = df['Vocabs-value'].quantile(0.75)
            max_value_vocabs = df['Vocabs-value'].max()
            mean_value_vocabs = df['Vocabs-value'].mean()

            evaluation_vocabs = [os.path.basename(file_path).split('.')[0],min_value_vocabs, q1_value_vocabs, median_value_vocabs, q3_value_vocabs, max_value_vocabs, mean_value_vocabs]
            data_vocabs.append(evaluation_vocabs)

            min_value_authors = df['Author-value'].min()
            q1_value_authors = df['Author-value'].quantile(0.25)
            median_value_authors = df['Author-value'].median()
            q3_value_authors = df['Author-value'].quantile(0.75)
            max_value_authors = df['Author-value'].max()
            mean_value_authors = df['Author-value'].mean()

            evaluation_authors = [os.path.basename(file_path).split('.')[0],min_value_authors, q1_value_authors, median_value_authors, q3_value_authors, max_value_authors, mean_value_authors]
            data_authors.append(evaluation_authors)

            min_value_contributors = df['Contributors-value'].min()
            q1_value_contributors = df['Contributors-value'].quantile(0.25)
            median_value_contributors = df['Contributors-value'].median()
            q3_value_contributors = df['Contributors-value'].quantile(0.75)
            max_value_contributors = df['Contributors-value'].max()
            mean_value_contributors = df['Contributors-value'].mean()

            evaluation_contributors = [os.path.basename(file_path).split('.')[0],min_value_contributors, q1_value_contributors, median_value_contributors, q3_value_contributors, max_value_contributors, mean_value_contributors]
            data_contributors.append(evaluation_contributors)

            min_value_publishers = df['Publishers-value'].min()
            q1_value_publishers = df['Publishers-value'].quantile(0.25)
            median_value_publishers = df['Publishers-value'].median()
            q3_value_publishers = df['Publishers-value'].quantile(0.75)
            max_value_publishers = df['Publishers-value'].max()
            mean_value_publishers = df['Publishers-value'].mean()

            evaluation_publishers = [os.path.basename(file_path).split('.')[0],min_value_publishers, q1_value_publishers, median_value_publishers, q3_value_publishers, max_value_publishers, mean_value_publishers]
            data_publishers.append(evaluation_publishers)

            min_value_sign = df['Sign-value'].min()
            q1_value_sign = df['Sign-value'].quantile(0.25)
            median_value_sign = df['Sign-value'].median()
            q3_value_sign = df['Sign-value'].quantile(0.75)
            max_value_sign = df['Sign-value'].max()
            mean_value_sign = df['Sign-value'].mean()

            evaluation_sign = [os.path.basename(file_path).split('.')[0],min_value_sign, q1_value_sign, median_value_sign, q3_value_sign, max_value_sign, mean_value_sign]
            data_sign.append(evaluation_sign)

            min_value_sources = df['Sources-value'].min()
            q1_value_sources = df['Sources-value'].quantile(0.25)
            median_value_sources = df['Sources-value'].median()
            q3_value_sources = df['Sources-value'].quantile(0.75)
            max_value_sources = df['Sources-value'].max()
            mean_value_sources = df['Sources-value'].mean()

            evaluation_sources = [os.path.basename(file_path).split('.')[0],min_value_sources, q1_value_sources, median_value_sources, q3_value_sources, max_value_sources, mean_value_sources]
            data_sources.append(evaluation_sources)

        here = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(here,f'{self.output_file}/by_metric/Vocabs-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_vocabs)

        save_path = os.path.join(here,f'{self.output_file}/by_metric/Author-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_authors)

        save_path = os.path.join(here,f'{self.output_file}/by_metric/Contributors-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_contributors)

        save_path = os.path.join(here,f'{self.output_file}/by_metric/Publishers-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_publishers)
        
        save_path = os.path.join(here,f'{self.output_file}/by_metric/Sign-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_sign)

        save_path = os.path.join(here,f'{self.output_file}/by_metric/Sources-value.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data_sources)

    def evaluate_integer_metrics(self,metric,new_column_name):
        '''
            Evaluates the quality of metrics that have list as their value.
            
            :param metric the metric name to evaluate.
            :param new_column_name the column name in which insert the number of elements in the measured meatric.
        '''
        data = []
        data.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)
            for idx, list_string in enumerate(df[metric]):
                try:
                    list_elements = ast.literal_eval(list_string)
                    if isinstance(list_elements, list):
                        df.at[idx, new_column_name] = len(list_elements)
                except Exception as error:
                   continue
            
            df[new_column_name] = pd.to_numeric(df[new_column_name], errors='coerce')
            min_value = df[new_column_name].min()
            q1_value = df[new_column_name].quantile(0.25)
            median_value = df[new_column_name].median()
            q3_value = df[new_column_name].quantile(0.75)
            max_value = df[new_column_name].max()
            mean_value = df[new_column_name].mean()

            evaluation = [os.path.basename(file_path).split('.')[0],min_value, q1_value, median_value, q3_value, max_value, mean_value]
            data.append(evaluation)
        
        here = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(here,f'{self.output_file}/{metric}.csv')
        with open(save_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    def evaluate_conciseness(self):
        '''
            Evaluate the extensional conciseness metric.
        '''
        data = []
        data.append(['Analysis date', 'Min', 'Q1', 'Median', 'Q3', 'Max', 'Mean'])
        for file_path in self.analysis_results_files:
            df = pd.read_csv(file_path)
            for idx, value in enumerate(df['Extensional conciseness']):
                conc_value = value.split(' ')[0]
                df.at[idx, 'CN2'] = conc_value
            
            df['CN2'] = pd.to_numeric(df['CN2'], errors='coerce')
            min_value = df['CN2'].min()
            q1_value = df['CN2'].quantile(0.25)
            median_value = df['CN2'].median()
            q3_value = df['CN2'].quantile(0.75)
            max_value = df['CN2'].max()
            mean_value = df['CN2'].mean()

            evaluation = [os.path.basename(file_path).split('.')[0],min_value, q1_value, median_value, q3_value, max_value, mean_value]
            data.append(evaluation)
        
        here = os.path.dirname(os.path.abspath(__file__))
        save_path = os.path.join(here,f'{self.output_file}/by_metric/extensional_conciseness.csv')
        with open(save_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    def classify_sparql_endpoint_availability(self,column_name='Sparql endpoint'):
        '''
            Analyze the SPARQL endpoint availabilty over time, Classifying the behavior into:
                - Always online
                - Always not specified
                - Always offline
                - Swinging

            :param column_name: string that is the column name which contains the SPARQL endpoint status.
        '''
        # Load CSV into one dataframe
        
        # We restrict the observation period to this interval, as there were no new KGs analyzed that could alter the data 
        # (if a KG is monitored only once (in the last analysis for example) and found UP, it would go into those ALWAYS UP and with a HIGH percentage of availability.
        start_date = datetime(2024, 3, 17)
        end_date = datetime(2024, 9, 1)

        filtered_files = [
            file for file in self.analysis_results_files
            if start_date <= datetime.strptime(file.split('/')[2].split('.')[0], '%Y-%m-%d') <= end_date
        ]

        df_list = [pd.read_csv(file, usecols=['KG id', 'Sparql endpoint','SPARQL endpoint URL']) for file in filtered_files]
        df = pd.concat(df_list, ignore_index=True)

        df[column_name] = df[column_name].str.strip()

        # Classify the status of every KG kg_id
        def classify_kg_status(sub_df):
            unique_statuses = sub_df[column_name].unique()
            if len(unique_statuses) == 1:
                return unique_statuses[0]
            else:
                return 'Alternating'

        # group by kg_id and use the classification function
        status_df = df.groupby('KG id').apply(classify_kg_status).reset_index(name='Status')

        # Count how many available, offline and laternating
        status_counts = status_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']

        status_counts.to_csv('./evaluation_results/over_time/by_metric/sparql_over_time.csv',index=False)

        return status_df, status_counts, df
    
    def calculate_percentage_of_availability_swinging_sparql(self,df, status_df, column_name='Sparql endpoint'):
        '''
            Calculate the percentage of SPARQL endpoint availability for every KGs analyzed.

            :param df: the dataframe with all the data quality calculated over time aggregated togheter.
            :param status_df: dataframe with the "Status" column, which contains the SPARQL endpoint status for every KGs analyzed over time
        '''
        # Filter for alternating KG ids
        alternating_kg_ids = status_df[status_df['Status'] == 'Alternating']['KG id']
        
        # Calculate the availability percentage for each alternating KG id
        availability_percentages = []
        availability_percentage_by_kgid = {}
        for kg_id in alternating_kg_ids:
            kg_df = df[df['KG id'] == kg_id]
            total_count = len(kg_df)
            available_count = len(kg_df[kg_df[column_name] == 'Available'])
            availability_percentage = (available_count / total_count) * 100
            availability_percentages.append(availability_percentage)
            availability_percentage_by_kgid[kg_id] = availability_percentage

        # Calculate the overall average availability percentage for all alternating KG ids
        overall_average_availability_percentage = df[df['KG id'].isin(alternating_kg_ids) & (df[column_name] == 'Available')].shape[0] / df[df['KG id'].isin(alternating_kg_ids)].shape[0] * 100

        stats = {
            'min': min(availability_percentages) if availability_percentages else 0,
            'max': max(availability_percentages) if availability_percentages else 0,
            'median': pd.Series(availability_percentages).median() if availability_percentages else 0,
            'q1': pd.Series(availability_percentages).quantile(0.25) if availability_percentages else 0,
            'q3': pd.Series(availability_percentages).quantile(0.75) if availability_percentages else 0,
            'std': pd.Series(availability_percentages).std() if availability_percentages else 0,
            'mean': pd.Series(availability_percentages).mean() if availability_percentages else 0,
            'overall_average': overall_average_availability_percentage
        }

        return stats,availability_percentage_by_kgid
    
    def group_by_availability_percentage(self,availability_percentage_by_kgid):
        '''
            Groub by percentage of SPARQL endpoint availability

            :param availability_percentage_by_kgid: dict with the percentace of SPARQL endpoint availability for every KG analyzed.
        '''
        grouped_counts = Counter(availability_percentage_by_kgid.values())

        df = pd.DataFrame(grouped_counts.items(), columns=['Percentage of availability', 'Number of KGs'])

        df.to_csv('./evaluation_results/over_time/by_metric/percentage_of_availability_sparql.csv', index=False)

    def extract_fields_from_sources(self,text):
        pattern = r'Web:\s*(\S+)?\s*Name:\s*([^,]+)?\s*Email:\s*([\w\.-]+@[\w\.-]+\.\w+)?'
        match = re.search(pattern, text)

        if match:
            web = match.group(1) if match.group(1) else "absent"
            name = match.group(2) if match.group(2) else "absent"
            email = match.group(3) if match.group(3) else "absent"
            return pd.Series([web, name.strip(), email])

        return pd.Series(["absent", "absent", "absent"])
