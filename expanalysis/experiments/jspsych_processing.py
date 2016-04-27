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
    df = df.rename(columns={'stim': 'cue'})
    for i in range(2,len(df)):
        if df.loc[i,'trial_id'] == 'probe':
            df.set_value(i,'stim_bottom', df.loc[i-3,'stim_bottom'])
            df.set_value(i,'stim_top', df.loc[i-3,'stim_top'])
            df.set_value(i,'cue', df.loc[i-2,'cue'])
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


def one_worker_decorate(func):
    """Decorator to ensure that dv functions have only one worker
    """
    def one_worker_wrap(df):
        assert len(pandas.unique(df['worker'])) == 1, \
            'dataframe must only have one worker in it'
        return func(df)
    return one_worker_wrap
    
@one_worker_decorate  
def calc_stroop_DV(df):
    """ Calculate dv for stroop task. Incongruent-Congruent, median RT and Percent Correct
    """
    dvs = {}
    contrast_df = df.groupby('condition')[['rt','correct']].agg(['mean','median'])
    contrast = contrast_df.loc['incongruent']-contrast_df.loc['congruent']
    dvs['rt'] = contrast['rt','median']
    dvs['correct'] = contrast['correct', 'mean']
    dvs['description'] = 'incongruent-congruent'
    return dvs

@one_worker_decorate
def calc_adaptive_n_back_DV(df):
    """ Calculate dv for adaptive_n_back task. Maximum load
    """
    dvs = {'max_load': df['load'].max()}
    dvs['description'] = 'max load'
    return dvs

