'''
expanalysis/results.py: part of expanalysis package
results class

'''
from expanalysis.maths import check_numeric
from expanalysis.testing import validate_result
from expanalysis.api import get_results
from expanalysis.utils import save_json
import datetime
import pandas
import numpy
import json
import os

class Result:
    def __init__(self,access_token=None,fields=None,filters=None):
        """Result loads data from expfactory to store in a Results object.
        :param access_token: token obtained from expfactory.org/token when user logged in
        :param fields: top level fields in the result json objects (not required)
        :param filters: filters to clean results (not required)
        """
        if fields == None:
            fields = get_result_fields()
        if filters == None:
            filters = get_filters()
        self.data = None
        self.fields = fields
        self.filters = filters
 
        # If access token is provided, parse immediately
        if access_token != None:
            self.json = get_results(access_token=access_token)
            self.results_to_df(fields)
            self.clean_results(filters)
    
    def load_results(self,json_file):
        '''load_results will load a saved json object result
        :param json_file: the json file to load
        '''
        self.json = json.load(open(json_file,"rb"))
        self.results_to_df(self.fields)
        self.clean_results(self.filters)
        return self.data

    def results_to_df(self,fields = None):
        '''results_to_df converts json result into a dataframe of json objects
        :param fields: list of (top level) fields to parse
        '''
        if fields == None:
            fields = self.fields
        tmp = pandas.DataFrame(self.json)
        self.data = pandas.DataFrame()
        for field in fields:
            if isinstance(tmp[field].values[0],dict):
                try:
                    field_df = pandas.concat([pandas.DataFrame.from_dict(item, orient='index').T for item in tmp[field]])
                    field_df.index = range(0,field_df.shape[0])
                    field_df.columns = ["%s_%s" %(field,x) for x in field_df.columns.tolist()]
                    self.data = pandas.concat([self.data,field_df],axis=1)
                except:
                    self.data[field] = tmp[field]                   
            else:
                 self.data[field] = tmp[field]                   
                            
    def clean_results(self,filters=None):
        '''clean_results separates incomplete experiments, surveys, and games, and formats data
        :param filters: a dictionary of filter criteria, with key as field name, value as a dictionary
                        with "operator", "value", and "drop" (boolean) to determine filters. See
                        results.get_filters() to see an example
        '''
        if filters == None:
            filters = self.filters
 
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
       
    
    def filter(self,field,value,sort_by=None,ascending=False):
        '''filter filters results based on a field of interest
        :param field: the field (column) name to filter
        :param value: the value to filter for
        :param sort_by: a list of fields to sort by, default is datetime
        :param ascending: direction of the sort (default False)
        '''
        if isinstance(self.data,pandas.DataFrame):

            if field in self.data.columns:
                # Default sorting is by finishing time
                if sort_by == None and "finishtime" in self.data.columns:
                    sort_by = ["finishtime"]
                else:
                    sort_by = [x for x in sort_by if x in self.data.columns]    
                data_sorted = self.data.sort_values(by=sort_by,ascending=ascending)

                return data_sorted[data_sorted[field] == value]
            else:
                print "Field %s is not present in the data columns. Choice are %s" %(field,",".join(self.data.columns))
        else:
            print "ERROR: No results found to filter."
       
         
    def export(self,file_name):
        """export saves raw results data to json 
        :param file_name: the json file to save to
        """
        file_name,ext = os.path.splitext(file_name)
        if ext.lower() == ".json":
            save_json(self.json,file_name)
        else:
            print "File extension to save raw results must be .json" 


    def extract_experiment(self,exp_id, fields = None):
        '''Extract the data column of the results object for a specified experiment.
        :param exp_id: the exp_id to extract
        :param fields: list of (top level) fields to add to experiment dataframe
        '''
        if isinstance(self.data,pandas.DataFrame):
            experiment = pandas.DataFrame()
            if exp_id in self.data["experiment_exp_id"].tolist():

                # Subset the data to the experiment of interest, give count
                subset = self.filter("experiment_exp_id",exp_id)
                subset.index = range(subset.shape[0])

                for row in subset.iterrows():
                    
                    data_results = row[1].data
                    result_id = row[0]

                    if not isinstance(data_results,list):
                        data_results = [data_results]
                        row_df = pandas.concat([pandas.DataFrame.from_dict(item, orient='index') for item in data_results])
                    else:
                        row_df = pandas.concat([pandas.DataFrame.from_dict(item, orient='index').T for item in data_results])
                    
                    has_dict = [x for x in row_df.columns if isinstance(row_df[x].tolist()[0],dict)]
                    while len(has_dict) != 0:
                        for fieldname in has_dict:
                            append_df = pandas.concat([pandas.DataFrame.from_dict(item, orient='index').T for item in row_df[fieldname]])
                            append_df = append_df.drop(fieldname,axis=1,errors="ignore")
                            row_df = pandas.concat([row_df,append_df],axis=1)
                            row_df = row_df.drop(fieldname,axis=1)
                        has_dict = [x for x in row_df.columns if isinstance(row_df[x].tolist()[0],dict)]
                    
                    # Add additional fields to dataframe
                    if fields:
                        if isinstance(fields,str):
                            fields = [fields]
                        for field in fields:
                            row_df[field] = row[1][field]
                    # Add the result to the experiment
                    row_df.index = ["%s_%s_%s" %(exp_id,result_id,x) for x in range(row_df.shape[0])]                    
                    experiment = experiment.append(row_df)
  
                return experiment

            # The user has selected an experiment not present in the results
            else:
                experiment_choices = numpy.unique(self.data["experiment_exp_id"]).tolist()
                print "Experiment %s not present in the results. Choice are %s" %(exp_id,",".join(experiment_choices))
        else:
            print "ERROR: No results found to filter."


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
    
