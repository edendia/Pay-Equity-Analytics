#Data processing module

import numpy as np
from datetime import datetime
import pandas as pd

class DataProcessor:
    
    #Transforms raw HR data into regression-ready format.

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()  # avoid mutating original dataframe

    def encode_gender(self):
        
        #Create binary gender variable (Female = 1, Male = 0).
        
        self.df["gender_binary"] = self.df["gender"].map(
            {"Male": 0, "Female": 1}
        )
        return self

    def create_log_pay(self):
        
        #Create log of total annual pay.
        #Log-linear models assume the dependent variable is logged.
        
        self.df["log_total_pay"] = np.log(
            self.df["total_actual_total_pay_2024"]
        )
        return self

    def ensure_numeric(self):
        
        #Ensure key numeric columns are numeric.
        #Non-numeric entries are coerced to NaN.
        
        numeric_cols = [
            "total_actual_total_pay_2024",
            "actual_annual_hours_worked_2024"
        ]

        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

        return self

    def process(self):
        
        #Full processing pipeline.
        
        (
            self.ensure_numeric()
                .encode_gender()
                .create_log_pay()
        )

        return self.df

