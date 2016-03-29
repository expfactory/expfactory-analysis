# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from results import Results, extract_experiments
from stats import compute_contrast
from jspsych import *

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()

results = Results(access_token)
calc_time_taken(results)
time_taken=print_time_taken(results)
time_taken.hist(bins = 20)

#for stroop
results.filter(battery = 'Self Regulation Pilot', experiment = 'stroop')
drop_rows = {'trial_id': ['welcome', 'instruction', 'attention_check','end', 'fixation']}
stroop_df = extract_experiments(results, drop_rows = drop_rows)
stroop_df.groupby(['condition', 'worker'])['rt'].mean()