#!/usr/bin/python

"""
Test analysis functions
"""

from expanalysis.maths import check_numeric
from expanalysis.utils import get_installdir
from expanalysis.results import Result
import pandas
import tempfile
import unittest
import numpy
import shutil
import json
import os
import re

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.pwd = get_installdir()
        self.tmpdir = tempfile.mkdtemp()
        self.jsonfile = os.path.abspath("%s/tests/data/results/results.json" %self.pwd)
        self.result = Result()
        self.result.load_results(self.jsonfile)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_check_numeric(self):
        not_numeric = ["hello","goodbye"]
        numeric_float = [1.1,2.2,3.3]
        numeric_int = [1,2,3]
        not_numeric_mixed = ["hello",2,3.0]
        self.assertTrue(check_numeric(numeric_float))
        self.assertTrue(check_numeric(numeric_int))
        self.assertTrue(check_numeric(not_numeric)==False)
        self.assertTrue(check_numeric(not_numeric_mixed)==False)


    def test_filter(self):
        filtered = self.result.filter(field="experiment_exp_id",value="bridge_game")
        self.assertTrue(filtered.shape[0]==20)
        self.assertTrue(len(numpy.unique(filtered["experiment_exp_id"]))==1)

    def test_load(self):
        print "TESTING: load data"
        result = Result()
        data = result.load_results(self.jsonfile)
        self.assertTrue(isinstance(data,pandas.DataFrame))
        self.assertTrue(data.shape[0] == 44)
        self.assertTrue(data.shape[1] == 13)

    def test_experiment_extract(self):
        print "TESTING: experiment extraction"
        experiment = self.result.extract_experiment(exp_id="stroop")
        experiment_columns = [u'block_duration', u'condition', u'correct', u'correct_response',
       u'current_trial', u'dateTime', u'feedback_duration',
       u'internal_node_id', u'key_press', u'possible_responses', u'responses',
       u'rt', u'stim_color', u'stim_duration', u'stim_word', u'stimulus',
       u'time_elapsed', u'timing_post_trial', u'trial_id', u'trial_index',
       u'trial_type', u'trialdata', u'uniqueid', u'view_history']
        self.assertTrue(isinstance(experiment,pandas.DataFrame))
        self.assertTrue(experiment.shape[0]==747)
        [self.assertTrue(x) in experiment.columns for x in experiment_columns]


    def test_survey_extract(self):
        print "TESTING: survey extraction"
        survey = self.result.extract_experiment(exp_id="bis11_survey")
        self.assertTrue(isinstance(survey,pandas.DataFrame))


    def test_game_extract(self):
        print "TESTING: game extraction"
        game = self.result.extract_experiment(exp_id="bridge_game")
        game_columns = [u'current_trial', u'uniqueid', u'dateTime', u'ACC', u'RT', u'solution',
       u'problem_id', u'trial', u'finished', u'points', u'answer', u'n1',
       u'n2', u'problem']
        self.assertTrue(isinstance(game,pandas.DataFrame))
        self.assertTrue(game.shape[0]==301)
        [self.assertTrue(x) in game.columns for x in game_columns]



if __name__ == '__main__':
    unittest.main()
