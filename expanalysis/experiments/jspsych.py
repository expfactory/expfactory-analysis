'''
analysis/results.py: part of expfactory package
jspsych functions

'''
from expanalysis.results import select_worker, extract_experiment
from expanalysis.utils import check_template, get_data, lookup_word
import numpy

def calc_time_taken(results):
    '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
    '''
    results = results.get_results()
    instruction_lengths = []
    exp_lengths = []
    for i,row in results.iterrows():
        if check_template(row) == 'jspsych':
            data = get_data(row)
            #ensure there is a time elapsed variable
            assert 'time_elapsed' in data[-1].keys(), \
                '"time_elapsed" not found for at least one dataset in these results'
            #sum time taken on instruction trials
            instruction_length = numpy.sum([trial['time_elapsed'] for trial in data if lookup_word(trial.get('trial_id')) == 'instruction'])        
            #Set the length of the experiment to the time elapsed on the last 
            #jsPsych trial
            experiment_length = data[-1]['time_elapsed']
            instruction_lengths.append(instruction_length/1000.0)
            exp_lengths.append(experiment_length/1000.0)
        else:
            instruction_lengths.append(numpy.nan)
            exp_lengths.append(numpy.nan)
    results['total_time'] = exp_lengths
    results['instruct_time'] = instruction_lengths
    results['ontask_time'] = results['total_time'] - results['instruct_time']
        
def print_time(results, time_col = 'ontask_time'):
    '''Prints time taken for each experiment in minutes
    :param time_col: Dataframe column of time in seconds
    '''
    df = results.get_results()
    
    assert time_col in df, \
        '"%s" has not been calculated yet. Use calc_time_taken method' % (time_col)
    #drop rows where time can't be calculated
    df = df.dropna(subset = [time_col])
    time = (df.groupby('experiment')[time_col].mean()/60.0).round(2)
    print(time)
    return time

def get_average_variable(results, var):
    '''Prints time taken for each experiment in minutes
    '''
    averages = {}
    for exp in results.get_experiments():
        data = extract_experiment(results,exp)
        try:
            average = data[var].mean()
        except TypeError:
            print "Cannot average %s" % (var)
        averages[exp] = average
    return averages
    
    
def get_post_task_responses(results):
    question_responses = {}
    for worker in results.get_workers():
        data = select_worker(results, worker)
        worker_responses = {}
        for i,row in data.iterrows():
            if check_template(row['data']) == 'jspsych':
                if 'responses' in row['data'][-2]['trialdata'].keys():
                    response = row['data'][-2]['trialdata']['responses']
                    worker_responses[row['experiment']] = response
                else:
                    worker_responses[row['experiment']] = ''
        question_responses[worker] = worker_responses
    return question_responses
    

    
    
    