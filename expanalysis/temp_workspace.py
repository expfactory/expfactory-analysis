# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from expanalysis.results import Results, extract_experiment
from expanalysis.stats import compute_contrast, compute_regression
from expanalysis.experiments.jspsych import *

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()

results = Results(access_token)
calc_time_taken(results)
time_taken=print_time_taken(results)
time_taken.hist(bins = 20)
results.get_results().groupby('worker').count()


#for stroop
stroop_df = extract_experiment(results, 'stroop')
compute_contrast(stroop_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = False)

