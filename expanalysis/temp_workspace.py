# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from results import Results, extract_experiments
from stats import compute_contrast

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()

results = Results(access_token)
results.filter(battery = 'Self Regulation Pilot', experiment = 'stroop')
stroop_df = extract_experiments(results)