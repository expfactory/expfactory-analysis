"""
expanalysis.api: functions for retrieving experiment factory results

"""

from expanalysis.utils import get_pages

def get_results(url="http://www.expfactory.org/api/results",access_token=None):
    '''get_results is a wrapper for get_url, to first check that the user has provided an access token
    :param url: the expfactory/results/api url
    :param access_token: a token obtained at expfactory.org/token when the user is logged in
    '''
    if access_token != None:
        return get_pages(url=url,access_token=access_token)
    else:
        print "You must provide an access_token to authenticate to the API."
   
