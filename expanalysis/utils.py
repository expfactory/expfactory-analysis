"""

functions for working with experiment factory results

"""
import requests
import __init__
import pandas
import numpy
import os
import unicodedata

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

def clean_data(df, experiment = None, drop_columns = None, drop_na=True, lookup = True, replace_correct = True):
    '''clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows a different set of columns to be dropped
    :df: a pandas dataframe
    :param experiment: a string identifying the experiment used to automatically drop unnecessary columns. df should not have multiple experiments if this flag is set!
    :param drop_columns: a list of columns to drop. If not specified, a default list will be used from utils.get_dropped_columns()
    :param lookup: bool, default true. If True replaces all values in dataframe using the lookup_val function
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
    if lookup == True:
        #convert vals based on lookup
        for col in df.columns:
            df[col] = df[col].map(lookup_val)
    #calculate correct responses if they haven't been calculated
    if 'correct_response' in df.columns and replace_correct == True:
        if 'correct' in df.columns:
            print 'Replacing a "correct" column!'
        response_cols = list(set(['key_press','clicked_on']).intersection(df.columns))
        df['correct'] =  [float(trial['correct_response'] in list(trial[response_cols])) if not pandas.isnull(trial['correct_response']) else numpy.nan for i, trial in df.iterrows()]
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
    gen_cols = ['welcome', 'text','instruction', 'attention_check','end', 'post task questions', 'fixation'] #generic_columns to drop
    lookup = {'adaptive_n_back': {'trial_id': gen_cols + ['update_target', 'update_delay', 'delay_text']},
                'angling_risk_task_always_sunny': {'trial_id': gen_cols + ['test_intro','intro','ask_fish','set_fish']}, 
                'attention_network_task': {'trial_id': gen_cols + ['spatialcue', 'centercue', 'doublecue', 'nocue', 'restblock']}, 
                'bickel_titrator': {'trial_id': gen_cols + ['update_delay', 'update_mag', 'gap']}, 
                'choice_reaction_time': {'trial_id': gen_cols + ['practice_intro', 'reset trial']}, 
                'columbia_card_task_cold': {'trial_id': gen_cols + ['calculate_reward','reward','end_instructions']}, 
                'columbia_card_task_hot': {'trial_id': gen_cols + ['calculate_reward', 'reward', 'test_intro']}, 
                'dietary_decision': {'trial_id': gen_cols + ['start_taste', 'start_health']}, 
                'digit_span': {'trial_id': gen_cols + ['test_intro', 'start_reverse']},
                'directed_forgetting': {'trial_id': gen_cols + ['ITI_fixation', 'intro_test', 'test_intro']},
                'dot_pattern_expectancy': {'trial_id': gen_cols + ['rest', 'cue', 'feedback']},
                'go_nogo': {'trial_id': gen_cols + ['reset_trial','test_block','test_intro']},
                'hierarchical_rule': {'trial_id': gen_cols + ['feedback', 'test_intro']},
                'information_sampling_task': {'trial_id': gen_cols + ['test_intro', 'DW_intro', 'reset_round']},
                'keep_track': {'trial_id': gen_cols + []},
                'kirby': {'trial_id': gen_cols + []},
                'local_global_letter': {'trial_id': gen_cols + ['practice_intro', 'test_intro']},
                'motor_selective_stop_signal': {'trial_id': gen_cols + ['prompt_fixation']},
                'probabilistic_selection': {'trial_id': gen_cols + []},
                'psychological_refractory_period_two_choices': {'trial_id': gen_cols + []},
                'recent_probes': {'trial_id': gen_cols + ['intro_test', 'test_intro', 'iti_fixation']},
                'shift_task': {'trial_id': gen_cols + []},
                'simple_reaction_time': {'trial_id': gen_cols + ['practice_intro','reset_trial','test_intro']},
                'spatial_span': {'trial_id': gen_cols + ['test_intro', 'start_reverse_intro']},
                'stim_selective_stop_signal': {'trial_id': gen_cols + []},
                'stop_signal': {'trial_id': gen_cols + ['reset']},
                'stroop': {'trial_id': gen_cols + ['practice_intro', 'test_intro', ]}, 
                'simon':{'trial_id': gen_cols + ['reset_trial', 'test_intro']}, 
                'threebytwo': {'trial_id': gen_cols + ['cue','practice_intro', 'gap', 'test_intro', 'set_stims']},
                'tower_of_london': {'trial_id': gen_cols + []},
                'two_stage_decision': {'trial_id': gen_cols + ['practice_intro', 'test_intro', 'wait']},
                'willingness_to_wait': {'trial_id': gen_cols + ['practice_intro', 'test_intro']},
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
        
    
def lookup_val(val):
    """function that modifies a string so that it conforms to expfactory analysis by 
    replacing it with an interpretable synonym
    :val: val to lookup
    """
    if isinstance(val,(str,unicode)):
        #convert unicode to str
        if isinstance(val, unicode):
            val = unicodedata.normalize('NFKD', val).encode('ascii', 'ignore')
        val = val.strip().lower()
        val = val.replace(" ", "_")
        #define synonyms
        lookup = {
        'reaction time': 'rt',
        'instructions': 'instruction',
        'correct': 1,
        'incorrect': 0}
        return lookup.get(val,val)
    else:
        return val
     
    


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