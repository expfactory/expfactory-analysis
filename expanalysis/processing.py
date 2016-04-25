"""
analysis/processing.py: part of expfactory package
functions for automatically cleaning and manipulating experiments
"""
from expanalysis.experiments.jspsych_processing import directed_forgetting_post, keep_track_post, stop_signal_post
from expanalysis.utils import get_data, lookup_val, select_experiment
import pandas
import numpy

def clean_data(df, experiment = None, drop_columns = None, drop_na=True, lookup = True, replace_correct = True):
    '''clean_df returns a pandas dataset after removing a set of default generic 
    columns. Optional variable drop_cols allows a different set of columns to be dropped
    :df: a pandas dataframe
    :param experiment: a string identifying the experiment used to automatically drop unnecessary columns. df should not have multiple experiments if this flag is set!
    :param drop_columns: a list of columns to drop. If not specified, a default list will be used from utils.get_dropped_columns()
    :param lookup: bool, default true. If True replaces all values in dataframe using the lookup_val function
    '''
    # apply post processing 
    df = apply_post(df, experiment)
    # Drop unnecessary columns
    if drop_columns == None:
        drop_columns = get_drop_columns()   
    df.drop(drop_columns, axis=1, inplace=True, errors='ignore')
    if experiment != None:
        assert sum(df['experiment'] == experiment) == len(df), \
            "An experiment was specified, but the dataframe has other experiments!"      
        drop_rows = get_drop_rows(experiment)
        # Drop unnecessary rows, all null rows
        for key in drop_rows.keys():
            df = df.query('%s not in  %s' % (key, drop_rows[key]))
    if drop_na == True:
        df = df.dropna(how = 'all')
    if lookup == True:
        #convert vals based on lookup
        for col in df.columns:
            df[col] = df[col].map(lookup_val)
    #calculate correct responses if they haven't been calculated
    if 'correct_response' in df.columns and replace_correct == True:
        if 'correct' in df.columns:
            print 'Replacing a "correct" column!'
        response_cols = list(set(['key_press','clicked_on']).intersection(df.columns))
        df['correct'] =  [float(trial['correct_response'] in list(trial[response_cols])) if not pandas.isnull(trial['correct_response']) else numpy.nan for i, trial in df.iterrows()]
    #convert all boolean columns to integer
    for column in df.select_dtypes(include = ['bool']).columns:
        df[column] = df[column].astype('int')
    return df


def get_drop_columns():
    return ['view_history', 'stimulus', 'trial_index', 'internal_node_id', 
           'stim_duration', 'block_duration', 'feedback_duration','timing_post_trial', 'exp_id']
           
def get_drop_rows(experiment):
    '''Function used by clean_df to drop rows from dataframes with one experiment
    :experiment: experiment key used to look up which rows to drop from a dataframe
    '''
    gen_cols = ['welcome', 'text','instruction', 'attention_check','end', 'post task questions', 'fixation', \
                'practice_intro', 'test_intro'] #generic_columns to drop
    lookup = {'adaptive_n_back': {'trial_id': gen_cols + ['update_target', 'update_delay', 'delay_text']},
                'angling_risk_task_always_sunny': {'trial_id': gen_cols + ['test_intro','intro','ask_fish','set_fish']}, 
                'attention_network_task': {'trial_id': gen_cols + ['spatialcue', 'centercue', 'doublecue', 'nocue', 'rest block', 'intro']}, 
                'bickel_titrator': {'trial_id': gen_cols + ['update_delay', 'update_mag', 'gap']}, 
                'choice_reaction_time': {'trial_id': gen_cols + ['practice_intro', 'reset trial']}, 
                'columbia_card_task_cold': {'trial_id': gen_cols + ['calculate_reward','reward','end_instructions']}, 
                'columbia_card_task_hot': {'trial_id': gen_cols + ['calculate_reward', 'reward', 'test_intro']}, 
                'dietary_decision': {'trial_id': gen_cols + ['start_taste', 'start_health']}, 
                'digit_span': {'trial_id': gen_cols + ['start_reverse', 'stim', 'feedback']},
                'directed_forgetting': {'trial_id': gen_cols + ['ITI_fixation', 'intro_test', 'stim', 'cue']},
                'dot_pattern_expectancy': {'trial_id': gen_cols + ['rest', 'cue', 'feedback']},
                'go_nogo': {'trial_id': gen_cols + ['reset_trial']},
                'hierarchical_rule': {'trial_id': gen_cols + ['feedback', 'test_intro']},
                'information_sampling_task': {'trial_id': gen_cols + ['DW_intro', 'reset_round']},
                'keep_track': {'trial_id': gen_cols + ['practice_end', 'stim']},
                'kirby': {'trial_id': gen_cols + ['prompt', 'wait']},
                'local_global_letter': {'trial_id': gen_cols + []},
                'motor_selective_stop_signal': {'trial_id': gen_cols + ['prompt_fixation', 'feedback']},
                'probabilistic_selection': {'trial_id': gen_cols + []},
                'psychological_refractory_period_two_choices': {'trial_id': gen_cols + []},
                'recent_probes': {'trial_id': gen_cols + ['intro_test', 'iti_fixation']},
                'shift_task': {'trial_id': gen_cols + []},
                'simple_reaction_time': {'trial_id': gen_cols + ['reset_trial']},
                'spatial_span': {'trial_id': gen_cols + ['start_reverse_intro', 'stim', 'feedback']},
                'stim_selective_stop_signal': {'trial_id': gen_cols + ['feedback']},
                'stop_signal': {'trial_id': gen_cols + ['reset', 'feedback']},
                'stroop': {'trial_id': gen_cols + []}, 
                'simon':{'trial_id': gen_cols + ['reset_trial']}, 
                'threebytwo': {'trial_id': gen_cols + ['cue', 'gap', 'set_stims']},
                'tower_of_london': {'trial_id': gen_cols + []},
                'two_stage_decision': {'trial_id': gen_cols + ['wait', 'first_stage_selected', 'second_stage_selected', 'wait_update_fb']},
                'willingness_to_wait': {'trial_id': gen_cols + []},
                'writing_task': {}}    
                
    try:
        return lookup[experiment]
    except KeyError:
        print "Automatic lookup of drop rows failed: %s not found in lookup table." % experiment
        return {}


def apply_post(df, experiment):
    '''Function used by clean_df to post-process dataframe
    :experiment: experiment key used to look up appropriate grouping variables
    '''
    lookup = {'directed_forgetting': directed_forgetting_post,
              'keep_track': keep_track_post,
                'motor_selective_stop_signal': stop_signal_post,
                'stim_selective_stop_signal': stop_signal_post,
                'stop_signal': stop_signal_post}         
    try:
        fun = lookup[experiment]
    except KeyError:
        print "No post processing function found for %s" % experiment
        fun = lambda df: df
    return fun(df)

def extract_experiment(results, experiment, clean = True, drop_columns = None, drop_na = True):
    '''Returns a dataframe that has expanded the data column of the results object for the specified experiment.
    Each row of this new dataframe is a data row for the specified experiment.
    :results: a Results object
    :experiment: a string identifying one experiment
    :param clean: boolean, if true call clean_df on the data
    :param drop_columns: list of columns to pass to clean_df
    :param drop_na: boolean to pass to clean_df
    :return df: dataframe containing the extracted experiment
    '''
    assert experiment in results.get_experiments(), "Experiment not found in results!"
    df = select_experiment(results, experiment)
    #ensure there is only one dataset for each battery/experiment/worker combination
    assert sum(df.groupby(['battery', 'experiment', 'worker']).size()>1)==0, \
        "More than one dataset found for at least one battery/experiment/worker combination"
    trial_list = []
    for i,row in df.iterrows():
        exp_data = get_data(row)
        for trial in exp_data:
            trial['battery'] = row['battery']
            trial['experiment'] = row['experiment']
            trial['worker'] = row['worker']
            trial['finishtime'] = row['finishtime']
        trial_list += exp_data
    df = pandas.DataFrame(trial_list)
    if clean == True:
        df = clean_data(df, experiment, drop_columns, drop_na)
    df.reset_index(inplace = True)
    return df
