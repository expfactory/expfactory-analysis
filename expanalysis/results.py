'''
expanalysis/results.py: part of expfactory package
results class

'''

from expanalysis.api import get_results
from expanalysis.utils import clean_df, load_result, check_template
import pandas
import numpy
import os

class Results:
    def __init__(self, access_token = None, results_file = None, clean = True):
        """ loads data from expfactory or a file and puts it in a Results object.
        
        """
        assert bool(access_token) != bool(results_file), \
            "Supplied an access token and a file to load. Supply one or the other"
        if access_token != None:
            self.data_orig = get_results(access_token=access_token) #original data
            self.data_orig = self.results_to_df()
        else:
            self.data_orig = load_result(results_file)
        self.data = self.data_orig #active data
        self.validate()
        self.clean = clean
        if self.clean:
            self.clean_results()
        self.battery = None
        self.experiment = None
        self.worker = None
        self.template = None
    
    #*******************************************
    #
    #*******************************************
    def validate(self):
        class ValidationError(Exception):
            pass
        if 'battery' not in self.data:
            raise ValidationError('"battery" column not found in results')
        elif 'experiment' not in self.data:
            raise ValidationError('"experiment" column not found in results')
        elif 'worker' not in self.data:
            raise ValidationError('"worker" column not found in results')
        elif 'finishtime' not in self.data:
            raise ValidationError('"datetime" column not found in results')
        
    def results_to_df(self):
        if isinstance(self.data_orig,list):
            return pandas.DataFrame(self.data_orig)
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
            df = df.dropna(subset = ['finishtime']) #redundancy check, all completed experiments should have a datetime
            #remove battery description and keywords, only keep name
            df.loc[:,'battery'] = [bat['name'] for bat in df['battery']]
            #remove everything from experiment except exp_id
            df.loc[:,'experiment'] = [exp['exp_id'] for exp in df['experiment']]
            #convert datetime to string
            df['finishtime'] = df['finishtime'].astype('str')
            #replace worker dictionary with string
            df.loc[:,'worker'] = [worker['id'].encode('utf-8') for worker in df['worker']]
            #see if there are any empty datasets, remove and report them
            empty_data = [len(data) == 0 for data in df['data']]
            if sum(empty_data) != 0:
                print 'Empty datasets found! See below:'
                print df[empty_data]
                df = df[[not x for x in empty_data]] 
        else:
            print "results have already been cleaned"
        self.data = df
    
    def filter(self, battery = None, experiment = None, worker = None, template = None, reset = False):
        '''Subset results to the specific battery(s), experiment(s) or worker(s). Each
            attribute may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        :param battery: a string or array of strings to select the battery(s)
        :param experiment: a string or array of strings to select the experiment(s)
        :param worker: a string or array of strings to select the worker(s)
        :param template: a string or array of strings to select the expfactory templates
        :param reset: boolean. If true calls reset_data before filtering
        '''
        assert self.clean, "The results must be clean to filter"
        if reset:
            self.reset()
        if template != None:
            self.data = select_template(self, template)
            self.template = template
        if worker != None:
            self.data = select_worker(self, worker)
            self.worker = worker
        if battery != None:
            self.data = select_battery(self, battery)
            self.battery = battery
        if experiment != None:
            self.data = select_experiment(self, experiment)
            self.experiment = experiment
        
    def get_filters(self, silent = False):
        '''Returns the settings for the current active dataset
            (battery, experiment, worker)
        :param silent: boolean, if false prints out filters
        '''
        if silent == False:
            print 'Battery: ', self.battery
            print 'Experiment: ', self.experiment
            print 'Worker: ', self.worker
            print 'Template: ', self.template
        return ({'battery': self.battery,
                 'experiment': self.experiment,
                 'worker': self.worker,
                 'template': self.template})
        
    def reset(self, battery = True, experiment = True, worker = True, template = True, clean = True):
        '''resets the data to the original loaded value and cleans if flag is set
        :param clean: boolean, if true cleans the data
        :param battery: boolean, if true reset battery filter
        :param experiment: boolean, if true reset experiment filter
        :param worker: boolean, if true reset worker filter
        '''
        self.data = self.data_orig
        self.clean = clean
        if self.clean:
            self.clean_results()
        if battery:
            self.battery = None
        if experiment:
            self.experiment = None
        if worker:
            self.worker = None
        if template:
            self.template = None
    
    def get_batteries(self):
        '''  Returns array of workers in the active results
        '''
        return numpy.sort(pandas.unique(self.data['battery']))
        
    def get_experiments(self):
        '''  Returns array of workers in the active results
        '''
        return numpy.sort(pandas.unique(self.data['experiment']))
        
    def get_workers(self):
        '''  Returns array of workers in the active results
        '''
        return numpy.sort(pandas.unique(self.data['worker'])) 
        
    def get_results(self):
        '''  Returns results in their current state (cleaned, filtered, etc.)
        '''
        return self.data
        
    def export_data(self, filey, orig = False):
        file_name,ext = os.path.splitext(filey)
        if orig:
            df = self.data_orig
        else:
            df = self.data
        if ext.lower() == ".csv":
            df.to_csv(filey)
        elif ext.lower() == ".pkl":
            df.to_pickle(filey)
        elif ext.lower() == ".json":
            df.to_json(filey)
        else:
            print "File extension not recognized, must be .csv, .pkl, or .json." 

def select_battery(results, battery):
    '''Selects a battery (or batteries) from results object and sorts based on worker and time of experiment completion
    :results: a Results object
    :battery: a string or array of strings to select the battery(s)
    :return df: dataframe containing the appropriate result subset
    '''
    Pass = True
    if isinstance(battery, (unicode, str)):
        battery = [battery]
    df = results.get_results()
    for b in battery:
        if not b in df['battery'].values:
            print "Alert!:  The battery '%s' not found in results. Try resetting the results" % (b)  
            Pass = False
    assert Pass == True, "At least one battery was not found in results"
    df = df.query("battery in %s" % battery)
    df = df.sort_values(by = ['battery', 'experiment', 'worker', 'finishtime'])
    df.reset_index(inplace = True)
    return df
    
def select_experiment(results, exp_id):
    '''Selects an experiment (or experiments) from results object and sorts based on worker and time of experiment completion
    :results: a Results object
    :param exp_id: a string or array of strings to select the experiment(s)
    :return df: dataframe containing the appropriate result subset
    '''
    Pass = True
    if isinstance(exp_id, (unicode, str)):
        exp_id = [exp_id]
    df = results.get_results()
    for e in exp_id:
        if not e in df['experiment'].values:
            print "Alert!: The experiment '%s' not found in results. Try resetting the results" % (e)
            Pass = False
    assert Pass == True, "At least one experiment was not found in results"
    df = df.query("experiment in %s" % exp_id)
    df = df.sort_values(by = ['experiment', 'worker', 'battery', 'finishtime'])
    return df
    
def select_worker(results, worker):
    '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
    :results: a Results object
    :worker: a string or array of strings to select the worker(s)
    :return df: dataframe containing the appropriate result subset
    '''
    Pass = True
    if isinstance(worker, (unicode, str)):
        worker = [worker]
    df = results.get_results()
    for w in worker:
        if not w in df['worker'].values:
            print "Alert!: The experiment '%s' not found in results. Try resetting the results" % (w)
            Pass = False
    assert Pass == True, "At least one worker was not found in results"
    df = df.query("worker in %s" % worker)
    df = df.sort_values(by = ['worker', 'experiment', 'battery', 'finishtime'])
    df.reset_index(inplace = True)
    return df   

def select_template(results, template):
    '''Selects a template (or templates) from results object and sorts based on experiment and time of experiment completion
    :results: a Results object
    :template: a string or array of strings to select the worker(s)
    :return df: dataframe containing the appropriate result subset
    '''
    if isinstance(template, (unicode, str)):
        template = [template]
    template = map(str.lower,template)
    df = results.get_results()
    df = df[[check_template(row['data']) in template for i,row in df.iterrows()]]
    assert len(df) != 0, "At least one template was not found in results"
    df = df.sort_values(by = ['worker', 'experiment', 'battery', 'finishtime'])
    df.reset_index(inplace = True)
    return df
    
def extract_experiment(results, experiment, clean = True, drop_columns = None, drop_na = True):
    '''Returns a dataframe that has expanded the data column of the results object for the specified experiment.
    Each row of this new dataframe is a data row for the specified experiment.
    :results: a Results object
    :experiment: a string identifying one experiment
    :param clean: boolean, if true call clean_df on the data
    :param drop_columns: list of columns to pass to clean_df
    :param drop_na: boolean to pass to clean_df
    :return df: dataframe containing the extracted experiment
    '''
    assert experiment in results.get_experiments(), "Experiment not found in results!"
    df = select_experiment(results, experiment)
    #ensure there is only one dataset for each battery/experiment/worker combination
    assert sum(df.groupby(['battery', 'experiment', 'worker']).size()>1)==0, \
        "More than one dataset found for at least one battery/experiment/worker combination"
    trial_list = []
    for i,row in df.iterrows():
        battery = row['battery']
        experiment = row['experiment']
        worker = row['worker']
        finishtime = row['finishtime']
        exp_data = row['data']
        for trial in exp_data:
            trialdata = trial['trialdata']
            trialdata['battery'] = battery
            trialdata['experiment'] = experiment
            trialdata['worker'] = worker
            trialdata['finishtime'] = finishtime
            trial_list.append(trialdata)
    df = pandas.DataFrame(trial_list)
    if clean == True:
        df = clean_df(df, experiment, drop_columns, drop_na)
    df.reset_index(inplace = True)
    return df

    