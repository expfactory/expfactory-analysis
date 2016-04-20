'''
expanalysis/testing.py: part of expanalysis package
testing functions

'''

import pandas
import json

def validate_result(result,fields=None):
    '''validate_result validates a results pandas data frame, ensuring that it has the correct field names
    :param fields: the top level fields expected in the result object (json), or column names (pandas df)
    '''
    if not isinstance(result,pandas.DataFrame):
        result = pandas.DataFrame(result)

    if fields == None:
        fields = ["battery","experiment","worker"]

    for field in fields:
        if field not in result:
            raise ValidationError('"%s" column not found in results' %(field))

class ValidationError(Exception):
    pass

