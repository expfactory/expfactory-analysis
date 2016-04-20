# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from expanalysis.results import Results, extract_experiment
from expanalysis.stats import compute_contrast, compute_regression, basic_stats
from expanalysis.experiments.jspsych import *
from expanalysis.utils import get_data
import pandas

pandas.set_option('display.width', 200)

##Load Results from Database
#f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
#access_token = f.read().strip()
#results = Results(access_token)
#
##Keep a local copy saved each time
#if (len(results.get_results()) > 0):
#    results.export_data('/home/ian/Experiments/expfactory/data/Pilot2_results_clean.json')
#    results.export_data('/home/ian/Experiments/expfactory/data/Pilot2_results_orig.json', orig = True)
#

#Lad results from File
results = Results(results_file = '/home/ian/Experiments/expfactory/data/Pilot2_results_orig.json')


#Filter results
results.filter(battery = 'Self Regulation Pilot')
#How many tasks has each worker done?
results.get_results().groupby('worker').count()
# worker with complete dataset saved in correct way
worker_complete = 'A07375212LC8D25XBGZ1J'
results.filter(worker = worker_complete, reset = True)
#Add time to each experiment
calc_time_taken(results)
time_taken=print_time(results)
time_taken.hist(bins = 20)


basic_stats(results, silent = True)

#for adaptive_n_back
nback_df = extract_experiments(results, 'adaptive_n_back')

#for ant
ant_df = extract_experiment(results, 'attention_network_task')

#for choice
choice_df = extract_experiment(results, 'choice_reaction_time')

#for CCTC
CCTC_df = extract_experiment(results, 'columbia_card_task_cold')

#for CCTH
CCTH_df = extract_experiment(results, 'columbia_card_task_hot')

#for forget
forget_df = extract_experiment(results, 'directed_forgetting')

#for hierarchical
hierarchical_df = extract_experiment(results, 'hierarchical_rule')

#for ISI
ISI_df = extract_experiment(results, 'information_sampling_task', clean = False)

#for stroop
stroop_df = extract_experiment(results, 'stroop')
compute_contrast(stroop_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = True)
compute_regression(stroop_df, 'numpy.log(rt) ~ condition')


#for simon
simon_df = extract_experiment(results, 'simon')
compute_contrast(simon_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = True)
compute_regression(simon_df, 'rt ~ condition')

#for two-stage
two_stage_df = extract_experiment(results,'two_stage_decision', clean = True)

