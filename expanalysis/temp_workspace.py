# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from expanalysis.results import Results, extract_experiment
from expanalysis.stats import compute_contrast, compute_regression, basic_stats
from expanalysis.experiments.jspsych import *

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read().strip()

results = Results(access_token)
if (len(results.get_results()) > 0):
    results.export_data('/home/ian/Experiments/expfactory/data/Pilot2_results_clean.json')
    results.export_data('/home/ian/Experiments/expfactory/data/Pilot2_results_orig.json', orig = True)
results.filter(battery = 'Self Regulation Pilot')

calc_time_taken(results)
time_taken=print_time(results)
time_taken.hist(bins = 20)
results.get_results().groupby('worker').count()

results.filter(experiment = ['stroop','choice_reaction_time'])
basic_stats(results)



#for choice
choice_df = extract_experiment(results, 'choice_reaction_time')

#for adaptive_n_back
nback_df = extract_experiments(results, 'adaptive_n_back')

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



