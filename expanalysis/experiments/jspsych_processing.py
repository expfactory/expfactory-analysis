"""
analysis/experiments/jspsych_processing.py: part of expfactory package
functions for automatically cleaning and manipulating jspsych experiments
"""
import re
import pandas

def stop_signal_post(df):
    df['stopped'] = df['key_press'] == -1
    return df
    
def directed_forgetting_post(df):
    df['cue'] = df['cue'].fillna(df['stim'])
    df.drop('stim',axis = 1, inplace = True)
    df['stim_bottom'] = df['stim_bottom'].fillna(df['stim_bottom'].shift(3))
    df['stim_top'] = df['stim_top'].fillna(df['stim_bottom'].shift(3))
    df['cue'] = df['cue'].fillna(df['cue'].shift(2))
    return df
    
def keep_track_post(df):
    for i,row in df.iterrows():
        if not pandas.isnull(row['responses']):
            response = row['responses']
            response = response[response.find('":"')+3:-2]
            response = re.split(r'[,; ]+', response)
            response = [x.lower().strip() for x in response]
            df.set_value(i,'responses', response)
            if not pandas.isnull(row['correct_responses']):
                targets = row['correct_responses'].values()
                score = sum([word in targets for word in response])
                df.set_value(i, 'score', score)
                df.set_value(i, 'possible_score', len(targets))
    return df


def multi_worker_decorate(func):
    """Decorator to ensure that dv functions have only one worker
    """
    def multi_worker_wrap(group_df):
        group_dvs = {}
        for worker in pandas.unique(group_df['worker']):
            df = group_df.query('worker == "%s"' %worker)
            group_dvs[worker] = func(df)
        return group_dvs
    return multi_worker_wrap

@multi_worker_decorate
def calc_adaptive_n_back_DV(df):
    """ Calculate dv for adaptive_n_back task. Maximum load
    """
    df = df.query('exp_stage != "practice"')
    dvs = {'max_load': df['load'].max()}
    dvs['description'] = 'max load'
    return dvs

@multi_worker_decorate
def calc_choice_reaction_time_DV(df):
    df = df.query('exp_stage != "practice"')
    dvs = {}
    dvs['avg_rt'] = df['rt'].median()
    dvs['accuracy'] = df['correct'].mean()
    dvs['description'] = 'standard'  
    return dvs

@multi_worker_decorate
def calc_simple_reaction_time_DV(df):
    df = df.query('exp_stage != "practice"')
    dvs = {}
    dvs['avg_rt'] = df['rt'].median()
    dvs['description'] = 'average reaction time'  
    return dvs
    
@multi_worker_decorate
def calc_stroop_DV(df):
    """ Calculate dv for stroop task. Incongruent-Congruent, median RT and Percent Correct
    """
    df = df.query('exp_stage != "practice"')
    dvs = {}
    contrast_df = df.groupby('condition')[['rt','correct']].agg(['mean','median'])
    contrast = contrast_df.loc['incongruent']-contrast_df.loc['congruent']
    dvs['stroop_rt'] = contrast['rt','median']
    dvs['stroop_correct'] = contrast['correct', 'mean']
    dvs['avg_rt'] = df['rt'].median()
    dvs['accuracy'] = df['correct'].mean()
    dvs['description'] = 'incongruent-congruent'
    return dvs