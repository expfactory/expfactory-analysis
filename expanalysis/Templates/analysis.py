# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from expanalysis.results import Results
from expanalysis.stats import results_check
from expanalysis.experiments.jspsych import *
from expanalysis.processing import extract_experiment
import pandas
import seaborn as sns

#Load Results from Database
f = open('Location of access token')
access_token = f.read().strip()
results = Results(access_token)

#Or from a file
results = Results(results_file = 'Results file Location')

#if you want to export your dataset so you don't have to load it each time...
results.export_data('location')


#You can filter your results based on the battery, experiment, worker
#or finishtime. This will subset the "active" dataset. If you set the parameter
#reset = True, the active dataset will be reset to the original data before 
#filtering

#Filter results to a particular battery, e.g. Self Regulation Pilot
results.filter(battery = 'Your Battery')

#Get data only after a specified date
first_update_time = '2016-04-17T04:24:37.041870Z'
results.filter(finishtime = first_update_time)
results.get_results().groupby('worker').count()


# Basic data quality tool
stats = results_check(results, silent = True, plot = True)
#you can use the function data_check to look at one experiment's dataframe using custom-set
#grouping variables

# Certain functions only work on experiments collected with a particular template
# Below are functions that calculate time taken on jspsych expeirments
#Add time to each experiment
calc_time_taken(results)
time_taken=print_time(results)
time_taken.hist(bins = 20)


# Data is saved in the "active dataset" in an awkward to use way.
# If you want to extract an experiment to a more useable dataframe, do this!

##for adaptive_n_back
nback_df = extract_experiment(results, 'adaptive_n_back')

#You can then export the data using pandas
nback_df.to_csv('location')

#If you just want the data exported you can skip these steps and use expanalysis directly
results.export_experiment('location.csv/json/pkl', 'adaptive_n_back')


