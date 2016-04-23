# -*- coding: utf-8 -*-
"""
Temporary file for testing analysis
"""

from expanalysis.results import Results
from expanalysis.stats import compute_contrast, compute_regression, results_check
from expanalysis.experiments.jspsych import *
from expanalysis.processing import extract_experiment
import pandas
import seaborn as sns

%matplotlib inline
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


#Lad results from File
results = Results(results_file = '/home/ian/Experiments/expfactory/data/Pilot2_results_orig.json')


#Filter results
results.filter(battery = 'Self Regulation Pilot')
#How many tasks has each worker done?
results.get_results().groupby('worker').count()
# time when data structure was updated
update_time = '2016-04-17T04:24:37.041870Z'
complete_wokrer = 'A07375212LC8D25XBGZ1J'
results.filter(finishtime = update_time)
#Add time to each experiment
calc_time_taken(results)
time_taken=print_time(results)
time_taken.hist(bins = 20)


stats = results_check(results, silent = True, plot = True)

#for adaptive_n_back
nback_df = extract_experiment(results, 'adaptive_n_back')

#for ant
ant_df = extract_experiment(results, 'attention_network_task')

#for ant
df = extract_experiment(results, 'angling_risk_task_always_sunny')

#for choice
choice_df = extract_experiment(results, 'choice_reaction_time')

#for CCTC
CCTC_df = extract_experiment(results, 'columbia_card_task_cold')

#for CCTH
CCTH_df = extract_experiment(results, 'columbia_card_task_hot')

#for dpx
dpx_df = extract_experiment(results,'dot_pattern_expectancy')

#for forget
forget_df = extract_experiment(results, 'directed_forgetting')

#for keep track
keep_df = extract_experiment(results, 'keep_track')

#for kirby track
kirby_df = extract_experiment(results, 'kirby')

#for hierarchical
hierarchical_df = extract_experiment(results, 'hierarchical_rule')

#for ISI
ISI_df = extract_experiment(results, 'information_sampling_task')

# for probabilistic selection
prob_df = extract_experiment(results, 'probabilistic_selection')

#for simon
shift_df = extract_experiment(results, 'shift_task')

#for simon
simon_df = extract_experiment(results, 'simon')

#for span
digit_df = extract_experiment(results, 'digit_span')
spatial_df = extract_experiment(results, 'spatial_span')

#for stop
stop_df = extract_experiment(results, 'stop_signal')
motor_df =  extract_experiment(results, 'motor_selective_stop_signal')
stim_df =  extract_experiment(results, 'stim_selective_stop_signal')

#for stroop
stroop_df = extract_experiment(results, 'stroop')

#for threebytwo
three_df = extract_experiment(results, 'threebytwo')

#for two stage
two_df = extract_experiment(results, 'two_stage_decision')
reward_probs = [x for x in two_df['FB_probs'] if type(x) == list]
sns.plt.plot(reward_probs)


compute_contrast(stroop_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = True)
compute_regression(stroop_df, 'numpy.log(rt) ~ condition')


#for simon
simon_df = extract_experiment(results, 'simon')
compute_contrast(simon_df, ind_var = 'condition', dep_var = 'rt', drop_rows = {'rt': -1}, plot = True)
compute_regression(simon_df, 'rt ~ condition')

#for two-stage
two_stage_df = extract_experiment(results,'two_stage_decision', clean = True)

for i in xrange(40,64):
    data = extract_experiment(results,results.get_experiments()[i])
    if 'trial_id' in data.columns:
        print('**************************')
        print numpy.unique(data[['trial_id','exp_id']])

