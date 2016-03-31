# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from results import Results, extract_experiment
from stats import compute_contrast, compute_regression
from jspsych import *

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()

results = Results(access_token)
calc_time_taken(results)
time_taken=print_time_taken(results)
time_taken.hist(bins = 20)
results.get_results().groupby('worker').count()


#for stroop
stroop_df = extract_experiment(results, 'stroop')
compute_contrast(stroop_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = True)
compute_regression(stroop_df, 'np.log(rt) ~ condition')


#for simon
simon_df = extract_experiment(results, 'simon')
compute_contrast(simon_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = False)
compute_regression(simon_df, 'rt ~ condition')

#for two-stage
two_stage_df = extract_experiment(results,'two_stage_decision', clean = False)

    