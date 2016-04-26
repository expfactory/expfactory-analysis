'''
expanalysis/results.py: part of expfactory package
results class

'''

from expanalysis.api import get_results
from expanalysis.utils import load_result, select_battery, select_experiment, \
     select_worker, select_template, select_finishtime
from expanalysis.processing import extract_experiment
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
        self.finishtime = None
    
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
        #elif 'finishtime' not in self.data:
         #   raise ValidationError('"finishtime" column not found in results')
        
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
            df = df.drop(['completed', 'language'], axis = 1)
            df = df.dropna(subset = ['finishtime']) #redundancy check, all completed experiments should have a datetime
            #remove battery description and keywords, only keep name
            df.loc[:,'battery'] = [bat['name'] for bat in df['battery']]
            #remove everything from experiment except exp_id
            df.loc[:,'experiment'] = [exp['exp_id'] for exp in df['experiment']]
            #if datetime is numeric (in ms), convert to datetime
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
    
    def filter(self, battery = None, experiment = None, worker = None, template = None, finishtime = None, reset = False):
        '''Subset results to the specific battery(s), experiment(s) or worker(s). Each
            attribute may be an array or a string. If reset is true, the data will
            be reset to a cleaned dataframe
        :param battery: a string or array of strings to select the battery(s)
        :param experiment: a string or array of strings to select the experiment(s)
        :param worker: a string or array of strings to select the worker(s)
        :param template: a string or array of strings to select the expfactory templates
        :param finishtime: either a string indicating the time when all data should come after, or a tuple
        with the string, followed by a boolean indicating what select_finishtime should set all_data to
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
        if finishtime != None:
            if isinstance(finishtime, str):
                self.data = select_finishtime(self,finishtime)
                self.finishtime = finishtime
            else:
                self.data = select_finishtime(self, finishtime[0], finishtime[1])
                self.finishtime = finishtime[0]
        
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
            print 'Finishtime: ', self.finishtime
        return ({'battery': self.battery,
                 'experiment': self.experiment,
                 'worker': self.worker,
                 'template': self.template,
                 'finishtime': self.finishtime})
        
    def reset(self, battery = True, experiment = True, worker = True, template = True, finishtime = True, clean = True):
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
        if finishtime:
            self.finishtime = None
    
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
        """ Exports data to path specified by filey. Must be .csv, .pkl or .json
        :filey: path to export data
        :param orig: if True export the original (uncleaned) data, if False exports
        the current active data
        """
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
    
    def export_experiment(self, filey, experiment, clean = True):
        """ Exports data from one experiment to path specified by filey. Must be .csv, .pkl or .json
        :filey: path to export data
        :experiment: experiment to export
        :param clean: boolean, default True. If true cleans the experiment df before export
        """
        df = extract_experiment(self, experiment, clean)
        file_name,ext = os.path.splitext(filey)
        if ext.lower() == ".csv":
            df.to_csv(filey)
        elif ext.lower() == ".pkl":
            df.to_pickle(filey)
        elif ext.lower() == ".json":
            df.to_json(filey)
        else:
            print "File extension not recognized, must be .csv, .pkl, or .json." 


    
