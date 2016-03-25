# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:03:04 2016

@author: ian
"""

from expanalysis.api import get_results
import pandas
import datetime

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()
results = get_results(access_token=access_token)

def results_to_df(results):
    if isinstance(results,list):
        df = pandas.DataFrame(results)
        return df
    else:
        print "Results not a list. Must supply loaded results" 
    return df

def clean_results(df):
    '''clean results remove incomplete experiments and cleans up identifier columns values
    '''
    if 'completed' in df.columns:
        #remove partially completed experiments
        df = df.query('completed == True') 
        df = df.drop(['completed', 'language', 'platform', 'browser'], axis = 1)
        df = df.dropna(subset = ['datetime']) #redundancy check, all completed experiments should have a datetime
        #remove battery description and keywords, only keep name
        df.loc[:,'battery'] = [bat['name'] for bat in df['battery']]
        #remove everything from experiment except exp_id
        df.loc[:,'experiment'] = [exp['exp_id'] for exp in df['experiment']]
        #convert datetime to string
        df.loc[:,'datetime'] = [date.encode('utf-8') for date in df['datetime']]
        #replace worker dictionary with string
        df.loc[:,'worker'] = [worker['id'] for worker in df['worker']]
    else:
        print "Results have already been claned"
    return df
    
def select_battery(df, battery_name):
    '''Selects a battery from results object and sorts based on worker and time of experiment completion
    '''
    df = df.query("battery == '%s'" % battery_name)
    df.sort_values(by = ['worker', 'datetime'], inplace = True)
    df.reset_index(inplace = True)
    return df
    
def select_experiment(df, exp_id):
    '''Selects a battery from results object and sorts based on worker and time of experiment completion
    '''
    def extract_experiment(df, worker):
        df = df.query("worker == '%s'" % worker)
        assert len(df) == 1, \
            "More than one %s experiment found for %s" % (exp_id, worker)
        trial_list = []
        for trial in df.data.iloc[0]:
            trialdata = trial['trialdata']
            trialdata['dateTime'] = trial['dateTime']
            trialdata['worker'] = worker
            trial_list.append(trialdata)
        return trial_list
    
    
    df = df.query("experiment == '%s'" % exp_id)
    group_trials = []
    for worker in pandas.unique(df.worker):
        group_trials += extract_experiment(df,worker)
    df = pandas.DataFrame(group_trials)
    df.reset_index(inplace = True)
    return df

def time_diff(t1, t2, output = 'hour'):
    '''Returns time elapsed between two time points. Specify output format as 
    "min", "hour", or "day"
    '''
    divisor = {'min': 60.0, 'hour': 3600.0, 'day': 86400.0}
    FMT = '%Y-%m-%d %H:%M:%S'
    t1 = datetime.datetime.strptime(t1,FMT)
    t2 = datetime.datetime.strptime(t2,FMT)
    diff = (max(t1,t2) - min(t1,t2))
    diff = diff.seconds + diff.days * 86400
    return diff/divisor[output]
    
    
#jsPsych specific

def get_task_stats(df, silent = False):
    '''Returns generic stats about tasks (not questionnaires) including time taken,
    time spent on instructions. Will print out the stats if silent is false
    '''
    stats = {}
    experiments = pandas.unique(df.experiment)
    for exp_id in experiments:
        exp_df = select_experiment(df, exp_id)
        if 'trial_id' in exp_df.columns:
            exp_min = exp_df.groupby('worker').time_elapsed.max()/60000
            exp_min = {'mean': exp_min.mean(), 'std': exp_min.std(), 'unit': 'minute'}
            instruct_sec = exp_df.query('trial_id == "instruction" or trial_id == "instructions"') \
                .groupby('worker').time_elapsed.max()/1000
            instruct_sec = {'mean': instruct_sec.mean(), 'std': instruct_sec.std(), 'unit': 'seconds'}
            stats[exp_id] = {'exp_min': exp_min, \
                                        'instruct_sec': instruct_sec}  
    #if silent is false, print the stats out nicely
    if silent == False:
        rows = [[name, round(i['exp_min']['mean'],2), round(i['instruct_sec']['mean'],2)] \
            for name, i in stats.items()]
        rows = [['exp', 'time (min)', 'instruct time (sec)'],['','', '']] + rows
        for row in rows:
            print("{: >45} {: >20} {: >20}".format(*row)) 
    return stats
            


results = results_to_df(results)
results = clean_results(results)
results = select_battery(results, 'Self Regulation Pilot')
stats = get_task_stats(results)





