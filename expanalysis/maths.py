'''
expanalysis/maths.py: part of expanalysis package
math functions

'''

import numpy

def check_numeric(vector):
    '''check_numeric checks to see if all entries in a vector are numeric
    :param vector: the vector to check
    '''
    if isinstance(vector,list):
        vector = numpy.array(vector)
    if (vector.dtype == numpy.float64 or vector.dtype == numpy.int64):
        return True
    else:
        return False
