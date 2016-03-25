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


def clean_df(df, drop_columns = None,drop_na=True):
    '''clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows a different set of columns to be dropped
    :df: a pandas dataframe, loaded via load_result
    :param drop_columns: a list of columns to drop. If not specified, a default list will be used from utils.get_dropped_columns()
    '''
    # Drop unnecessary columns
    if drop_columns == None:
        drop_columns = get_drop_columns()   
    df.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    drop_trial_ids = ['welcome', 'instruction', 'attention_check','end']
    # Drop unnecessary columns, all null rows
    df = df.query('trial_id not in  @drop_trial_ids')
    if drop_na == True:
        df = df.dropna()
    return df


def get_drop_columns():
    return ['view_history', 'stimulus', 'trial_index', 'internal_node_id', 
            'time_elapsed', 'exp_id', 'stim_duration', 'block_duration', 
            'feedback_duration','timing_post_trial']
