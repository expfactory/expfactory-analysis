'''
analysis/results.py: part of expfactory package
results class

'''

from expanalysis.api import get_results
from utils import clean_df
import pandas

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
            print "results not a list. Must supply loaded results" 

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
            print "results have already been claned"
        self.data = df
    
    def filter(self, battery = None, experiment = None, worker = None, reset = False):
        '''Subset data to the specific battery(s), experiment(s) or worker(s). Each
            attribute may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        '''
        if reset:
            self.reset_data()
        if battery != None:
            assert battery in self.data['battery'].values, \
                "The battery '%s' not found in results. Try resetting the results" % (battery)
            self.battery = battery
            self.data = select_battery(self, battery)
        if experiment != None:
            assert experiment in self.data['experiment'].values, \
                "The experiment '%s' not found in results. Try resetting the results" % (experiment)
            self.experiment = experiment
            self.data = select_experiment(self, experiment)
        if worker != None:
            assert worker in self.data['worker'].values, \
                "The worker ID '%s' not found in results. Try resetting the results" % (worker)
            self.worker = worker
            self.data = select_worker(self, worker)
        
    def get_filters(self, silent = False):
        '''Returns the settings for the current active dataset
            (battery, experiment, worker)
        '''
        if silent == False:
            print 'Battery: ', self.battery
            print 'Experiment: ', self.experiment
            print 'Worker: ', self.worker
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
    

def select_battery(results, battery):
    '''Selects a battery (or batteries) from results object and sorts based on worker and time of experiment completion
    '''
    if isinstance(battery, (unicode, str)):
        battery = [battery]
    df = results.get_results()
    df = df.query("battery in %s" % battery)
    df = df.sort_values(by = ['worker', 'datetime'])
    df.reset_index(inplace = True)
    return df
    
def select_experiment(results, exp_id):
    '''Selects an experiment (or experiments) from results object and sorts based on worker and time of experiment completion
    '''
    if isinstance(exp_id, (unicode, str)):
        exp_id = [exp_id]
    df = results.get_results()
    df = df.query("experiment in %s" % exp_id)
    df = df.sort_values(by = ['worker', 'battery'])
    return df
    
def select_worker(results, worker):
    '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
    '''
    if isinstance(worker, (unicode, str)):
        worker = [worker]
    df = results.get_results()
    df = df.query("worker in %s" % worker)
    df = df.sort_values(by = ['experiment', 'datetime'])
    df.reset_index(inplace = True)
    return df   

def extract_experiments(results, clean = True, drop_columns = None, drop_rows = None, drop_na = True):
    df = results.get_results()
    
    #ensure there is only one dataset for each battery/experiment/worker combination
    assert sum(df.groupby(['battery', 'experiment', 'worker']).size()>1)==0, \
        "More than one dataset found for at least one battery/experiment/worker combination"
    trial_list = []
    for i,row in df.iterrows():
        battery = row['battery']
        experiment = row['experiment']
        worker = row['worker']
        datetime = row['datetime']
        exp_data = row['data']
        for trial in exp_data:
            trialdata = trial['trialdata']
            trialdata['battery'] = battery
            trialdata['experiment'] = experiment
            trialdata['worker'] = worker
            trialdata['datetime'] = datetime
            trial_list.append(trialdata)
    df = pandas.DataFrame(trial_list)
    if clean == True:
        df = clean_df(df, drop_columns, drop_rows, drop_na)
    df.reset_index(inplace = True)
    return df
        
