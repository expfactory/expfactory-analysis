# -*- coding: utf-8 -*-
"""
Calculate a t-statistic to compare the stroop "condition" variable (independent variable)
to the "reaction time" (dependent variable)

"""
from expfactory.analysis.utils import load_result, clean_df
from expfactory.analysis.maths import check_numeric
from expfactory.analysis.stats import compute_contrast
import matplotlib.pylab as plt

# load data frame, clean out unnecessary fields
df = load_result('stroop_results.csv')
df = clean_df(df)

# List of dependent and independent variables to test
result = compute_contrast(df,ind_var="condition",dep_var="rt")
plt.show(result["plot"])
