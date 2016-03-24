# -*- coding: utf-8 -*-
"""

functions for working with experiment factory results
from collections import OrderedDict

"""

import simplejson as json
import pandas
from collections import OrderedDict

file_path = 'results.json'

# Data Json (from file)
def read_json_file(file_path):
    f = read_text_file(file_path)
    return json.loads(f, object_pairs_hook=OrderedDict)

# Text (from file)
def read_text_file(file_path):
    f = open(file_path,'rb')
    tmp = f.readlines()
    f.close()
    return "\n".join(tmp)
    
# Convert json to pandas data frame
def get_df(myjson):
    try:
        df = pandas.DataFrame(myjson)
    except:
        df = []
    return df
    
# Data Json Object (from URL)
class ResultsJson:
  """DataJson: internal class for storing json, accessed by NeuroVault Object"""
  def __init__(self,file_path):
    self.json = read_json_file(file_path)
    self.pandas = get_df(self.json['results'])
    
  """Print json data fields"""
  def __str__(self):
    return "Result Includes:<pandas:data frame><json:dict><txt:str><url:str>"

    
tmp_data = read_json_file(file_path)['results'][3]['taskdata']

