'''
analysis/stats.py: part of expfactory package
stats functions

'''
from expanalysis.maths import check_numeric
from patsy import ModelDesc
import statsmodels.api as sm
import statsmodels.formula.api as smf
import scipy.stats as stats
import seaborn as sns
import pandas


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
            print("Found %s independent variables: %s" %(len(ind_labels),",".join(ind_labels.tolist())))
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
    def parse(formula):
        parse = ModelDesc.from_formula(formula)
        dep_vars = [term.name() for term in parse.lhs_termlist]
        ind_vars = [term.name() for term in parse.rhs_termlist]
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