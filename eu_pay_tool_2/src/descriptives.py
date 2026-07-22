
#Descriptive statistics module 

#EU Pay Transparency Directive Metrics

#This module calculates all descriptive metrics required under the EU Pay Transparency Directive.
#   - Mean and median gender pay gaps
#   - Hourly pay gaps
#   - Bonus gaps and participation rates
#   - Gender distribution across pay quartiles
#   - Workforce gender distribution

#These metrics form the unadjusted (raw) component of pay gap analysis.

import pandas as pd
import numpy as np

def unadjusted_pay_gap(df):

    #Compute the unadjusted (raw) gender pay gap using mean and median pay.

    #Formula:
    #   Gap (%) = (Male Pay − Female Pay) / Male Pay × 100

    #Returns:
    #    - summary_dict: Key headline statistics
    #   - gender_summary: Table of mean and median pay by gender

    gender_summary = df.groupby("gender")[
        "total_actual_total_pay_2024"
    ].agg(["mean", "median"])

    male_mean = gender_summary.loc["Male", "mean"]
    female_mean = gender_summary.loc["Female", "mean"]

    mean_gap = (male_mean - female_mean) / male_mean * 100

    male_median = gender_summary.loc["Male", "median"]
    female_median = gender_summary.loc["Female", "median"]

    median_gap = (male_median - female_median) / male_median * 100

    summary_dict = {
        "Mean Gender Pay Gap (%)": round(mean_gap, 2),
        "Median Gender Pay Gap (%)": round(median_gap, 2),
        "Workforce Size": len(df)
    }

    return summary_dict, gender_summary


def pay_quartiles(df: pd.DataFrame):
    
    #Calculate gender distribution across pay quartiles.
    
    #Employees are divided into four equally sized pay groups using
    #pandas qcut (quartile-based binning).

    #Returns:
    #    Cross-tabulated table showing proportion of men and women within each quartile.
    
    df["pay_quartile"] = pd.qcut(
        df["total_actual_total_pay_2024"],
        4,
        labels=["Q1", "Q2", "Q3", "Q4"]
    )

    quartile_table = pd.crosstab(
        df["pay_quartile"],
        df["gender"],
        normalize="index"
    )

    print("\nGender Distribution by Pay Quartile:")
    print(quartile_table)

    return quartile_table


class EUMetrics:
    
    #Calculates EU Pay Transparency Directive required metrics.

    #This class computes all mandatory gender pay reporting indicators,
    #structured for dashboard display and export.

    #It operates on a processed DataFrame and does not modify original source data.
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    @staticmethod
    def _gap(male_value, female_value):
        #Internal helper to compute gender pay gap percentage.
        #Standard formula: (Male − Female) / Male × 100
        return (male_value - female_value) / male_value * 100

    def mean_median_pay_gap(self):
    #Calculate mean and median annual gender pay gaps.
        grouped = self.df.groupby("gender")[
            "total_actual_total_pay_2024"
        ].agg(["mean", "median"])

        mean_gap = self._gap(
            grouped.loc["Male", "mean"],
            grouped.loc["Female", "mean"]
        )

        median_gap = self._gap(
            grouped.loc["Male", "median"],
            grouped.loc["Female", "median"]
        )
        
        #Returns:
        #   - Mean gap (%)
        #   - Median gap (%)
        #   - Aggregated pay table by gender
        return round(mean_gap, 2), round(median_gap, 2), grouped

    # --------------------------------------------------

    def hourly_pay_gap(self):
        #Calculate mean and median hourly gender pay gaps.

        #Required for EU directive compliance where hourly reporting
        #is mandated in addition to annual pay reporting.

        grouped = self.df.groupby("gender")[
            "total_hourly_total_pay_2024"
        ].agg(["mean", "median"])

        mean_gap = self._gap(
            grouped.loc["Male", "mean"],
            grouped.loc["Female", "mean"]
        )

        median_gap = self._gap(
            grouped.loc["Male", "median"],
            grouped.loc["Female", "median"]
        )

        return round(mean_gap, 2), round(median_gap, 2), grouped

    # --------------------------------------------------

    def bonus_gap(self):
        #Calculate gender bonus gap and bonus participation rates.

        #Includes:
        #    - Mean bonus gap (%)
        #    - Bonus pay summary table
        #    - Bonus participation rate (% of employees receiving bonus)
        
        grouped = self.df.groupby("gender")[
            "actual_bonus_2024"
        ].agg(["mean", "median"])

        mean_gap = self._gap(
            grouped.loc["Male", "mean"],
            grouped.loc["Female", "mean"]
        )

        # Bonus participation
        participation = (
            self.df.assign(bonus_received=self.df["actual_bonus_2024"] > 0)
            .groupby("gender")["bonus_received"]
            .mean()
            * 100
        )

        return round(mean_gap, 2), grouped, participation.round(2)

    # --------------------------------------------------

    def pay_quartiles(self):
        #Calculate gender representation within pay quartiles.

        #Quartiles are determined using total annual pay distribution.
        #Output shows percentage gender composition per quartile.

        self.df["pay_quartile"] = pd.qcut(
            self.df["total_actual_total_pay_2024"],
            4,
            labels=["Q1 (Lowest)", "Q2", "Q3", "Q4 (Highest)"]
        )

        quartiles = pd.crosstab(
            self.df["pay_quartile"],
            self.df["gender"],
            normalize="index"
        ) * 100

        return quartiles.round(2)

    # --------------------------------------------------

    def workforce_distribution(self):
        #Calculate overall workforce gender composition (%).
        distribution = (
            self.df["gender"].value_counts(normalize=True) * 100
        )

        return distribution.round(2)

    # --------------------------------------------------

    def full_summary(self):
        #Generate a complete EU metrics package.

        #Returns a structured dictionary containing:
        #    - Headline summary statistics
        #    - Detailed pay tables
        #    - Quartile distribution
        #    - Bonus participation
        #    - Workforce composition

        #This method acts as the primary interface for dashboard display and reporting export.

        mean_gap, median_gap, pay_table = self.mean_median_pay_gap()
        hourly_mean, hourly_median, hourly_table = self.hourly_pay_gap()
        bonus_gap, bonus_table, bonus_participation = self.bonus_gap()
        quartiles = self.pay_quartiles()
        workforce = self.workforce_distribution()

        summary_dict = {
            "Mean Gender Pay Gap (%)": mean_gap,
            "Median Gender Pay Gap (%)": median_gap,
            "Mean Hourly Pay Gap (%)": hourly_mean,
            "Median Hourly Pay Gap (%)": hourly_median,
            "Mean Bonus Gap (%)": bonus_gap,
            "Workforce Size": len(self.df),
        }

        return {
            "summary": summary_dict,
            "annual_pay_table": pay_table,
            "hourly_pay_table": hourly_table,
            "bonus_table": bonus_table,
            "bonus_participation": bonus_participation,
            "quartiles": quartiles,
            "workforce_distribution": workforce,
        }
