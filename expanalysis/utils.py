"""
analysis/utils.py: part of expfactory package
functions for working with experiment factory results
"""

import requests
import __init__
import pandas
import os
import unicodedata
import re

def get_installdir():
    return os.path.dirname(os.path.abspath(__init__.__file__))

def get_pages(url="http://www.expfactory.org/api/results",access_token=None):
    '''get_url retrieves the data at the experiment factory results page. The user must provide authentication, and the function assumes paginated results.
    :param url: the url to retrieve, default is expfactory.org/api/results
    '''
    if access_token != None:
        headers = {"Authorization":"token %s" %(access_token)}
        
    results = []
    # Continue retrieving pages until there is no next page
    while url != None:
       print "Retrieving %s" %(url)
       r = get_url(url,headers=headers)
       if r.status_code == 200:
           data = r.json()
           results = results + data["results"]
           url = data["next"]
       else:       
           print "Error: %s" %(r.reason)
           if (r.reason) == 'UNAUTHORIZED':
               break
    print "Found %s results!" %(len(results))
    
    return results
     
    
def get_url(url,headers=None):
    '''get_url returns a url, with params embedded in the header
    :param url: the url to retrieve
    :param headers: a dictionary of {"headerName":"headervalue"}
    '''
    if headers != None:
        return requests.get(url,headers=headers)
    else:
        return requests.get(url)
 
def load_result(result):
    '''load_result returns a pandas data frame of a result variable, either a json data structure, a downloaded csv file from an individual experiment, or a tsv file exported from the expfactory-docker instance
    :param result: one of a csv (from jsPsych), tsv (from expfactory-docker) or json (from Jspsych)
    '''
    if isinstance(result,str):
        filey = os.path.abspath(result)
        file_name,ext = os.path.splitext(filey)

        if ext.lower() == ".csv":
            df = pandas.read_csv(result,sep=",")
        elif ext.lower() == ".tsv":
            df = pandas.read_csv(result,sep="\t")
        elif ext.lower() == ".json":
            df = pandas.read_json(result)
        else:
            print "File extension not recognized, must be .csv (JsPsych single experiment export) or tsv (expfactory-docker) export." 
    return df
    
def check_template(row):
    """Determines which template was used to create a data object
    :row: tone row of a results dataframe
    """
    try:
        data = row['data']
    except:
        print 'No data column found!'
    if isinstance(data,dict):
        return 'survey'
    elif isinstance(data,list):
        return 'jspsych'
    else:
        return 'unknown'

def get_data(row):
    """Data can be stored in different forms depending on the experiment template.
    This function returns the data in a standard form (a list of trials)
    :data: the content of one row of the data column in a results dataframe
    """
    def get_response_text(question):
        """Returns the response text that corresponds to the value recorded in a survey question
        :question: A dictionary corresponding to a survey question
        """
        val = question['response']
        if 'options' in question.keys() and val != 'on':
            options = question['options']
            print(options)
            text = [str(opt['text']) for opt in options if opt['value'] == val]
            if len(text) == 1: text = text[0]
        else:
            text = pandas.np.nan
        return text
    try:
        data = row['data']
    except:
        print 'No data column found!'
    if check_template(row) == 'jspsych':
        if len(data) == 1:
            return data[0]['trialdata']
        elif len(data) > 1:
           return  [trial['trialdata'] for trial in data]
        else:
            print "No data found"
    elif check_template(row) == 'survey':
        survey =  data.values()
        for i in survey:
            i['question_num'] = int(re.search(r'%s_([0-9]{1,2})*' % row['experiment'], i['id']).group(1))
            #i['response_text'] = get_response_text(i)
        survey = sorted(survey, key=lambda k: k['question_num'])
        return survey
    elif check_template(row) == 'unknown':
        print "Couldn't determine data template"
        
    
def lookup_val(val):
    """function that modifies a string so that it conforms to expfactory analysis by 
    replacing it with an interpretable synonym
    :val: val to lookup
    """
    if isinstance(val,(str,unicode)):
        #convert unicode to str
        if isinstance(val, unicode):
            val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
        lookup_val = val.strip().lower()
        lookup_val = val.replace(" ", "_")
        #define synonyms
        lookup = {
        'reaction time': 'rt',
        'instructions': 'instruction',
        'correct': 1,
        'incorrect': 0}
        return lookup.get(lookup_val,val)
    else:
        return val
    
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
    df.reset_index(inplace = True, drop = True)
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
    df.reset_index(inplace = True, drop = True)
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
    df.reset_index(inplace = True, drop = True)
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
    df.reset_index(inplace = True, drop = True)
    return df
    
def select_finishtime(results, finishtime, all_data = True):
     '''Get results after a finishtime 
    :results: a Results object
    :finishtime: a date string
    :param all_data: boolean, default True. If true, only select data where the entire dataset was collected afte rthe finishtime
    :return df: dataframe containing the appropriate result subset
    '''
     df = results.get_results()
     if all_data:
        passed_df = df.groupby('worker')['finishtime'].min() >= finishtime
        workers = list(passed_df[passed_df].index)
        df = select_worker(results, workers)
     else:
        df = df.query('finishtime >= "%s"' % finishtime) 
        df.reset_index(inplace = True, drop = True)
     return df
    