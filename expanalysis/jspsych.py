'''
analysis/results.py: part of expfactory package
jspsych functions

'''
from results import select_worker, extract_experiment

def calc_time_taken(results):
    '''Selects a worker (or workers) from results object and sorts based on experiment and time of experiment completion
    '''
    data = results.get_results()
    exp_lengths = []
    for i,row in data.iterrows():
        #ensure there is a time elapsed variable
        assert 'time_elapsed' in row['data'][-1]['trialdata'].keys(), \
            '"time_elapsed" not found for at least one dataset in these results'
        #Set the length of the experiment to the time elapsed on the last 
        #jsPsych trial
        exp_lengths.append(row['data'][-1]['trialdata']['time_elapsed']/1000.0)
    data['time_taken'] = exp_lengths
        
def print_time_taken(results):
    '''Prints time taken for each experiment in minutes
    '''
    assert 'time_taken' in results.get_results(), \
        '"time_taken" has not been calculated yet. Use calc_time_taken method'
    time_taken = (results.get_results().groupby('experiment')['time_taken'].mean()/60.0).round(2)
    print(time_taken)
    return time_taken

def get_average_variable(results, var):
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
            if 'responses' in row['data'][-2]['trialdata'].keys():
                response = row['data'][-2]['trialdata']['responses']
                worker_responses[row['experiment']] = response
        question_responses[worker] = worker_responses
    return question_responses