# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 16:03:04 2016

@author: ian
"""

from expanalysis.api import get_results
from expanalysis.utils import clean_df
import pandas
import datetime

f = open('/home/ian/Experiments/expfactory/docs/expfactory_token.txt')
access_token = f.read()
#results = get_results(access_token=access_token)


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

class Results:
    def __init__(self, access_token, clean = True):
        self.data_json = get_results(access_token=access_token) #original data
        self.data = self.results_to_df() #active data
        if clean:
            self.clean_results()
        self.battery = None
        self.experiment = None
        self.worker = None
    
    #*******************************************
    #
    #*******************************************
    def set_battery(self, battery, reset = False):
        '''Subset data to the specific battery, or array of batteries
            battery may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        '''
        if reset:
            self.reset_data()
        self.battery = battery
        self.data = self.select_battery(battery)
    def results_to_df(self):
        if isinstance(self.data_json,list):
            return pandas.DataFrame(self.data_json)
        else:
            print "Results not a list. Must supply loaded results" 

    def clean_results(self):
        '''clean results: remove incomplete experiments and cleans up identifier columns values
        '''
        df = self.data
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
            df.loc[:,'worker'] = [worker['id'].encode('utf-8') for worker in df['worker']]
        else:
            print "Results have already been claned"
        self.data = df
        
    def set_experiment(self, exp_id, reset = False):
        '''Subset data to the specific experiment, or array of experiments
            exp_id may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        '''
        if reset:
            self.reset_data()
        self.experiment = exp_id
        self.data = self.select_experiment(exp_id)
        
    def set_worker(self, worker_id, reset = False):
        '''Subset data to the specific worker, or array of workers. Worker_id
        may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        '''
        if reset:
            self.reset_data()
        self.worker = worker_id
        self.data = self.select_worker(worker_id)
        
    def get_settings(self, silent = False):
        '''Returns the settings for the current active dataset
            (battery, experiment, worker)
        '''
        if silent == False:
            print('Battery: ', self.battery)
            print('Experiment: ', self.experiment)
            print('Worker: ', self.worker)
        return ({'battery': self.battery,
                 'experiment': self.experiment,
                 'worker': self.worker})
        
    def reset_results(self, clean = True):
        self.data = self.results_to_df()
        if clean:
            self.clean_results()
        self.battery = None
        self.experiment = None
        self.worker = None
    
    def get_results(self):
        return self.data
        
    def select_battery(self, battery):
        '''Selects a battery (or batteries) from results object and sorts based on worker and time of experiment completion
        '''
        if isinstance(battery, (unicode, str)):
            battery = [battery]
        df = self.data
        df = df.query("battery in %s" % battery)
        df.sort_values(by = ['worker', 'datetime'], inplace = True)
        df.reset_index(inplace = True)
        return df
        
    def select_experiment(self, exp_id, clean = True, drop_columns = None, drop_na = True):
        '''Selects an experiment (or experiments) from results object and sorts based on worker and time of experiment completion
        '''
        def extract_experiment(df, worker):
            df = df.query("worker == '%s'" % worker)
            #if there are multiple experiments for one worker, check if they are all the same
            assert df['datetime'].value_counts().sum() <= len(exp_id), \
                "More than one experiment out of %s found for %s" % (exp_id, worker)
            trial_list = []
            for i,row in df.iterrows():
                battery = row['battery']
                experiment = row['experiment']
                exp_data = row['data']
                for trial in exp_data:
                    trialdata = trial['trialdata']
                    trialdata['battery'] = battery
                    trialdata['experiment'] = experiment
                    trialdata['dateTime'] = trial['dateTime']
                    trialdata['worker'] = worker
                    trial_list.append(trialdata)
            return trial_list
        
        if isinstance(exp_id, (unicode, str)):
            exp_id = [exp_id]
        df = self.data
        df = df.query("experiment in %s" % exp_id)
        group_trials = []
        for worker in pandas.unique(df.worker):
            group_trials += extract_experiment(df,worker)
        df = pandas.DataFrame(group_trials)
        if clean == True:
            df = clean_df(df, drop_columns, drop_na)
        df.reset_index(inplace = True)
        return df
        
    def select_worker(self, worker):
        '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
        '''
        if isinstance(worker, (unicode, str)):
            worker = [worker]
        df = self.data
        df = df.query("worker in %s" % worker)
        df = df.sort_values(by = ['experiment', 'datetime'])
        df.reset_index(inplace = True)
        return df
        
    #jsPsych specific
    def calc_time_taken(self):
        '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
        '''
        exp_lengths = []
        for i,row in df.iterrows():
            #ensure there is a time elapsed variable
            assert 'time_elapsed' in df.iloc[0]['data'][-1]['trialdata'].keys(), \
                '"time_elapsed" not found for at least one dataset in these results'
            #Set the length of the experiment to the time elapsed on the last 
            #jsPsych trial
            exp_lengths.append(row['data'][-1]['trialdata']['time_elapsed']/1000.0)
        self.data['time_taken'] = exp_lengths
    
    def print_time_taken(self):
        '''Prints time taken for each experiment in minutes
        '''
        assert 'time_taken' in self.data, \
            '"time_taken" has not been calculated yet. Use calc_time_taken method'
        print((df.groupby('experiment')['time_taken'].mean()/60.0).round(2))
        
    


