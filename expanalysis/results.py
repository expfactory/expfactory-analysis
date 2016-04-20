'''
expanalysis/results.py: part of expanalysis package
results class

'''
from expanalysis.utils import clean_data, load_result, check_template, get_data
from expanalysis.maths import check_numeric
from expanaysis.testing import validate_result
from expanalysis.api import get_results
import datetime
import pandas
import numpy
import os

class Result:
    def __init__(self,access_token,fields=None,filters=None):
        """Result loads data from expfactory to store in a Results object.
        :param access_token: token obtained from expfactory.org/token when user logged in [required]
        :param fields: top level fields in the result json objects
        """
        if fields == None:
            fields = get_result_fields()

        self.json = get_results(access_token=access_token)
        self.data = None
        self.results_to_df(fields)
        self.clean_results(filters)
    
    def results_to_df(self,fields):
        '''results_to_df converts json result into a dataframe of json objects
        :param fields: list of (top level) fields to parse
        '''
        tmp = pandas.DataFrame(self.json)
        self.df = pandas.DataFrame()
        for field in fields:
            if isinstance(tmp[field].values[0],dict):
                try:
                    field_df = pandas.concat([pandas.DataFrame.from_dict(item, orient='index').T for item in tmp[field]])
                    field_df.index = range(0,field_df.shape[0])
                    field_df.columns = ["%s_%s" %(field,x) for x in field_df.columns.tolist()]
                    self.df = pandas.concat([self.df,field_df],axis=1)
                except:
                    self.df[field] = tmp[field]                   
            else:
                 self.df[field] = tmp[field]                   
                            
    def clean_results(self,filters=None):
        '''clean_results separates incomplete experiments, surveys, and games, and formats data
        :param filters: a dictionary of filter criteria, with key as field name, value as a dictionary
                        with "operator", "value", and "drop" (boolean) to determine filters. See
                        results.get_filters() to see an example
        '''
        if filters == None:
            filters = get_filters()
 
        # Apply user filters
        for filt,params in filters.iteritems():
            if filt in self.data.columns:
            
                # Does the filter have an operator and value?
                if "operator" in params and "value" in params:
                    operator = params["operator"]
                    value = params["value"]
                    try:
                        self.data = self.data.query("%s %s %s" %(filt,operator,value))
                    except:
                        print "Filter %s %s %s not functioning, skipping" %(filt,operator,value)
 
                # Does the filter include request to drop variable?
                if "drop" in params:
                    if params["drop"] == True:
                        self.data = self.data.drop([filt],axis=1)
            
        # Separate empty datasets
        self.empty = self.data[self.data["data"].isnull()==True]
        self.data = self.data[self.data["data"].isnull()==False]  
        if self.empty.shape[0] != 0:
            print 'Empty datasets found! See Results.empty field'
       
    
    def filter(self,field,value):
        '''filter filters results based on a field of interest
        :param field: the field (column) name to filter
        :param value: the value to filter for
        '''
        if self.data != None:
            return self.data[self.data[field] == value]
        else:
            print "ERROR: No results found to filter."
                
    def export(self,file_name):
        """export exports data to path specified by file_name. Must end in .csv, .pkl or .json
        :file_name: full path to export data
        """
        file_name,ext = os.path.splitext(file_name)
        if ext.lower() == ".csv":
            self.data.to_csv(file_name)
        elif ext.lower() == ".pkl":
            self.data.to_pickle(file_name)
        elif ext.lower() == ".json":
            self.data.to_json(file_name)
        else:
            print "File extension not recognized, must be .csv, .pkl, or .json." 

def get_result_fields():
    return ['finishtime',
            'language',
            'battery',
            'completed',
            'worker',
            'platform',
            'experiment',
            'data',
            'browser']

def get_filters():
    '''get_filters returns standard filters for results dataframe.
    ::note

       the keys of the dictionary should be the column names to apply filters to
       Each should be associated with a dictionary with the following fields:
       
       drop [boolean] will drop the field after filter
       operator [str] must be in ["==","<",">","<=",">=","!="
       value [str or int] should correspond to the value to go after the operator
       
    '''
    filters = {"language":{"drop":True},
              "completed": {"drop":True,
                          "operator":"==",
                          "value":True}}
    return filters



# HAVE NOT YET REVIEWED

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
        exp_data = get_data(row)
        for trial in exp_data:
            trial['battery'] = row['battery']
            trial['experiment'] = row['experiment']
            trial['worker'] = row['worker']
            trial['finishtime'] = row['finishtime']
        trial_list += exp_data
    df = pandas.DataFrame(trial_list)
    if clean == True:
        df = clean_data(df, experiment, drop_columns, drop_na)
    df.reset_index(inplace = True)
    return df

    
