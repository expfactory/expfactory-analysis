"""

functions for working with experiment factory results

"""
import requests
import __init__
import pandas
import json
import os


def get_installdir():
    '''get_installdir returns the install directory of the package'''
    return os.path.dirname(os.path.abspath(__init__.__file__))


def save_json(json_obj,output_file):
    '''save_json saves a pretty json
    :json_obj: the dictionary to save as json
    :output_file: the output file to save to
    '''
    filey = open(output_file,'wb')
    filey.write(json.dumps(json_obj, sort_keys=True,indent=4, separators=(',', ': ')))
    filey.close()
    return output_file


def get_pages(url=None,access_token=None):
    '''get_url retrieves the data at the experiment factory results page. The user must provide authentication, and the function assumes paginated results.
    :param url: the url to retrieve, default is expfactory.org/api/results
    :param access_token: access token retrieved at expfactory.org/token
    '''
    if url == None:
        url = "http://www.expfactory.org/api/results"

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

