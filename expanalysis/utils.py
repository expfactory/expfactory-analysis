"""

functions for working with experiment factory results

"""
import requests
import __init__
import pandas
import os


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

def clean_data(df, experiment = None, drop_columns = None, drop_na=True):
    '''clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows a different set of columns to be dropped
    :df: a pandas dataframe
    :param experiment: a string identifying the experiment used to automatically drop unnecessary columns. df should not have multiple experiments if this flag is set!
    :param drop_columns: a list of columns to drop. If not specified, a default list will be used from utils.get_dropped_columns()
    '''
    # Drop unnecessary columns
    if drop_columns == None:
        drop_columns = get_drop_columns()   
    df.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    if experiment != None:
        assert sum(df['experiment'] == experiment) == len(df), \
            "An experiment was specified, but the dataframe has other experiments!"      
        drop_rows = get_drop_rows(experiment)
    # Drop unnecessary rows, all null rows
    for key in drop_rows.keys():
        df = df.query('%s not in  %s' % (key, drop_rows[key]))
    if drop_na == True:
        df = df.dropna(how = 'all')
    #calculate correct responses if they haven't been calculated
    if set(['key_press', 'correct_response']).issubset(df.columns):
        if 'correct' in df.columns:
            print('Dataframe had a "Correct" column that has been overwritten!')
        df['correct'] = df['key_press'] == df['correct_response'] 
    #convert all boolean columns to integer
    for column in df.select_dtypes(include = ['bool']).columns:
        df[column] = df[column].astype('int')
    return df


def get_drop_columns():
    return ['view_history', 'stimulus', 'trial_index', 'internal_node_id', 
           'stim_duration', 'block_duration', 'feedback_duration','timing_post_trial']
           
def get_drop_rows(experiment):
    '''Function used by clean_df to drop rows from dataframes with one experiment
    :experiment: experiment key used to look up which rows to drop from a dataframe
    '''
    gen_cols = ['welcome', 'instruction', 'instruction', 'attention_check','end', 'post task questions'] #generic_columns to drop
    lookup = {'adaptive_n_back': {'trial_id': gen_cols + []},
                'angling_risk_task_always_sunny': {'trial_id': gen_cols + []}, 
                'attention_network_task': {'trial_id': gen_cols + []}, 
                'bickel_titrator': {'trial_id': gen_cols + []}, 
                'choice_reaction_time': {'trial_id': gen_cols + ['practice_intro', 'reset_trial']}, 
                'columbia_card_task_cold': {'trial_id': gen_cols + []}, 
                'columbia_card_task_hot': {'trial_id': gen_cols + []}, 
                'dietary_decision': {'trial_id': gen_cols + []}, 
                'digit_span': {'trial_id': gen_cols + []},
                'directed_forgetting': {'trial_id': gen_cols + []},
                'dot_pattern_expectancy': {'trial_id': gen_cols + []},
                'go_nogo': {'trial_id': gen_cols + []},
                'hierarchical_rule': {'trial_id': gen_cols + []},
                'information_sampling_task': {'trial_id': gen_cols + []},
                'keep_track': {'trial_id': gen_cols + []},
                'kirby': {'trial_id': gen_cols + []},
                'local_global_letter': {'trial_id': gen_cols + []},
                'motor_selective_stop_signal': {'trial_id': gen_cols + []},
                'probabilistic_selection': {'trial_id': gen_cols + []},
                'psychological_refractory_period_two_choices': {'trial_id': gen_cols + []},
                'recent_probes': {'trial_id': gen_cols + []},
                'shift_task': {'trial_id': gen_cols + []},
                'simple_reaction_time': {'trial_id': gen_cols + ['practice_intro','reset_tria','test_intro']},
                'spatial_span': {'trial_id': gen_cols + []},
                'stroop': {'trial_id': gen_cols + ['fixation', 'practice_intro', 'test_intro', ]}, 
                'simon':{'trial_id': gen_cols + ['reset_trial', 'test_intro']}, 
                'threebytwo': {'trial_id': gen_cols + []},
                'tower_of_london': {'trial_id': gen_cols + []},
                'two_stage_decision': {'trial_id': gen_cols + ['practice_intro', 'test_intro', 'wait']},
                'willingness_to_wait': {'trial_id': gen_cols + []},
                'writing_task': {}}    
                
    try:
        return lookup[experiment]
    except KeyError:
        print "Automatic lookup of drop rows failed: experiment not found in lookup table."
        return {}
       
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
        return data.values()
    elif check_template(row) == 'unknown':
        print "Couldn't determine data template"
        
    
    
    


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