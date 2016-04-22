"""
analysis/experiments/jspsych_processing.py: part of expfactory package
functions for automatically cleaning and manipulating jspsych experiments
"""

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