'''
expanalysis/stats.py: part of expfactory package
stats functions
'''
from expanalysis.maths import check_numeric
from expanalysis.plots import plot_groups
from expanalysis.processing import extract_experiment, extract_row, get_DV
from patsy import ModelDesc
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as stats
import seaborn as sns
from matplotlib import pyplot as plt
import pandas
import numpy
import hddm

def results_check(results, experiment = None, worker = None, columns = ['correct', 'rt'], remove_practice = True, use_groups = True,  plot = False, silent = False):
    """Outputs info for a basic data check on the results object. Uses data_check to group, describe and plot
    dataframes. Function first filters the results object as specified,
    loops through each experiment and worker contained in the results object, performs some basic dataframe manipulation
    and runs data_check
    :df:
    :param experiment: a string or array of strings to select the experiment(s) before calculating basic stats
    :param worker: a string or array of strings to select the worker(s) before calculating basic stats
    :param columns: array of columns to subset summary statistics, if they exist
    :param remove_practice: bool, default True. If True will remove any rows labeled "practice" in the "exp_stage" column, if it exists
    :param use_groups: bool, default True. If True will lookup grouping variables using get_groupby for the experiment
    :param silent: bool, default False. If True will not print output
    :param plot: bool, default False: If True plots data using plot_groups
    :return summary, p: summary data frame and plot object
    """
    print '******************************************************************************'
    print 'Input: Type "exit" to end, "skip" to skip to the next experiment, or hit enter to continue'
    print '******************************************************************************'
    stats = {}
    filters = results.get_filters(silent = True)
    results.filter(experiment = experiment, worker = worker)
    for experiment in results.get_experiments():
        stats[experiment] = {}
        if not silent or plot:
            print '******************************************************************************'
            print '    Experiment: ',  experiment
            print '******************************************************************************'
        if use_groups:
            groupby = get_groupby(experiment)
        else:
            groupby = []
        experiment_df = extract_experiment(results, experiment)
        for worker in pandas.unique(experiment_df['worker']):
            if not silent or plot:
                print '******************************************************************************'
                print '    Worker: ',  worker
                print '******************************************************************************'
            df = experiment_df.query('worker == "%s"' % worker)
            summary, p = data_check(df, columns, remove_practice, groupby, silent, plot)
            #add summary and plot to dictionary of summaries
            stats[experiment]= {worker: {'summary': summary, 'plot': p}}
            if not silent or plot:
                input_text = raw_input("Press Enter to continue...")
                plt.close()
                if input_text in ['skip', 'exit']:
                    break
        if input_text == 'exit': 
            break
    results.filter(reset = True, **filters) 
    return stats

def data_check(df, columns = [], remove_practice = True, groupby = [], silent = False, plot = False):
    """Outputs info for a basic data check on one experiment. Functionality to group, describe and plot
    dataframes
    :df:
    :param columns: array of columns to subset summary statistics, if they exist
    :param remove_practice: bool, default True. If True will remove any rows labeled "practice" in the "exp_stage" column, if it exists
    :param groupby: list of columns in df to groupby using pandas .groupby function
    :param silent: bool, default False. If True will not print output
    :param plot: bool, default False: If True plots data using plot_groups
    :return summary, p: summary data frame and plot object
    """
    assert len(pandas.unique(df['experiment'])) == 1, \
        "More than one experiment found"
    generic_drop_cols = ['correct_response', 'question_num', 'focus_shifts', 'full_screen', 'stim_id', 'trial_id', 'index', 'trial_num', 'responses', 'key_press', 'time_elapsed']
    df.replace(-1, numpy.nan, inplace = True)
    
    if remove_practice and 'exp_stage' in df.columns:
        df = df.query('exp_stage != "practice"')
        
    if not set(columns).issubset(df.columns) or len(columns) == 0:
        print "Columns selected were not found for %s. Printing generic info" % df['experiment'].iloc[0]
        keep_cols = df.columns
    else:
        keep_cols = groupby + columns
    df = df[keep_cols]
    drop_cols = [col for col in generic_drop_cols if col in df.columns]
    df = df.drop(drop_cols, axis = 1)
        
    #group summary if groupby variables exist
    if len(groupby) != 0:
        summary = df.groupby(groupby).describe()
        summary.reset_index(inplace = True)
        #reorder columns
        stats_level = 'level_%s' % len(groupby)
        summary.insert(0, 'Stats', summary[stats_level])
        summary.drop(stats_level, axis = 1, inplace = True)
        summary = summary.query("Stats in ['mean','std','min','max','50%']")
    else:
        summary = df.describe()
        summary.insert(0, 'Stats', summary.index)
    if plot:
        p = plot_groups(df, groupby)
    else:
        p = numpy.nan
    if not silent:
        print(summary)
        print('\n')
    return summary, p
    
def get_groupby(experiment):
    '''Function used by basic_stats to group data ouptut
    :experiment: experiment key used to look up appropriate grouping variables
    '''
    lookup = {'adaptive_n_back': ['load'],
                'angling_risk_task_always_sunny': [], 
                'attention_network_task': ['flanker_type', 'cue'], 
                'bickel_titrator': [], 
                'choice_reaction_time': [], 
                'columbia_card_task_cold': [], 
                'columbia_card_task_hot': [], 
                'dietary_decision': [], 
                'digit_span': ['condition'],
                'directed_forgetting': [],
                'dot_pattern_expectancy': [],
                'go_nogo': [],
                'hierarchical_rule': [],
                'information_sampling_task': [],
                'keep_track': [],
                'kirby': [],
                'local_global_letter': [],
                'motor_selective_stop_signal': ['SS_trial_type'],
                'probabilistic_selection': [],
                'psychological_refractory_period_two_choices': [],
                'recent_probes': [],
                'shift_task': [],
                'simple_reaction_time': [],
                'spatial_span': ['condition'],
                'stim_selective_stop_signal': ['condition'],
                'stop_signal': ['condition', 'SS_trial_type'],
                'stroop': ['condition'], 
                'simon':['condition'], 
                'threebytwo': ['task_switch', 'cue_switch'],
                'tower_of_london': [],
                'two_stage_decision': [],
                'willingness_to_wait': [],
                'writing_task': []} 
                
    try:
        return lookup[experiment]
    except KeyError:
        print "Automatic lookup of groups failed: %s not found in lookup table." % experiment
        return []


def calc_DVs(results):
    """Calculate DVs for each experiment
    :results: results object
    """
    results = results.get_results()
    DVs = []
    for i, row in results.iterrows():
        df = extract_row(row)
        DVs.append(get_DV(df, row['experiment']))
    results['DVs'] = DVs
    
def EZ_diffusion(df):
    assert 'correct' in df.columns, 'Could not calculate EZ DDM'
    pc = df['correct'].mean()
    vrt = numpy.var(df.query('correct == True')['rt'])
    mrt = numpy.mean(df.query('correct == True')['rt'])
    drift, thresh, non_dec = hddm.utils.EZ(pc, vrt, mrt)
    return {'drift': drift, 'thresh': thresh, 'non_decision': non_dec}
    

def run_DDM(results, EZ = True):
    experiment_DDM = {}
    if EZ:
        for experiment in results.get_experiments():
            df = extract_experiment(results, experiment)
            if 'correct' in df.columns:
                experiment_DDM[experiment] = EZ_diffusion(df)
            else:
                print 'Could not calculate EZ DDM for %s. No "correct" column.' % (experiment)
    return experiment_DDM
    
        

def compute_contrast(df, dep_var, ind_var, drop_rows = {}, plot=True):
    '''compute_contrast calculates a contrast (either pearson correlation for numeric or ttest for not) between two variables in the data frame
    :param dep_var: dependent variable, must be column in data frame
    :param ind_var: independent variable, must be column in data frame
    :param plot: boolean to return plot object in result (default True)
    :param drop_rows: a dictionary of columns/value pairs used to drop rows. Drops rows where the row value for the column equals the value specified.
    :return results: dict that includes t statistic or correlation, prob (two tailed p value), and plot
    '''
    
    assert isinstance(drop_rows, dict), 'drop_rows must be a dictionary'
    results = dict()
    if set([dep_var, ind_var]).issubset(df.columns):
        df.dropna(subset = [ind_var, dep_var], inplace = True)
         # Drop unnecessary rows, all null rows
        for key in drop_rows.keys():
            exclude = drop_rows[key]
            if isinstance(exclude, list):
                df = df.query('%s not in  %s' % (key, exclude))
            else:
                df = df.query('%s !=  %s' % (key, exclude))
        ind_vec = df[ind_var]
        dep_vec = df[dep_var]
        if (check_numeric(ind_vec) and check_numeric(dep_vec)):
            corr,pval = stats.stats.pearsonr(ind_vec,dep_vec) # most results can be computed with regression. These are stand ins
            results["corr"] = corr
            results["pval"] = pval 
            if plot == True:
                results["plot"] = sns.jointplot(ind_var,dep_var, data = df)
        else:
            ind_labels = pandas.unique(ind_vec)
            print("Found %s independent variables: %s" %(len(ind_labels),", ".join([str(label) for label in ind_labels])))
            if (len(ind_labels) == 2):
                vals1 = df[ind_vec == ind_labels[0]][dep_var]
                vals2 = df[ind_vec == ind_labels[1]][dep_var]
                tstat, pval = stats.ttest_ind(vals1,vals2) 
                results["tstat"] = tstat.tolist()
                results["pval_two_tailed"] = pval
                if plot == True:
                    results["plot"] = sns.boxplot(data = df, x = ind_var, y = dep_var)
        return results
    else:
        missing = [x for x in [dep_var,ind_var] if x not in df.columns]
        print "'%s' missing from data frame columns." %(",".join(missing))
    

def compute_regression(df, formula, drop_rows = {}):
    '''Computes appropriate regression using statsmodels. If the dependent variable is numeric,
    computes multiple regression. If it is categorical, computes logistic regression.
    :param formula: R-style formula to pass to statsmodels. see: http://statsmodels.sourceforge.net/0.6.0/examples/notebooks/generated/formulas.html
    :param drop_rows: a dictionary of columns/value pairs used to drop rows. Drops rows where the row value for the column equals the value specified.
    '''
    def extract_var(var):
        if (var.find("(") + var.find("(")) != -2:
            return var[var.find("(") + 1:var.find(")")]
        return var
    def parse(formula):
        parse = ModelDesc.from_formula(formula)
        dep_vars = [extract_var(term.name()) for term in parse.lhs_termlist]
        ind_vars = [extract_var(term.name()) for term in parse.rhs_termlist]
        assert len(dep_vars) == 1, "Only one dependent variable allowed"
        if 'Intercept' in ind_vars:
            ind_vars.remove('Intercept')
        for item in ind_vars:
            if ":" in item:
                ind_vars.remove(item)
        return (dep_vars[0], ind_vars)
    
    assert isinstance(drop_rows, dict), 'drop_rows must be a dictionary'
    dep_var, ind_vars = parse(formula)
    var_list = [dep_var] + ind_vars
    if set(var_list).issubset(df.columns):
        df.dropna(subset = var_list, inplace = True)
        for key in drop_rows.keys():
            exclude = drop_rows[key]
            if isinstance(exclude, list):
                df = df.query('%s not in  %s' % (key, exclude))
            else:
                df = df.query('%s !=  %s' % (key, exclude))
        dep_vec = df[dep_var]
        if check_numeric(dep_vec):
            fit = smf.ols(formula, df).fit()
        else:
            fit = smf.glm(formula, df, family = sm.families.Binomial()).fit()
        print fit.summary()
    else:
        missing = [x for x in var_list if x not in df.columns]
        print "'%s' missing from data frame columns." %(",".join(missing))