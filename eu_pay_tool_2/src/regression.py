import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from typing import List

# This class implements a log-linear OLS regression framework for analyzing gender pay gaps

class RegressionEngine:
    
    #Runs log-linear multivariate regression for gender pay gap analysis.
    #Handles adjusted pay gap calculation, stepwise gap decomposition, 
    #and driver contribution computation.
    
    def __init__(self, df: pd.DataFrame, dependent: str = "log_total_pay", controls: List[str] = None):
        self.df = df.copy()
        self.dependent = dependent
        self.controls = controls or []
        self.model = None  # Full model after fit

    # Internal methods
    def _fit_model(self, variables: List[str]):
        
        #Fit OLS regression with specified variables.
        #Returns fitted model.
        
        formula = f"{self.dependent} ~ " + " + ".join(variables)
        return smf.ols(formula=formula, data=self.df).fit()

    # Public methods
    def fit(self):
        
        #Fit full model with all controls + gender_binary.
        #Stores fitted model in self.model.
        
        self.model = self._fit_model(["gender_binary"] + self.controls)
        return self.model

    def adjusted_gender_gap(self):
        
        #Returns adjusted gender pay gap (%) based on fitted log-linear regression.
        #Formula: 100 * (exp(beta_gender) - 1)
        
        if self.model is None:
            raise ValueError("Model not fitted yet.")
        beta = self.model.params["gender_binary"]
        return round((np.exp(beta) - 1) * 100, 2)

    def regression_summary_df(self):
        
        #Returns coefficients, std errors, and p-values as a DataFrame.
        
        if self.model is None:
            raise ValueError("Model not fitted yet.")
        return pd.DataFrame({
            "Coefficient": self.model.params,
            "Std Error": self.model.bse,
            "P-value": self.model.pvalues
        })

    def model_stats(self):
        
        #Returns key model statistics.
        
        if self.model is None:
            raise ValueError("Model not fitted yet.")
        return {
            "Adjusted Gender Pay Gap (%)": self.adjusted_gender_gap(),
            "R-squared": round(self.model.rsquared, 4),
            "Adjusted R-squared": round(self.model.rsquared_adj, 4),
            "F-statistic": round(self.model.fvalue, 2),
            "F-test p-value": round(self.model.f_pvalue, 6),
            "Observations": int(self.model.nobs),
            "Root MSE": round(np.sqrt(self.model.mse_resid), 4)
        }

    # Gap decomposition and driver contribution

    def driver_shares(self):
    
    #Compute each control variable's contribution to reducing the gender pay gap.
    #Based on stepwise regression movement.
    #Returns weights summing to 100%.
    #Does NOT call gap_decomposition().
    

        # Step 0: Unadjusted
        model = self._fit_model(["gender_binary"])
        beta = model.params["gender_binary"]
        prev_gap = (np.exp(beta) - 1) * 100

        raw_contribs = []

        # Stepwise addition of controls
        current_controls = []
        for control in self.controls:
            current_controls.append(control)
            model = self._fit_model(["gender_binary"] + current_controls)
            beta = model.params["gender_binary"]
            new_gap = (np.exp(beta) - 1) * 100

            change = abs(new_gap - prev_gap)
            raw_contribs.append(change)

            prev_gap = new_gap

        total = sum(raw_contribs)

        if total == 0:
            return {c: 0 for c in self.controls}

        weights = {
            control: round(change / total * 100, 2)
            for control, change in zip(self.controls, raw_contribs)
        }

        return weights


    def gap_decomposition(self):
    
    #Pure visual proportional decomposition.
    #Does NOT refit models.
    #Uses:
        #- unadjusted gap
        #- adjusted gap
        #- driver shares (must sum to 100)
    

        if self.model is None:
            self.fit()

        # Get actual unadjusted gap
        model_unadj = self._fit_model(["gender_binary"])
        beta_unadj = model_unadj.params["gender_binary"]
        unadjusted_gap = (np.exp(beta_unadj) - 1) * 100

        # Get actual adjusted gap
        adjusted_gap = self.adjusted_gender_gap()

        # Total movement
        total_change = adjusted_gap - unadjusted_gap

        # Get driver percentages (already correct)
        driver_weights = self.driver_shares()

        steps = [("Unadjusted", round(unadjusted_gap, 2))]
        current_gap = unadjusted_gap

        # Move proportionally
        for driver, pct in driver_weights.items():
            movement = total_change * (pct / 100)
            current_gap += movement
            steps.append((driver, round(current_gap, 2)))

        # Force exact landing
        steps.append(("Adjusted", round(adjusted_gap, 2)))

        return steps
    
