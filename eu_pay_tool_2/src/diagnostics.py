
#Regression Diagnostics Module

#Provides statistical diagnostic tools for evaluating the quality 
# and validity of the fitted regression model.

#Includes:
#   - Model fit statistics
#   - Confidence intervals
#   - Heteroscedasticity testing (Breusch–Pagan)
#   - Multicollinearity testing (VIF)

import pandas as pd
import statsmodels.stats.api as sms
from statsmodels.stats.outliers_influence import variance_inflation_factor

class Diagnostics:
    
    #Provides statistical diagnostics for regression results.
    #Parameters
        #regression_engine : RegressionEngine
        #An instance of RegressionEngine after calling '.fit()'.
        #The engine must contain a fitted statsmodels OLS result object.

    def __init__(self, regression_engine):
        self.engine = regression_engine
        self.results = regression_engine.model

    # Model Fit Statistics
    def summary_stats(self):
        
        #Returns core regression performance statistics.
        return {
            "R_squared": self.results.rsquared,
            "Adj_R_squared": self.results.rsquared_adj,
            "F_statistic": self.results.fvalue,
            "Model_p_value": self.results.f_pvalue,
            "Observations": int(self.results.nobs),
        }

    # Confidence Intervals
    def confidence_intervals(self):
        #Returns 95% confidence intervals for all regression coefficients.
        return self.results.conf_int()

    # Heteroscedasticity Test
    def breusch_pagan_test(self):
        
        #Performs Breusch–Pagan test for heteroscedasticity.

        #Null Hypothesis:
        #    Homoscedasticity (constant variance of residuals)

        #If p-value < 0.05:
        #   Evidence of heteroscedasticity.
        
        test = sms.het_breuschpagan(
            self.results.resid,
            self.results.model.exog
        )

        labels = [
            "Lagrange multiplier statistic",
            "p-value",
            "f-value",
            "f p-value"
        ]

        return dict(zip(labels, test))

    # Multicollinearity Test
    def calculate_vif(self):
        
        #Computes Variance Inflation Factor (VIF) for each regressor.

        #Interpretation:
        #    VIF = 1        → No multicollinearity
        #    VIF > 5         → Moderate concern
        #    VIF > 10       → Serious multicollinearity problem
        
        X = self.results.model.exog
        vif_data = pd.DataFrame()
        vif_data["VIF"] = [
            variance_inflation_factor(X, i)
            for i in range(X.shape[1])
        ]
        vif_data["variable"] = self.results.model.exog_names
        return vif_data
    
    